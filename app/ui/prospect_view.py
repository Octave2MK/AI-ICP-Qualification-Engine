import pandas as pd


def results_to_dataframe(results):
    rows = []
    for item in results:
        prospect = item.get(
            "prospect"
        )
        if "error" in item:
            rows.append(
                {
                    "Nom": prospect.fullname,
                    "LinkedIn": prospect.linkedin_url,
                    "Erreur": item["error"],
                }
            )
            continue

        workflow_result = item.get(
            "qualification",
            {}
        )

        qualification = workflow_result.get(
            "qualification"
        )

        rows.append(
            {
                "Nom": prospect.fullname,
                "LinkedIn": prospect.linkedin_url,
                "Métier": prospect.job_title,
                "Score ICP": workflow_result.get(
                    "score",
                    0
                ),

                "ICP Match": (
                    qualification.icp_match
                    if qualification
                    else False
                ),

                "Confiance": (
                    qualification.confidence
                    if qualification
                    else 0
                ),

                "Offre B2B": (
                    qualification.offer_detected
                    if qualification
                    else False
                ),

                "Secteur": (
                    qualification.sector
                    if qualification
                    else ""
                ),

                "Profession": (
                    qualification.profession
                    if qualification
                    else ""
                ),
            }
        )
    return pd.DataFrame(rows)