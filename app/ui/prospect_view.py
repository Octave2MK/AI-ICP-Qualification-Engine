import pandas as pd

def results_to_dataframe(results):
    """Build the intentionally compact prospect result table."""
    rows = []

    for item in results:
        prospect = item.get("prospect")
        rows.append(
            {
                "Nom": getattr(prospect, "fullname", ""),
                "LinkedIn": getattr(prospect, "linkedin_url", ""),
                "Métier": getattr(prospect, "job_title", ""),
                "Erreur": item.get("error", ""),
            }
        )

    return pd.DataFrame(
        rows,
        columns=["Nom", "LinkedIn", "Métier", "Erreur"],
    )
