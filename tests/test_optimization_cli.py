"""
Integration tests for CLI commands 'optimize' and 'optimize-compare'.
"""

import json
from pathlib import Path
from unittest.mock import patch

from aevoraseo.cli import main
from aevoraseo.optimization.reporter import sanitize_csv_cell


def _setup_mock_crawl_snapshot(snapshot_dir: Path):
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    p1 = {
        "url": "https://example.com/guide",
        "data": {
            "title": "Complete SEO Guide | ExampleBrand",
            "meta_description": "Discover comprehensive SEO strategies with our practical guide.",
            "headings": {
                "h1": ["Complete SEO Guide"],
                "h2": ["What is Technical SEO?", "How to Optimize Content?"],
            },
            "word_count": 850,
            "main_text": "Comprehensive explanation of SEO techniques and content strategies.",
            "links": [
                {"url": "https://example.com/services", "anchor": "Our Services"},
            ],
            "schema_types": ["Article"],
        },
        "html": """
        <html>
            <body>
                <h1>Complete SEO Guide</h1>
                <h2>What is Technical SEO?</h2>
                <p>Technical SEO refers to website and server optimizations that help search engine spiders crawl and index your site more effectively.</p>
                <h2>How to Optimize Content?</h2>
                <ol>
                    <li>Research queries.</li>
                    <li>Write answer boxes.</li>
                </ol>
            </body>
        </html>
        """,
    }
    (snapshot_dir / "page_001.json").write_text(json.dumps(p1), encoding="utf-8")


def test_sanitize_csv_cell_formula_injection():
    assert sanitize_csv_cell("=SUM(A1:A10)") == "'=SUM(A1:A10)"
    assert sanitize_csv_cell("+cmd|' /C calc'!A0") == "'+cmd|' /C calc'!A0"
    assert sanitize_csv_cell("-10") == "'-10"
    assert sanitize_csv_cell("@mention") == "'@mention"
    assert sanitize_csv_cell("\tTab") == "'\tTab"
    assert sanitize_csv_cell("Normal Text") == "Normal Text"
    assert sanitize_csv_cell(123) == "123"


def test_cli_optimize_terminal(tmp_path: Path, capsys):
    crawl_dir = tmp_path / "crawl1"
    _setup_mock_crawl_snapshot(crawl_dir)

    test_args = ["aevoraseo", "optimize", str(crawl_dir), "--format", "terminal"]
    with patch("sys.argv", test_args):
        ret = main()
        assert ret == 0

    out = capsys.readouterr().out
    assert "AEVORASEO CONTENT & OPTIMIZATION INTELLIGENCE" in out
    assert "HEADLINE CONTENT SCORE" in out


def test_cli_optimize_json_and_out(tmp_path: Path, capsys):
    crawl_dir = tmp_path / "crawl1"
    out_dir = tmp_path / "opt_out"
    _setup_mock_crawl_snapshot(crawl_dir)

    test_args = ["aevoraseo", "optimize", str(crawl_dir), "--out", str(out_dir), "--format", "json"]
    with patch("sys.argv", test_args):
        ret = main()
        assert ret == 0

    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert parsed["target_url"] == "https://example.com/guide"
    assert "headline" in parsed["score"]

    # Verify generated files
    assert (out_dir / "content_optimization.sqlite3").exists()
    assert (out_dir / "content-optimization.json").exists()
    assert (out_dir / "content-optimization.md").exists()
    assert (out_dir / "content-recommendations.csv").exists()
    assert (out_dir / "content-briefs.csv").exists()
    assert (out_dir / "direct-answers.csv").exists()
    assert (out_dir / "internal-links.csv").exists()


def test_cli_optimize_compare(tmp_path: Path, capsys):
    crawl1 = tmp_path / "crawl1"
    crawl2 = tmp_path / "crawl2"
    _setup_mock_crawl_snapshot(crawl1)
    _setup_mock_crawl_snapshot(crawl2)

    diff_out = tmp_path / "diff_out"
    test_args = [
        "aevoraseo", "optimize-compare",
        "--before", str(crawl1),
        "--after", str(crawl2),
        "--out", str(diff_out),
        "--format", "terminal",
    ]
    with patch("sys.argv", test_args):
        ret = main()
        assert ret == 0

    out = capsys.readouterr().out
    assert "CONTENT OPTIMIZATION SNAPSHOT COMPARISON" in out
    assert "Score Delta" in out
