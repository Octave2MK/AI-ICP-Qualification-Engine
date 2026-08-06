from app.enrichment.dto import ProfileData
from app.qualification.icp.icp_definition import ICPDefinition


class PromptBuilder:

    def build(
        self,
        profile: ProfileData,
        icp: ICPDefinition | None = None,
    ) -> str:

        icp_section = self._build_icp_section(icp)

        return f"""
You are an expert B2B ICP qualification engine.

Your task is to analyze a professional profile
and determine if it matches the target ICP.

{icp_section}


PROFILE INFORMATION

Name:
{profile.name}

Headline:
{profile.headline}

About:
{profile.about}

Profile text:
{profile.clean_text}


RULES

- Use only information present in the profile.
- Do not invent facts.
- Do not make assumptions.
- Return JSON only.


EXPECTED JSON FORMAT

{{
    "profession": "",
    "sector": "",
    "target_market": "",
    "offer_detected": false,
    "authority_signals": [],
    "content_signals": [],
    "commercial_signals": [],
    "icp_match": false,
    "confidence": 0.0,
    "evidence": [],
    "exclusion_reason": null
}}
"""

    @staticmethod
    def _build_icp_section(
        icp: ICPDefinition | None,
    ) -> str:

        if not icp:
            return ""

        return f"""
TARGET ICP

Professions:
{", ".join(icp.professions)}

Sectors:
{", ".join(icp.sectors)}

Target markets:
{", ".join(icp.target_markets)}

Required keywords:
{", ".join(icp.required_keywords)}

Forbidden keywords:
{", ".join(icp.forbidden_keywords)}

Minimum confidence:
{icp.minimum_confidence}
"""