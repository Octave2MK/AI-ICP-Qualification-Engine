from app.enrichment.dto import ProfileData

from app.qualification.exclusions.rules import EXCLUSION_KEYWORDS


class ExclusionEngine:

    @staticmethod
    def check(profile: ProfileData):

        text = (
            f"{profile.headline} "
            f"{profile.about} "
            f"{profile.raw_text} "
            f"{profile.clean_text}"
        ).lower()


        for keyword, reason in EXCLUSION_KEYWORDS.items():

            if keyword in text:

                return {
                    "excluded": True,
                    "reason": reason,
                }


        return {
            "excluded": False,
            "reason": None,
        }