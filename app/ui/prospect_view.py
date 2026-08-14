import pandas as pd


def _decision_status(workflow_result):
    """Return the normalized decision/status of one workflow result."""
    status = workflow_result.get("status")
    if status:
        return status

    decision = workflow_result.get("decision")
    if isinstance(decision, str):
        return decision

    return getattr(decision, "status", None)


def summarize_results(results):
    """Return accurate workflow outcome counts for the Streamlit summary."""
    errors = 0
    filtered = 0
    successful = 0

    for item in results:
        if "error" in item:
            errors += 1
            continue

        workflow_result = item.get("qualification") or {}
        status = _decision_status(workflow_result)

        if status == "QUALIFIED":
            successful += 1
        else:
            # EXCLUDED/FILTERED happen before Gemini; REJECTED/REVIEW can
            # happen after Gemini. All are non-successful outcomes.
            filtered += 1

    return {
        "successful": successful,
        "errors": errors,
        "filtered": filtered,
    }


def results_to_dataframe(results):
    """Build the intentionally compact prospect result table."""
    rows = []

    for item in results:
        prospect = item.get("prospect")
        rows.append(
            {
                "Nom": getattr(prospect, "fullname", ""),
                "LinkedIn": getattr(prospect, "linkedin_url", ""),
                "Erreur": item.get("error", ""),
                "Métier": getattr(prospect, "job_title", ""),
            }
        )

    return pd.DataFrame(
        rows,
        columns=["Nom", "LinkedIn", "Erreur", "Métier"],
    )
