from app.enrichment.profile_extractor import ProfileExtractor


HTML = """
<html>
    <head>
        <title>Jean Dupont | Consultant Marketing</title>
        <meta property="og:title" content="Jean Dupont | Consultant Marketing">
        <meta property="og:description" content="J'aide les entreprises à développer leur activité.">
    </head>
    <body>
        <h1>Jean Dupont</h1>
        <p>J'aide les entreprises à développer leur activité.</p>
    </body>
</html>
"""


def test_extract_profile():
    profile = ProfileExtractor().extract(
        HTML,
        "https://linkedin.com/in/jean-dupont",
    )

    assert profile.linkedin_url == "https://linkedin.com/in/jean-dupont"
    assert profile.name == "Jean Dupont"
    assert profile.headline == "Jean Dupont | Consultant Marketing"
    assert profile.about == "J'aide les entreprises à développer leur activité."
    assert "Jean Dupont" in profile.raw_text
    assert "développer leur activité" in profile.raw_text


def test_extract_profile_name_falls_back_to_title():
    html = """
    <html>
        <head><title>Marie Martin | Business Coach</title></head>
        <body><p>Accompagnement de dirigeants.</p></body>
    </html>
    """

    profile = ProfileExtractor().extract(html, "https://linkedin.com/in/marie-martin")

    assert profile.name == "Marie Martin"
    assert profile.headline == "Marie Martin | Business Coach"


def test_extract_empty_html():
    profile = ProfileExtractor().extract("<html></html>", "")

    assert profile.name == ""
    assert profile.headline == ""
    assert profile.about == ""
    assert profile.raw_text == ""
