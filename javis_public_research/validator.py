"""CI05 independent PUBLIC-ONLY synthetic input validation.

No private source, credentials, OS calls, network, or publication authorization.
THIS VALIDATOR DOES NOT ACCEPT REAL RESEARCH DATA.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import hashlib
import json
import re

KIND = 'CI05_SYNTHETIC_ONLY_NOT_FOR_PUBLICATION'
FIELDS = frozenset({'fixture_kind', 'week', 'date', 'full_markdown', 'source_ids'})
WEEK = re.compile(r'20[0-9]{2}-W(?:0[1-9]|[1-4][0-9]|5[0-3])\Z')
SOURCE = re.compile(r'synthetic:[a-z][a-z0-9-]{1,63}\Z')
MAX_MARKDOWN_BYTES = 12_000


class PublicInputHold(ValueError):
    """Denied untrusted or out-of-scope input (not production approval)."""


@dataclass(frozen=True)
class Validated:
    week: str
    day: str
    markdown: bytes
    markdown_sha256: str
    sources: tuple[str, ...]
    sources_sha256: str


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def encode_json(data: object) -> bytes:
    return (json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2, separators=(',', ': ')) + '\n').encode('utf-8')


def validate(obj: object) -> Validated:
    if type(obj) is not dict or set(obj) != FIELDS or obj.get('fixture_kind') != KIND:
        raise PublicInputHold('CI05_SYNTHETIC_SCHEMA_ONLY')
    week, day, source_ids, text = (obj[k] for k in ('week','date','source_ids','full_markdown'))
    if type(week) is not str or not WEEK.fullmatch(week) or type(day) is not str:
        raise PublicInputHold('WEEK_OR_DATE_SCHEMA')
    try:
        d = date.fromisoformat(day)
    except ValueError as exc:
        raise PublicInputHold('DATE_NOT_ISO') from exc
    if d.isoformat() != day or d.isoweekday() != 5 or f'{d.isocalendar().year}-W{d.isocalendar().week:02d}' != week:
        raise PublicInputHold('DATE_WEEK_MISMATCH')
    if type(source_ids) is not list or not 1 <= len(source_ids) <= 10 or any(
        type(s) is not str or not SOURCE.fullmatch(s) for s in source_ids
    ) or len(set(source_ids)) != len(source_ids):
        raise PublicInputHold('SYNTHETIC_SOURCES_ONLY')
    if type(text) is not str or not text.startswith(KIND + '\n'):
        raise PublicInputHold('REAL_MARKDOWN_DENIED')
    raw = text.encode('utf-8')
    if not (90 <= len(raw) <= MAX_MARKDOWN_BYTES) or b'\x00' in raw or b'\r' in raw:
        raise PublicInputHold('MARKDOWN_CONTENT_INVALID')
    # Only toy/plain fixture data is accepted. No real research URLs or technical bodies.
    if any(key in text.lower() for key in ('https://', 'http://', 'private_workspace',
                                          'github_pat_', 'ghp_', 'sk-proj-',
                                          '/users/', '/home/', 'private key')):
        raise PublicInputHold('EXTERNAL_OR_PRIVATE_CONTENT_DENIED')
    sr = encode_json(source_ids)
    return Validated(week, day, raw, digest(raw), tuple(source_ids), digest(sr))


def fake_case(week: str = '2030-W14', day: str = '2030-04-05') -> dict:
    return {'fixture_kind': KIND, 'week': week, 'date': day,
            'source_ids': ['synthetic:paper-one', 'synthetic:paper-two'],
            'full_markdown': KIND + '\n' + ('Original fictional test markdown only.\n' * 7)}
