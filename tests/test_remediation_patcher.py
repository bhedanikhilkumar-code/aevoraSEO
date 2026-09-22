"""Unit tests for AevoraSEO remediation AST/HTML patch generators."""

from __future__ import annotations

import json
import unittest

from aevoraseo.remediation.patcher import (
    PatchType,
    patch_canonical,
    patch_direct_answer,
    patch_headings,
    patch_internal_link,
    patch_meta_description,
    patch_schema,
    patch_title,
)


class RemediationPatcherTests(unittest.TestCase):
    def test_patch_title_replace_existing(self):
        html = "<html><head><title>Old Title</title></head><body><h1>Hello</h1></body></html>"
        res = patch_title(html, "New Optimized Title | Brand")
        self.assertTrue(res.success)
        self.assertEqual(res.patch_type, PatchType.TITLE)
        self.assertIn("<title>New Optimized Title | Brand</title>", res.full_html)
        self.assertNotIn("Old Title", res.full_html)
        self.assertIn("Old Title", res.diff)
        self.assertIn("New Optimized Title | Brand", res.diff)

    def test_patch_title_insert_in_head(self):
        html = "<html><head><meta charset='utf-8'></head><body><h1>Hello</h1></body></html>"
        res = patch_title(html, "Inserted Title")
        self.assertTrue(res.success)
        self.assertIn("<title>Inserted Title</title>", res.full_html)

    def test_patch_title_insert_at_root(self):
        html = "<div>Simple snippet without head</div>"
        res = patch_title(html, "Root Title")
        self.assertTrue(res.success)
        self.assertIn("<title>Root Title</title>", res.full_html)

    def test_patch_meta_description_update(self):
        html = '<html><head><meta name="description" content="Short desc"></head><body></body></html>'
        new_desc = "Discover our comprehensive SEO and AEO intelligence platform with automated remediation."
        res = patch_meta_description(html, new_desc)
        self.assertTrue(res.success)
        self.assertIn(f'content="{new_desc}"', res.full_html)
        self.assertNotIn("Short desc", res.full_html)

    def test_patch_meta_description_insert(self):
        html = "<html><head><title>Test Page</title></head><body></body></html>"
        new_desc = "Explore our advanced generative engine optimization guides and audit toolkits."
        res = patch_meta_description(html, new_desc)
        self.assertTrue(res.success)
        self.assertIn(f'<meta content="{new_desc}" name="description"/>', res.full_html)

    def test_patch_headings_insert_single_h1(self):
        html = "<html><body><p>Some introductory paragraph without any heading.</p></body></html>"
        res = patch_headings(html, h1_text="Primary Target Keyword")
        self.assertTrue(res.success)
        self.assertIn("<h1>Primary Target Keyword</h1>", res.full_html)

    def test_patch_headings_demote_extra_h1(self):
        html = "<html><body><h1>First Main Heading</h1><p>Text</p><h1>Second Heading That Should Be H2</h1></body></html>"
        res = patch_headings(html, demote_extra_h1=True)
        self.assertTrue(res.success)
        self.assertIn("<h1>First Main Heading</h1>", res.full_html)
        self.assertIn("<h2>Second Heading That Should Be H2</h2>", res.full_html)
        self.assertEqual(res.full_html.count("<h1>"), 1)

    def test_patch_headings_level_repairs(self):
        html = "<html><body><h1>Main</h1><h3>Skipped Level H3</h3></body></html>"
        res = patch_headings(html, level_repairs={"h3": "h2"})
        self.assertTrue(res.success)
        self.assertIn("<h2>Skipped Level H3</h2>", res.full_html)
        self.assertNotIn("<h3>", res.full_html)

    def test_patch_direct_answer_inject(self):
        html = "<html><body><h2>What is AEO?</h2><p>General intro</p></body></html>"
        answer = "AEO (Answer Engine Optimization) is the practice of structuring content so AI search engines can cite it directly."
        res = patch_direct_answer(html, "What is AEO", answer)
        self.assertTrue(res.success)
        self.assertIn('class="aevora-direct-answer"', res.full_html)
        self.assertIn(answer, res.full_html)

    def test_patch_direct_answer_with_list(self):
        html = "<html><body><h2>How to audit schema?</h2></body></html>"
        answer = "Auditing schema involves three structured verification steps:"
        items = ["Inspect JSON-LD syntax", "Verify required properties", "Test Google rich results"]
        res = patch_direct_answer(html, "How to audit schema", answer, list_items=items)
        self.assertTrue(res.success)
        self.assertIn('class="aevora-answer-list"', res.full_html)
        for item in items:
            self.assertIn(f"<li>{item}</li>", res.full_html)

    def test_patch_direct_answer_not_found(self):
        html = "<html><body><h2>Topic Overview</h2></body></html>"
        res = patch_direct_answer(html, "Nonexistent Question", "Some answer")
        self.assertFalse(res.success)
        self.assertIn("not found", res.details)

    def test_patch_schema_inject(self):
        html = "<html><head><title>Dentist Page</title></head><body></body></html>"
        schema_data = {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": "Acme Dental Care",
            "telephone": "+1-555-0199",
        }
        res = patch_schema(html, schema_data)
        self.assertTrue(res.success)
        self.assertIn('type="application/ld+json"', res.full_html)
        self.assertIn("Acme Dental Care", res.full_html)

    def test_patch_schema_skip_duplicate(self):
        schema_data = {
            "@context": "https://schema.org",
            "@type": "Article",
            "name": "SEO Trends 2026",
        }
        html = f'<html><head><script type="application/ld+json">\n{json.dumps(schema_data)}\n</script></head><body></body></html>'
        res = patch_schema(html, schema_data)
        self.assertFalse(res.success)
        self.assertIn("already exists", res.details)

    def test_patch_canonical_inject_and_update(self):
        # Insert
        html1 = "<html><head><title>Test</title></head><body></body></html>"
        res1 = patch_canonical(html1, "https://example.com/canonical")
        self.assertTrue(res1.success)
        self.assertIn('<link href="https://example.com/canonical" rel="canonical"/>', res1.full_html)

        # Update
        html2 = '<html><head><link rel="canonical" href="https://example.com/old"/></head><body></body></html>'
        res2 = patch_canonical(html2, "https://example.com/new")
        self.assertTrue(res2.success)
        self.assertIn('href="https://example.com/new"', res2.full_html)
        self.assertNotIn("old", res2.full_html)

    def test_patch_internal_link_in_text(self):
        html = "<html><body><p>We provide advanced dental implants for patients in Seattle.</p></body></html>"
        res = patch_internal_link(html, "https://example.com/services/implants", "dental implants")
        self.assertTrue(res.success)
        self.assertIn('<a href="https://example.com/services/implants">dental implants</a>', res.full_html)

    def test_patch_internal_link_append_fallback(self):
        html = "<html><body><p>Generic text without mentioning the target topic.</p></body></html>"
        res = patch_internal_link(html, "https://example.com/services/whitening", "Teeth Whitening")
        self.assertTrue(res.success)
        self.assertIn('class="aevora-related-link"', res.full_html)
        self.assertIn('<a href="https://example.com/services/whitening">Teeth Whitening</a>', res.full_html)


if __name__ == "__main__":
    unittest.main()
