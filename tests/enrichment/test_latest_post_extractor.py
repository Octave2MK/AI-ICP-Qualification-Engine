from bs4 import BeautifulSoup

from app.enrichment.latest_post_extractor import extract_latest_post


def test_extract_latest_post_returns_most_recent_post_date_and_text():
    html = """
    <html>
      <body>
        <article>
          <time datetime="2026-09-01T10:00:00Z">1w</time>
          <p>Older post</p>
        </article>
        <article>
          <time datetime="2026-09-09T10:00:00Z">1d</time>
          <p>Latest offer post</p>
        </article>
      </body>
    </html>
    """

    date, text = extract_latest_post(BeautifulSoup(html, "html.parser"))

    assert date == "2026-09-09"
    assert "Latest offer post" in text


def test_extract_latest_post_returns_empty_values_when_no_post_date_exists():
    soup = BeautifulSoup("<html><body><p>Profile only</p></body></html>", "html.parser")

    assert extract_latest_post(soup) == ("", "")
