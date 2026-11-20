"""CI05 synthetic Writer stage/replay/crash/secret/race regression tests."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from javis_public_research.validator import KIND, fake_case
from javis_public_research import draft_writer as w


class SyntheticWriterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='ci05-public-writer-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / w.MARKER).write_text(KIND+'\n', encoding='ascii')
        self.case = fake_case()

    def stage(self, packet=None):
        return w.stage_synthetic(self.root, packet or self.case)

    def test_initial_archive(self):
        r = self.stage()
        self.assertEqual(r['new_drafts'],1)
        self.assertTrue(r['receipt_digest_matches'])
        self.assertFalse(r['production'])

    def test_exact_markdown_bytes(self):
        self.stage()
        p=self.root / w.FOLDER / '2030-W14' / '2030-04-05.md'
        self.assertEqual(p.read_bytes(),self.case['full_markdown'].encode('utf-8'))

    def test_receipt_source_and_markdown_sha(self):
        self.stage()
        r=json.loads((self.root/w.FOLDER/'2030-W14'/'2030-04-05.receipt.json').read_text())
        self.assertEqual(r['markdown_sha256'], w.digest(self.case['full_markdown'].encode()))
        self.assertEqual(r['source_ids'], self.case['source_ids'])
        self.assertFalse(r['published'])

    def test_idempotent_replay(self):
        self.stage()
        self.assertEqual(self.stage()['new_drafts'],0)

    def test_changed_markdown_holds(self):
        self.stage()
        p=copy.deepcopy(self.case)
        p['full_markdown'] += '\nDifferent fictional content'
        with self.assertRaises(w.WriterHold): self.stage(p)

    def test_changed_source_ids_holds(self):
        self.stage()
        p=copy.deepcopy(self.case)
        p['source_ids']=['synthetic:new-fake']
        with self.assertRaises(w.WriterHold): self.stage(p)

    def test_corrupt_markdown_holds(self):
        self.stage()
        (self.root/w.FOLDER/'2030-W14'/'2030-04-05.md').write_text('corrupted')
        with self.assertRaises(w.WriterHold): self.stage()

    def test_corrupt_receipt_holds(self):
        self.stage()
        (self.root/w.FOLDER/'2030-W14'/'2030-04-05.receipt.json').write_text('{}')
        with self.assertRaises(w.WriterHold): self.stage()

    def test_corrupt_index_holds(self):
        self.stage()
        (self.root/w.FOLDER/'_index.txt').write_text('changed')
        with self.assertRaises(w.WriterHold): self.stage()

    def test_missing_receipt_crash_holds(self):
        self.stage()
        (self.root/w.FOLDER/'2030-W14'/'2030-04-05.receipt.json').unlink()
        with self.assertRaises(w.WriterHold): self.stage()

    def test_missing_index_crash_holds(self):
        self.stage()
        (self.root/w.FOLDER/'_index.txt').unlink()
        with self.assertRaises(w.WriterHold): self.stage()

    def test_lock_collision_holds(self):
        (self.root/w.LOCK).mkdir()
        with self.assertRaises(w.WriterHold): self.stage()

    def test_lock_released_success(self):
        self.stage()
        self.assertFalse((self.root/w.LOCK).exists())

    def test_lock_released_after_exception(self):
        self.stage()
        p=copy.deepcopy(self.case);p['full_markdown']+='other'
        with self.assertRaises(w.WriterHold):self.stage(p)
        self.assertFalse((self.root/w.LOCK).exists())

    def test_multiweek_cumulative_index(self):
        self.stage()
        second=fake_case('2030-W15','2030-04-12')
        self.assertEqual(self.stage(second)['new_drafts'],1)
        idx=(self.root/w.FOLDER/'_index.txt').read_text()
        self.assertIn('2030-W14',idx)
        self.assertIn('2030-W15',idx)
        self.assertEqual(self.stage(second)['new_drafts'],0)

    def test_existing_real_data_dir_denied(self):
        (self.root/'private_research').mkdir()
        with self.assertRaises(w.WriterHold):self.stage()

    def test_unmarked_scratch_denied(self):
        (self.root/w.MARKER).unlink()
        with self.assertRaises(w.WriterHold):self.stage()

    def test_wrong_marker_denied(self):
        (self.root/w.MARKER).write_text('unapproved\n')
        with self.assertRaises(w.WriterHold):self.stage()

    def test_git_root_denied(self):
        (self.root/'.git').mkdir()
        with self.assertRaises(w.WriterHold):self.stage()

    def test_symlink_marker_denied(self):
        (self.root/w.MARKER).unlink()
        x=self.root/'real';x.write_text(KIND+'\n')
        (self.root/w.MARKER).symlink_to(x)
        with self.assertRaises(w.WriterHold):self.stage()

    def test_symlink_archive_directory_denied(self):
        dest=self.root/'other';dest.mkdir()
        (self.root/w.FOLDER).symlink_to(dest)
        with self.assertRaises(w.WriterHold):self.stage()

    def test_symlink_draft_denied(self):
        self.stage()
        p=self.root/w.FOLDER/'2030-W14'/'2030-04-05.md'
        p.unlink();p.symlink_to(self.root/w.MARKER)
        with self.assertRaises(w.WriterHold):self.stage()

    def test_unexpected_file_denied(self):
        self.stage()
        (self.root/w.FOLDER/'2030-W14'/'other').write_text('hi')
        with self.assertRaises(w.WriterHold):self.stage()

    def test_private_credentials_environment_not_required(self):
        with mock.patch.dict(os.environ,{'GITHUB_TOKEN':'fake','GH_TOKEN':'fake','OPENAI_API_KEY':'fake'},clear=False):
            r=self.stage()
        self.assertFalse(r['remote_write'])

    def test_no_subprocess_or_network_in_writer_source(self):
        source=Path(w.__file__).read_text()
        for forbidden in ('subprocess', 'requests', 'urllib', 'import socket', 'git push', 'GITHUB_TOKEN'):
            self.assertNotIn(forbidden,source)

    def test_no_implicit_release_after_stage(self):
        r=self.stage()
        self.assertFalse(r['production'])
        self.assertFalse(r['remote_write'])

    def test_stage_refuses_actual_private_input(self):
        p=copy.deepcopy(self.case);p['fixture_kind']='UNAPPROVED_REAL_INPUT'
        with self.assertRaises(ValueError):self.stage(p)

    def test_no_real_tokens_in_receipt(self):
        self.stage()
        receipt=(self.root/w.FOLDER/'2030-W14'/'2030-04-05.receipt.json').read_text()
        self.assertNotIn('GITHUB_TOKEN',receipt)
        self.assertNotIn('PRIVATE',receipt)


if __name__ == '__main__':unittest.main()
