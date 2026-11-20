"""CI05 independent, offline, synthetic-only Draft/Receipt/Index writer.

NOT a production writer or public publisher. Runs only in a separately marked,
non-Git scratch directory; no GitHub API, tokens, network or private source.
A live Public input route must be designed and explicitly approved separately.
"""
from __future__ import annotations

from contextlib import contextmanager
import json
import os
from pathlib import Path
import stat
import uuid

from .validator import KIND, PublicInputHold, digest, encode_json, validate

MARKER = '.CI05_SYNTHETIC_SCRATCH_ONLY'
LOCK = '.CI05_SINGLE_WRITER_CLAIM'
FOLDER = 'ci05_synthetic_drafts'
SCHEMA = 'ci05-synthetic-archive-v1-not-for-publication'


class WriterHold(PublicInputHold):
    pass


def _check_path(root: Path) -> None:
    if not root.is_absolute() or not root.is_dir():
        raise WriterHold('ABSOLUTE_SCRATCH_ROOT_REQUIRED')
    for path in (root, *root.parents):
        if path.is_symlink():
            raise WriterHold('SYMLINK_ANCESTOR_DENIED')
    m = root / MARKER
    if m.is_symlink() or not m.is_file() or m.read_bytes() != (KIND + '\n').encode('ascii'):
        raise WriterHold('EXPLICIT_SYNTHETIC_MARKER_REQUIRED')
    if (root / '.git').exists() or (root / '.git').is_symlink():
        raise WriterHold('GIT_WORKTREE_DENIED')
    if (root / 'private_research').exists() or (root / 'public_research').exists():
        raise WriterHold('NON_SYNTHETIC_DATA_DIRECTORY_DENIED')


def _safe_read(p: Path) -> bytes:
    if p.is_symlink() or not p.is_file():
        raise WriterHold('MISSING_OR_SYMLINK_FILE')
    if p.stat().st_size > 100_000:
        raise WriterHold('OVERSIZED_WRITER_FILE')
    return p.read_bytes()


def _write_exclusive(path: Path, raw: bytes) -> None:
    if path.exists() or path.is_symlink():
        raise WriterHold('EXCLUSIVE_WRITE_ONLY')
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, 'O_NOFOLLOW', 0)
    fd = os.open(str(path), flags, 0o600)
    with os.fdopen(fd, 'wb') as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())


@contextmanager
def _lease(root: Path):
    claim = root / LOCK
    try:
        claim.mkdir(mode=0o700)
    except FileExistsError as exc:
        raise WriterHold('DUPLICATE_OR_STALE_WRITER_CLAIM_HOLD') from exc
    try:
        yield
    finally:
        claim.rmdir()


def _entries(root: Path) -> dict[str, tuple[str, bytes]]:
    base = root / FOLDER
    if not base.exists():
        return {}
    if base.is_symlink() or not base.is_dir():
        raise WriterHold('UNSAFE_DRAFT_FOLDER')
    out = {}
    for w in sorted(base.iterdir()):
        if w.name == '_index.txt':
            continue
        if w.is_symlink() or not w.is_dir() or not w.name.startswith('20'):
            raise WriterHold('UNREVIEWED_CHILD_PATH')
        names = sorted(v.name for v in w.iterdir())
        if len(names) != 2 or sum(name.endswith('.md') for name in names) != 1 or sum(name.endswith('.receipt.json') for name in names) != 1:
            raise WriterHold('PARTIAL_OR_UNKNOWN_ARCHIVE_FILES')
        md = next(w / n for n in names if n.endswith('.md'))
        rec = next(w / n for n in names if n.endswith('.receipt.json'))
        data = _safe_read(md)
        try:
            r = json.loads(_safe_read(rec))
        except (UnicodeError, ValueError) as exc:
            raise WriterHold('CORRUPT_RECEIPT') from exc
        if (type(r) is not dict or set(r) != {'schema', 'kind', 'week', 'date', 'markdown_sha256', 'sources_sha256', 'source_ids', 'published'}
                or r['schema'] != SCHEMA or r['kind'] != KIND or r['published'] is not False
                or r['week'] != w.name or r['markdown_sha256'] != digest(data)
                or md.name != str(r['date']) + '.md' or rec.name != str(r['date']) + '.receipt.json'):
            raise WriterHold('RECEIPT_INTEGRITY_HOLD')
        if type(r['source_ids']) is not list or r['sources_sha256'] != digest(encode_json(r['source_ids'])):
            raise WriterHold('RECEIPT_SOURCE_INTEGRITY_HOLD')
        if w.name in out:
            raise WriterHold('DUPLICATE_WEEK')
        out[w.name] = (r['date'], data)
    return out


def _index(entries: dict[str, tuple[str, bytes]]) -> bytes:
    return (KIND + '\n' + ''.join(f'{week} {entries[week][0]} {digest(entries[week][1])}\n' for week in sorted(entries))).encode('ascii')


def _validate_index(base: Path, entries: dict) -> None:
    index = base / '_index.txt'
    if not entries:
        if index.exists() or index.is_symlink():
            raise WriterHold('UNEXPECTED_EMPTY_INDEX')
    elif _safe_read(index) != _index(entries):
        raise WriterHold('INDEX_INTEGRITY_HOLD')


def _atomic_index(base: Path, contents: bytes) -> None:
    temp = base / ('._ci05_index_' + uuid.uuid4().hex)
    _write_exclusive(temp, contents)
    os.replace(temp, base / '_index.txt')


def stage_synthetic(root: Path, bundle: dict) -> dict:
    """Strict, deterministic synthetic only; no identity or release authority."""
    _check_path(root)
    v = validate(bundle)
    with _lease(root):
        base = root / FOLDER
        entries = _entries(root)
        _validate_index(base, entries) if base.exists() else None
        if v.week in entries:
            date, old_raw = entries[v.week]
            r = json.loads(_safe_read(base / v.week / (date + '.receipt.json')))
            if date != v.day or old_raw != v.markdown or r['sources_sha256'] != v.sources_sha256 or r['source_ids'] != list(v.sources):
                raise WriterHold('WEEK_CONFLICT_HOLD')
            return {'status':'CI05_SYNTHETIC_IDEMPOTENT_PASS', 'new_drafts':0, 'existing':1, 'production':False}
        if base.is_symlink():
            raise WriterHold('SYMLINK_ARCHIVE_ROOT')
        base.mkdir(mode=0o700, exist_ok=True)
        week_dir = base / v.week
        week_dir.mkdir(mode=0o700)
        receipt = {'schema':SCHEMA, 'kind':KIND,'week':v.week,'date':v.day,
                   'markdown_sha256':v.markdown_sha256,'sources_sha256':v.sources_sha256,
                   'source_ids':list(v.sources),'published':False}
        _write_exclusive(week_dir / (v.day + '.md'), v.markdown)
        _write_exclusive(week_dir / (v.day + '.receipt.json'), encode_json(receipt))
        changed = dict(entries)
        changed[v.week] = (v.day, v.markdown)
        _atomic_index(base, _index(changed))
        if _entries(root) != changed or _safe_read(base / '_index.txt') != _index(changed):
            raise WriterHold('AFTER_WRITE_LOCAL_READBACK_HOLD')
        return {'status':'CI05_SYNTHETIC_ARCHIVE_PASS_NOT_PUBLICATION', 'new_drafts':1,
                'existing':len(entries), 'receipt_digest_matches':True,
                'index_integrity':True, 'production':False, 'remote_write':False}
