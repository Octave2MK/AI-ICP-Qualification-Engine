from datetime import datetime

from bs4 import BeautifulSoup


POST_SELECTORS = (
    "div.feed-shared-update-v2",
    "article",
    "div[data-urn*='activity']",
)


def extract_latest_post(soup: BeautifulSoup) -> tuple[str, str]:
    """Return the latest identifiable post date and visible post text.

    Only dates found inside likely feed/post containers are considered. If no
    post date can be identified, the function returns empty values rather than
    inferring or inventing a date.
    """
    candidates: list[tuple[datetime, str]] = []

    for selector in POST_SELECTORS:
        for container in soup.select(selector):
            for time_node in container.select("time[datetime]"):
                raw_date = (time_node.get("datetime") or "").strip()
                parsed = _parse_datetime(raw_date)
                if parsed is None:
                    continue

                text = container.get_text(" ", strip=True)
                candidates.append((parsed, text))

    if not candidates:
        return "", ""

    latest_date, latest_text = max(candidates, key=lambda item: item[0])
    return latest_date.date().isoformat(), latest_text[:4000]


def _parse_datetime(value: str) -> datetime | None:
    if not value:
        return None

    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None
