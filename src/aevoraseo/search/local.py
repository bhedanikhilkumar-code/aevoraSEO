"""
Local search visibility signals, NAP consistency, and LocalBusiness schema auditing.
"""

import json
import re
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlsplit

from .models import LocalSignalAnalysis

LOCAL_BUSINESS_TYPES: Set[str] = {
    "localbusiness", "dentist", "dentalclinic", "medicalbusiness", "medicalclinic",
    "physician", "hospital", "legalservice", "attorney", "notary", "store",
    "restaurant", "barorpub", "cafeorcoffeeshop", "bakery", "financialservice",
    "bankorcreditunion", "accountingbusiness", "insuranceagency", "realestateagent",
    "automotivebusiness", "autorepair", "autodealer", "homeandconstructionbusiness",
    "plumber", "electrician", "generalcontractor", "roofingcontractor", "locksmith",
    "movingcompany", "healthandbeautybusiness", "beautysalon", "dayspa", "hairssalon",
    "lodgingbusiness", "hotel", "motel", "professionalservice", "drycleaningorlaundry",
    "childcare", "school", "veterinarycare",
}

PHONE_REGEX = re.compile(
    r"(?:\+?(\d{1,3}))?[-.\s]?(?:\(?(\d{2,4})\)?[-.\s]?)?(\d{3,4})[-.\s]?(\d{3,4})"
)
TEL_HREF_REGEX = re.compile(r"""href\s*=\s*['"]tel:([^'"]+)['"]""", re.IGNORECASE)
MAP_EMBED_REGEX = re.compile(
    r"""(?:iframe[^>]*src\s*=\s*['"][^'"]*(?:google\.com/maps|maps\.google\.com)[^'"]*['"]|href\s*=\s*['"][^'"]*(?:maps\.google\.com|google\.com/maps|maps\.app\.goo\.gl)[^'"]*['"])""",
    re.IGNORECASE,
)
ADDRESS_TAG_REGEX = re.compile(r"""<address[^>]*>(.*?)</address>""", re.IGNORECASE | re.DOTALL)


def extract_jsonld_schemas(html: str) -> List[Dict[str, Any]]:
    """Extract all JSON-LD script blocks from HTML."""
    schemas: List[Dict[str, Any]] = []
    pattern = re.compile(
        r"""<script[^>]*type\s*=\s*['"]application/ld\+json['"][^>]*>(.*?)</script>""",
        re.IGNORECASE | re.DOTALL,
    )
    for match in pattern.finditer(html):
        content = match.group(1).strip()
        if not content:
            continue
        try:
            data = json.loads(content)
            if isinstance(data, dict):
                if "@graph" in data and isinstance(data["@graph"], list):
                    schemas.extend([item for item in data["@graph"] if isinstance(item, dict)])
                else:
                    schemas.append(data)
            elif isinstance(data, list):
                schemas.extend([item for item in data if isinstance(item, dict)])
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
    return schemas


def audit_local_signals(url: str, html: str) -> LocalSignalAnalysis:
    """
    Audits a page for Local SEO visibility signals:
    - LocalBusiness schema and sub-types
    - NAP (Name, Address, Phone) consistency
    - Clickable telephone link
    - Map embed / directions link
    - Service areas declared
    - Opening hours & GeoCoordinates
    """
    schemas = extract_jsonld_schemas(html)
    schema_types: List[str] = []
    has_local_schema = False
    name: Optional[str] = None
    address_str: Optional[str] = None
    phone_str: Optional[str] = None
    service_areas: List[str] = []
    has_opening_hours = False
    has_geo = False

    for s in schemas:
        raw_type = s.get("@type", "")
        types = [raw_type] if isinstance(raw_type, str) else (raw_type if isinstance(raw_type, list) else [])
        for t in types:
            if not isinstance(t, str):
                continue
            schema_types.append(t)
            if t.lower() in LOCAL_BUSINESS_TYPES:
                has_local_schema = True
                if not name and "name" in s and isinstance(s["name"], str):
                    name = s["name"]
                if not phone_str and "telephone" in s and isinstance(s["telephone"], str):
                    phone_str = s["telephone"]

                addr = s.get("address")
                if isinstance(addr, dict) and not address_str:
                    parts = [
                        addr.get("streetAddress", ""),
                        addr.get("addressLocality", ""),
                        addr.get("addressRegion", ""),
                        addr.get("postalCode", ""),
                        addr.get("addressCountry", ""),
                    ]
                    address_str = ", ".join([p for p in parts if p and isinstance(p, str)])
                elif isinstance(addr, str) and not address_str:
                    address_str = addr

                if "openingHoursSpecification" in s or "openingHours" in s:
                    has_opening_hours = True

                geo = s.get("geo")
                if isinstance(geo, dict):
                    if "latitude" in geo and "longitude" in geo:
                        has_geo = True

                area = s.get("areaServed")
                if isinstance(area, str):
                    service_areas.append(area)
                elif isinstance(area, list):
                    for item in area:
                        if isinstance(item, str):
                            service_areas.append(item)
                        elif isinstance(item, dict) and "name" in item:
                            service_areas.append(str(item["name"]))
                elif isinstance(area, dict) and "name" in area:
                    service_areas.append(str(area["name"]))

    # Check for clickable tel link
    tel_matches = TEL_HREF_REGEX.findall(html)
    has_clickable_tel = len(tel_matches) > 0
    if not phone_str and tel_matches:
        phone_str = tel_matches[0].strip()

    # Check for map embed or directions link
    has_map = bool(MAP_EMBED_REGEX.search(html))

    # Fallback address check from <address> tag
    if not address_str:
        addr_match = ADDRESS_TAG_REGEX.search(html)
        if addr_match:
            raw_addr = re.sub(r"<[^>]+>", " ", addr_match.group(1)).strip()
            if len(raw_addr) > 10:
                address_str = " ".join(raw_addr.split()[:15])

    nap_present = bool(name and (address_str or has_local_schema) and (phone_str or has_clickable_tel))

    return LocalSignalAnalysis(
        url=url,
        has_local_business_schema=has_local_schema,
        schema_types=schema_types,
        nap_present=nap_present,
        name=name,
        address=address_str,
        phone=phone_str,
        has_clickable_tel=has_clickable_tel,
        has_map_embed_or_link=has_map,
        service_areas_declared=list(set(service_areas)),
        opening_hours_present=has_opening_hours,
        geo_coordinates_present=has_geo,
    )
