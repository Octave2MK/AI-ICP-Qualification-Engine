from app.enrichment.profile_extractor import ProfileExtractor


HTML = """
<html>
    <head>
        <title>Jean Dupont | Consultant Marketing</title>
    </head>

    <body>

        <h1>Jean Dupont</h1>

        <p>
            J'aide les entreprises à développer leur activité.
        </p>

    </body>
</html>
"""


def test_extract_profile():
    extractor = ProfileExtractor()

    profile = extractor.extract(
        HTML,
        "https://linkedin.com/in/jean-dupont"
    )

    assert profile.linkedin_url == "https://linkedin.com/in/jean-dupont"

    assert profile.headline == "Jean Dupont | Consultant Marketing"

    assert "Jean Dupont" in profile.raw_text

    assert "développer leur activité" in profile.raw_text


def test_extract_empty_html():
    extractor = ProfileExtractor()

    profile = extractor.extract("<html></html>", "")

    assert profile.headline == ""

    assert profile.raw_text == ""