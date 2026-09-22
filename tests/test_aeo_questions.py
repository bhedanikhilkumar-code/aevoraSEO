"""Tests for AevoraSEO AEO question and direct answer detection."""

import unittest

from aevoraseo.aeo.questions import (
    analyze_page_questions,
    extract_faq_from_jsonld,
    extract_questions_from_html,
    is_question_text,
)


class TestAEOQuestions(unittest.TestCase):
    def test_interrogative_detection(self):
        self.assertEqual(is_question_text("What is Search Engine Optimization?"), (True, "what"))
        self.assertEqual(is_question_text("How does crawl budget work?"), (True, "how"))
        self.assertEqual(is_question_text("Why should I use structured data?"), (True, "why"))
        self.assertEqual(is_question_text("Can crawlers execute modern JavaScript?"), (True, "can"))
        self.assertEqual(is_question_text("Is canonical URL mandatory?"), (True, "is"))
        self.assertEqual(is_question_text("Are outbound citations helpful?"), (True, "are"))

        # Non-questions
        self.assertEqual(is_question_text("Introduction to Web Architecture")[0], False)
        self.assertEqual(is_question_text("")[0], False)

    def test_html_question_heading_and_answer_proximity(self):
        html = """
        <html>
        <body>
            <h2>What is Generative Engine Optimization?</h2>
            <p>Generative Engine Optimization is a methodology that structures web content to be reliably digested and cited by AI answer engines.</p>
            <h3>How to verify robots permissions?</h3>
            <ol>
                <li>Inspect robots.txt directives</li>
                <li>Check meta robots tags</li>
                <li>Review HTTP X-Robots-Tag headers</li>
            </ol>
            <h4>Where is the data stored?</h4>
            <!-- No immediate answer here -->
            <h2>Next Topic</h2>
        </body>
        </html>
        """
        signals = extract_questions_from_html(html)
        self.assertEqual(len(signals), 3)

        # First question with concise definition paragraph
        q1 = signals[0]
        self.assertEqual(q1.question, "What is Generative Engine Optimization?")
        self.assertTrue(q1.answer_detected)
        self.assertIn("Generative Engine Optimization is a methodology", q1.answer_text)
        self.assertEqual(q1.answer_location, "heading:h2 + p")
        self.assertGreaterEqual(q1.confidence, 0.85)

        # Second question with ordered list steps
        q2 = signals[1]
        self.assertEqual(q2.question, "How to verify robots permissions?")
        self.assertTrue(q2.answer_detected)
        self.assertIn("Inspect robots.txt directives", q2.answer_text)
        self.assertEqual(q2.answer_location, "heading:h3 + ol")

        # Third question without immediate answer
        q3 = signals[2]
        self.assertEqual(q3.question, "Where is the data stored?")
        self.assertFalse(q3.answer_detected)
        self.assertEqual(q3.answer_text, "")

    def test_jsonld_faq_extraction(self):
        jsonld_blocks = [
            {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": "What is AevoraSEO?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "AevoraSEO is an autonomous SEO and AEO intelligence platform.",
                        },
                    },
                    {
                        "@type": "Question",
                        "name": "Does it support incremental crawling?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Yes, it leverages HTTP 304 conditional validation and SQLite snapshots.",
                        },
                    },
                ],
            }
        ]
        signals = extract_faq_from_jsonld(jsonld_blocks)
        self.assertEqual(len(signals), 2)
        self.assertEqual(signals[0].question, "What is AevoraSEO?")
        self.assertTrue(signals[0].answer_detected)
        self.assertEqual(signals[0].answer_location, "jsonld:FAQPage")
        self.assertEqual(signals[0].confidence, 0.95)

    def test_html_details_summary_faq(self):
        html = """
        <details>
            <summary>Can I export reports to CSV?</summary>
            <p>Yes, all AEO metrics can be exported as structured CSV files.</p>
        </details>
        """
        signals = extract_questions_from_html(html)
        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0].question, "Can I export reports to CSV?")
        self.assertTrue(signals[0].answer_detected)
        self.assertEqual(signals[0].answer_location, "details:summary + body")


if __name__ == "__main__":
    unittest.main()
