"""CI05 public-only synthetic validator negative/positive contract tests."""
from __future__ import annotations

import copy
import unittest

from javis_public_research.validator import KIND, PublicInputHold, fake_case, validate


class SyntheticPublicValidatorTests(unittest.TestCase):
    def setUp(self):
        self.case = fake_case()

    def deny(self, **updates):
        obj = copy.deepcopy(self.case)
        obj.update(updates)
        with self.assertRaises(PublicInputHold):
            validate(obj)

    def test_valid_fictional_input(self):
        v = validate(self.case)
        self.assertEqual(v.week, '2030-W14')
        self.assertEqual(len(v.markdown_sha256), 64)
        self.assertEqual(len(v.sources_sha256), 64)

    def test_marker_missing(self): self.deny(fixture_kind='')
    def test_marker_forged_real(self): self.deny(fixture_kind='UNAPPROVED_REAL_INPUT')
    def test_private_report_rejected(self): self.deny(full_markdown='2030-W14 confidential workspace text')
    def test_extra_field_denied(self): self.deny(owner_approved=True)
    def test_missing_field_denied(self):
        x = copy.deepcopy(self.case)
        x.pop('source_ids')
        with self.assertRaises(PublicInputHold): validate(x)
    def test_wrong_type_denied(self): self.deny(week=202647)
    def test_traversal_week_denied(self): self.deny(week='../2030-W14')
    def test_wrong_friday_denied(self): self.deny(date='2026-11-19')
    def test_wrong_iso_week_denied(self): self.deny(week='2026-W46')
    def test_invalid_date_denied(self): self.deny(date='2026-02-30')
    def test_real_source_url_denied(self): self.deny(source_ids=['https://example.org/fictional-unapproved-source'])
    def test_real_arxiv_source_denied(self): self.deny(source_ids=['arxiv:9999.99999v1'])
    def test_duplicate_source_denied(self): self.deny(source_ids=['synthetic:paper-one'] * 2)
    def test_private_link_denied(self): self.deny(full_markdown=self.case['full_markdown'] + '\nhttps://example.com')
    def test_secret_shape_denied(self): self.deny(full_markdown=self.case['full_markdown'] + '\nGHp_long_fake_token')
    def test_null_byte_denied(self): self.deny(full_markdown=self.case['full_markdown'] + '\0')
    def test_carriage_return_denied(self): self.deny(full_markdown=self.case['full_markdown'] + '\r')
    def test_oversize_denied(self): self.deny(full_markdown=KIND + '\n' + 'a' * 13000)
    def test_empty_body_denied(self): self.deny(full_markdown=KIND + '\n')
    def test_trailing_whitespace_preserved(self):
        x = copy.deepcopy(self.case)
        x['full_markdown'] += ' \n'
        self.assertTrue(validate(x).markdown.endswith(b' \n'))


if __name__ == '__main__': unittest.main()
