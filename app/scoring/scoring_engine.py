from app.scoring.rules import (
    JOB_TITLE_RULES,
    COUNTRY_RULES,
    FOLLOWERS_RULES,
)


class ScoringEngine:

    @staticmethod
    def calculate_score(prospect):

        score = 0
        details = []

        # ----------------------
        # Job Title
        # ----------------------

        if prospect.job_title:
            job = prospect.job_title.lower()
            for keyword, points in JOB_TITLE_RULES.items():
                if keyword in job:
                    score += points
                    details.append({
                        "criterion": "Job Title",
                        "points": points,
                        "comment": keyword
                    })
                    break

        # ----------------------
        # Country
        # ----------------------
        if prospect.country:
            country = prospect.country.lower()
            if country in COUNTRY_RULES:

                points = COUNTRY_RULES[country]
                score += points
                details.append({
                    "criterion": "Country",
                    "points": points,
                    "comment": prospect.country
                })

        # ----------------------
        # Followers
        # ----------------------

        if prospect.followers is not None:
            for minimum, maximum, points in FOLLOWERS_RULES:
                if minimum <= prospect.followers <= maximum:
                    score += points
                    details.append({
                        "criterion": "Followers",
                        "points": points,
                        "comment": str(prospect.followers)
                    })
                    break

        return score, details