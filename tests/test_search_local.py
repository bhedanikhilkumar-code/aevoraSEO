"""
Tests for local search visibility signals, NAP consistency, and schema auditing.
"""

from aevoraseo.search.local import audit_local_signals


def test_audit_local_signals_complete():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Arlington Dental Clinic</title>
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Dentist",
            "name": "Arlington Heights Smile Center",
            "telephone": "+1-847-555-0199",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "120 W Eastman St",
                "addressLocality": "Arlington Heights",
                "addressRegion": "IL",
                "postalCode": "60004",
                "addressCountry": "US"
            },
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": "42.0834",
                "longitude": "-87.9806"
            },
            "openingHoursSpecification": [
                {
                    "@type": "OpeningHoursSpecification",
                    "dayOfWeek": ["Monday", "Tuesday", "Wednesday"],
                    "opens": "08:00",
                    "closes": "17:00"
                }
            ],
            "areaServed": ["Arlington Heights", "Mount Prospect", "Palatine"]
        }
        </script>
    </head>
    <body>
        <h1>Welcome to Arlington Heights Smile Center</h1>
        <p>Call our office: <a href="tel:+18475550199">+1 (847) 555-0199</a></p>
        <iframe src="https://www.google.com/maps/embed?pb=123" width="600" height="450"></iframe>
    </body>
    </html>
    """

    res = audit_local_signals("https://example.com/locations/arlington", html)
    assert res.has_local_business_schema is True
    assert "Dentist" in res.schema_types
    assert res.nap_present is True
    assert res.name == "Arlington Heights Smile Center"
    assert "Arlington Heights" in (res.address or "")
    assert res.phone == "+1-847-555-0199"
    assert res.has_clickable_tel is True
    assert res.has_map_embed_or_link is True
    assert res.opening_hours_present is True
    assert res.geo_coordinates_present is True
    assert "Mount Prospect" in res.service_areas_declared


def test_audit_local_signals_missing_clickable_tel_and_schema():
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Downtown Office</title></head>
    <body>
        <h1>Downtown Law Office</h1>
        <address>100 Main St, Chicago, IL 60601</address>
        <p>Phone: 312-555-0144 (plain text)</p>
    </body>
    </html>
    """

    res = audit_local_signals("https://example.com/chicago", html)
    assert res.has_local_business_schema is False
    assert res.has_clickable_tel is False
    assert res.has_map_embed_or_link is False
    assert res.address is not None
