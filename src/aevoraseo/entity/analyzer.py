"""
AevoraSEO Entity & Authority Intelligence Analyzer
Coordinates entity extraction, knowledge graph topology, authority scoring, and multi-format reporting.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, urlsplit

from aevoraseo.evidence import selected_data
from .authority import calculate_entity_authority_score
from .consistency import audit_entity_conflicts
from .extractor import EntityExtractor
from .graph import EntityKnowledgeGraph
from .models import EntityAnalysisResult
from .persistence import save_entity_snapshot
from .reporter import save_entity_reports


def analyze_entity_snapshot(
    snapshot_dir: Path,
    out_dir: Optional[Path] = None,
    brand: str = ""
) -> EntityAnalysisResult:
    """
    Analyzes an existing crawl snapshot directory for entity signals, authority footprint, and graph topology.
    """
    snap_path = Path(snapshot_dir)
    if not snap_path.exists():
        raise FileNotFoundError(f"Snapshot directory does not exist: {snap_path}")

    # Read summary if present
    summary: Dict[str, Any] = {}
    summary_file = snap_path / "summary.json"
    if summary_file.exists():
        try:
            summary = json.loads(summary_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    target_url = summary.get("url") or summary.get("seed_url") or ""
    brand_name = brand or summary.get("brand") or (urlsplit(target_url).hostname or "").removeprefix("www.")

    # Read pages from pages.jsonl or crawl.sqlite3
    pages_raw: List[Dict[str, Any]] = []
    pages_file = snap_path / "pages.jsonl"
    if pages_file.exists():
        with pages_file.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        pages_raw.append(json.loads(line))
                    except Exception:
                        pass
    elif (snap_path / "crawl.sqlite3").exists():
        import sqlite3
        conn = sqlite3.connect(str(snap_path / "crawl.sqlite3"))
        try:
            cur = conn.cursor()
            rows = cur.execute("SELECT url, data_json, rendered_json, html FROM pages").fetchall()
            for url, data_str, rend_str, html in rows:
                p_dict = {"url": url, "html": html}
                if data_str:
                    try:
                        p_dict["data"] = json.loads(data_str)
                    except Exception:
                        pass
                if rend_str:
                    try:
                        p_dict["rendered"] = json.loads(rend_str)
                    except Exception:
                        pass
                pages_raw.append(p_dict)
        finally:
            conn.close()

    if not target_url and pages_raw:
        target_url = pages_raw[0].get("final_url") or pages_raw[0].get("url") or ""

    if not brand_name and target_url:
        brand_name = (urlsplit(target_url).hostname or "").removeprefix("www.")

    # Execute entity extraction
    extractor = EntityExtractor()
    crawled_urls: List[str] = []

    for page in pages_raw:
        data, _ = selected_data(page)
        url = page.get("final_url") or page.get("url") or ""
        if url:
            crawled_urls.append(url)
        extractor.extract_from_page(url, data)

    nodes = list(extractor.nodes.values())
    edges = extractor.edges
    same_as_links = extractor.same_as_links

    # Identify primary organization
    org_nodes = [n for n in nodes if n.entity_type in ("Organization", "Corporation", "LocalBusiness")]
    primary_org = org_nodes[0] if org_nodes else None

    # Audit conflicts and missing pages
    conflicts, missing_pages = audit_entity_conflicts(nodes, same_as_links, crawled_urls)

    # Build knowledge graph
    graph = EntityKnowledgeGraph(nodes, edges, same_as_links)
    graph_metrics = graph.calculate_metrics()
    graph_metrics["graph_json"] = graph.to_graph_json()

    # Calculate authority score
    score = calculate_entity_authority_score(nodes, conflicts, same_as_links, missing_pages)

    # Topical clusters from knowsAbout / keywords / categories
    topical_clusters: Dict[str, int] = {}
    for n in nodes:
        if n.entity_type in ("Article", "Service", "Product"):
            cat = n.attributes.get("serviceType") or n.attributes.get("category") or n.entity_type
            topical_clusters[cat] = topical_clusters.get(cat, 0) + 1

    created_at = datetime.now(timezone.utc).isoformat()
    snap_id = summary.get("snapshot_id") or snap_path.name

    result = EntityAnalysisResult(
        target_url=target_url,
        brand_name=brand_name,
        created_at=created_at,
        primary_organization=primary_org.to_dict() if primary_org else None,
        nodes=[n.to_dict() for n in nodes],
        edges=[e.to_dict() for e in edges],
        same_as_links=[sa.to_dict() for sa in same_as_links],
        conflicts=[c.to_dict() for c in conflicts],
        missing_entity_pages=missing_pages,
        score=score.to_dict(),
        topical_clusters=topical_clusters,
        graph_metrics=graph_metrics,
    )

    # Persistence and reports
    target_out = out_dir or snap_path
    save_entity_reports(result, target_out)
    db_path = target_out / "entities.sqlite3"
    save_entity_snapshot(db_path, result, snapshot_id=snap_id)

    return result


def analyze_target_entities(
    target: str,
    out_dir: Optional[Path] = None,
    brand: str = "",
) -> EntityAnalysisResult:
    """
    Main entry point. Analyzes either a crawl directory or directly fetches target URL.
    """
    target_path = Path(target)
    if target_path.exists() and target_path.is_dir():
        return analyze_entity_snapshot(target_path, out_dir=out_dir, brand=brand)

    # If target is a URL, perform bounded fetch of target
    url = target if target.startswith(("http://", "https://")) else f"https://{target}"
    from aevoraseo.crawler import crawl
    from aevoraseo.network import Config

    host_slug = (urlsplit(url).hostname or "target").removeprefix("www.").replace(".", "_")
    crawl_out = out_dir or Path(f"entity_crawl_{host_slug}")
    crawl_out.mkdir(parents=True, exist_ok=True)

    config = Config()
    config.max_pages = 10
    config.out = crawl_out
    crawl(url, config)

    return analyze_entity_snapshot(crawl_out, out_dir=crawl_out, brand=brand)
