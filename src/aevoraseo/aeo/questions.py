"""
AevoraSEO AEO Question & Direct Answer Analyzer
Detects interrogative patterns, question headings, FAQ structures, answer proximity,
and calculates deterministic answer-readiness confidence.
"""

import re
from typing import Any, Dict, List, Optional, Tuple
from bs4 import BeautifulSoup

from aevoraseo.aeo.models import QuestionAnswerSignal

INTERROGATIVE_STARTERS = (
    "what",
    "why",
    "how",
    "when",
    "where",
    "who",
    "which",
    "can",
    "does",
    "is",
    "are",
    "should",
    "will",
    "could",
    "would",
    "do",
    "did",
)

DEFINITION_MARKERS = (
    " is a ",
    " is an ",
    " refers to ",
    " is defined as ",
    " means ",
    " consists of ",
    " represents ",
    " provides ",
    " allows you to ",
    " can be defined as ",
)


def is_question_text(text: str) -> Tuple[bool, str]:
    """
    Checks whether a string is phrased as a question.
    Returns (is_question, interrogative_type).
    """
    clean_text = text.strip()
    if not clean_text:
        return False, ""

    lower_text = clean_text.lower()
    has_question_mark = clean_text.endswith("?")

    # Check interrogative starters
    words = re.findall(r"\b[a-z]+\b", lower_text)
    if not words:
        return False, ""

    first_word = words[0]
    if first_word in INTERROGATIVE_STARTERS:
        return True, first_word

    if has_question_mark and len(words) >= 3:
        return True, first_word if first_word in INTERROGATIVE_STARTERS else "other"

    return False, ""


def extract_faq_from_jsonld(jsonld_blocks: List[Any]) -> List[QuestionAnswerSignal]:
    """
    Extracts structured Q&A pairs from JSON-LD FAQPage blocks.
    """
    signals: List[QuestionAnswerSignal] = []

    def _traverse(node: Any):
        if isinstance(node, dict):
            type_val = node.get("@type", "")
            types = type_val if isinstance(type_val, list) else [type_val]
            if any(t in ("FAQPage", "QAPage") for t in types):
                entities = node.get("mainEntity", [])
                if isinstance(entities, dict):
                    entities = [entities]
                for entity in entities:
                    if isinstance(entity, dict) and entity.get("@type") == "Question":
                        q_name = str(entity.get("name", "")).strip()
                        ans = entity.get("acceptedAnswer") or entity.get("suggestedAnswer") or {}
                        a_text = ""
                        if isinstance(ans, dict):
                            a_text = str(ans.get("text", "")).strip()
                        elif isinstance(ans, list) and ans:
                            a_text = str(ans[0].get("text", "")).strip()

                        if q_name:
                            _, itype = is_question_text(q_name)
                            signals.append(
                                QuestionAnswerSignal(
                                    question=q_name,
                                    detected=True,
                                    answer_detected=bool(a_text),
                                    answer_text=a_text[:300],
                                    answer_location="jsonld:FAQPage",
                                    interrogative_type=itype or "faq",
                                    confidence=0.95 if a_text else 0.70,
                                )
                            )
            for v in node.values():
                _traverse(v)
        elif isinstance(node, list):
            for item in node:
                _traverse(item)

    for block in jsonld_blocks:
        _traverse(block)

    return signals


def extract_questions_from_html(
    html: str,
    headings_data: Optional[Dict[str, List[str]]] = None
) -> List[QuestionAnswerSignal]:
    """
    Analyzes HTML for question headings and their direct answer proximity.
    """
    signals: List[QuestionAnswerSignal] = []
    seen_questions = set()

    if not html:
        # Fallback to headings_data if HTML string is unavailable
        if headings_data:
            for level, heading_list in headings_data.items():
                for h in heading_list:
                    is_q, itype = is_question_text(h)
                    if is_q and h.lower() not in seen_questions:
                        seen_questions.add(h.lower())
                        signals.append(
                            QuestionAnswerSignal(
                                question=h,
                                detected=True,
                                answer_detected=False,
                                answer_text="",
                                answer_location=f"heading:{level}",
                                interrogative_type=itype,
                                confidence=0.55,
                            )
                        )
        return signals

    soup = BeautifulSoup(html, "html.parser")

    # 1. Inspect headings h1 - h4
    for tag_name in ["h1", "h2", "h3", "h4"]:
        for heading in soup.find_all(tag_name):
            heading_text = heading.get_text(" ", strip=True)
            is_q, itype = is_question_text(heading_text)
            if not is_q or heading_text.lower() in seen_questions:
                continue

            seen_questions.add(heading_text.lower())

            # Look for answer in immediate following sibling elements
            answer_detected = False
            answer_text = ""
            answer_location = f"heading:{tag_name}"
            confidence = 0.60

            if heading_text.endswith("?"):
                confidence += 0.10
            if itype in INTERROGATIVE_STARTERS:
                confidence += 0.05

            curr = heading.next_sibling
            hops = 0
            while curr and hops < 5:
                if getattr(curr, "name", None) in ["h1", "h2", "h3", "h4"]:
                    # Hit next section heading without finding answer
                    break

                if getattr(curr, "name", None) == "p":
                    p_text = curr.get_text(" ", strip=True)
                    if len(p_text) > 15:
                        answer_detected = True
                        answer_text = p_text[:300]
                        answer_location = f"heading:{tag_name} + p"
                        words = p_text.split()
                        # Concise introductory answer (10-60 words) receives confidence bonus
                        if 10 <= len(words) <= 60:
                            confidence += 0.15
                        # Definition phrasing bonus
                        if any(marker in f" {p_text.lower()} " for marker in DEFINITION_MARKERS):
                            confidence += 0.10
                        break

                elif getattr(curr, "name", None) in ["ol", "ul"]:
                    items = [li.get_text(" ", strip=True) for li in curr.find_all("li")]
                    if items:
                        answer_detected = True
                        answer_text = "; ".join(items[:3])[:300]
                        answer_location = f"heading:{tag_name} + {curr.name}"
                        confidence += 0.15
                        break

                elif getattr(curr, "name", None) == "dl":
                    dds = [dd.get_text(" ", strip=True) for dd in curr.find_all("dd")]
                    if dds:
                        answer_detected = True
                        answer_text = "; ".join(dds[:2])[:300]
                        answer_location = f"heading:{tag_name} + dl"
                        confidence += 0.15
                        break

                curr = curr.next_sibling
                hops += 1

            confidence = min(0.98, max(0.20, confidence)) if answer_detected else min(0.60, confidence)

            signals.append(
                QuestionAnswerSignal(
                    question=heading_text,
                    detected=True,
                    answer_detected=answer_detected,
                    answer_text=answer_text,
                    answer_location=answer_location,
                    interrogative_type=itype,
                    confidence=round(confidence, 2),
                )
            )

    # 2. Inspect <details><summary> FAQ structures
    for details in soup.find_all("details"):
        summary = details.find("summary")
        if summary:
            s_text = summary.get_text(" ", strip=True)
            if s_text and s_text.lower() not in seen_questions:
                seen_questions.add(s_text.lower())
                is_q, itype = is_question_text(s_text)
                body_text = ""
                # Get text of details excluding summary
                for child in details.children:
                    if child != summary and hasattr(child, "get_text"):
                        child_t = child.get_text(" ", strip=True)
                        if child_t:
                            body_text = child_t
                            break

                signals.append(
                    QuestionAnswerSignal(
                        question=s_text,
                        detected=True,
                        answer_detected=bool(body_text),
                        answer_text=body_text[:300],
                        answer_location="details:summary + body",
                        interrogative_type=itype or "faq",
                        confidence=0.88 if body_text else 0.50,
                    )
                )

    return signals


def analyze_page_questions(
    page_data: Dict[str, Any],
    html: Optional[str] = None
) -> List[QuestionAnswerSignal]:
    """
    Unified analyzer combining JSON-LD FAQ analysis with DOM question parsing.
    """
    signals: List[QuestionAnswerSignal] = []
    seen = set()

    # 1. JSON-LD FAQ
    jsonld_blocks = page_data.get("jsonld", [])
    if jsonld_blocks:
        faq_signals = extract_faq_from_jsonld(jsonld_blocks)
        for s in faq_signals:
            if s.question.lower() not in seen:
                seen.add(s.question.lower())
                signals.append(s)

    # 2. HTML DOM extraction
    html_content = html or ""
    dom_signals = extract_questions_from_html(
        html_content,
        headings_data=page_data.get("headings", {})
    )
    for s in dom_signals:
        if s.question.lower() not in seen:
            seen.add(s.question.lower())
            signals.append(s)

    return signals
