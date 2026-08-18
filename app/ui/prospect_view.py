import pandas as pd


def _normalize_linkedin_url(url):
    """Return a clickable absolute URL when a LinkedIn URL is available."""
    if not url:
        return ""

    value = str(url).strip()
    if not value:
        return ""

    if value.startswith(("http://", "https://")):
        return value

    if value.startswith("linkedin.com/"):
        return f"https://{value}"

    return value


def results_to_dataframe(results):
    """Build the intentionally compact prospect result table."""
    rows = []

    for item in results:
        prospect = item.get("prospect")
        rows.append(
            {
                "Prospect": getattr(prospect, "fullname", "") or "",
                "Profil LinkedIn": _normalize_linkedin_url(
                    getattr(prospect, "linkedin_url", "")
                ),
                "Métier": getattr(prospect, "job_title", "") or "",
                "Erreur": item.get("error", "") or "",
            }
        )

    return pd.DataFrame(
        rows,
        columns=["Prospect", "Profil LinkedIn", "Métier", "Erreur"],
    )
