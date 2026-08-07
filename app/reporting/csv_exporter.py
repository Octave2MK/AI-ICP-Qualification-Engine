import csv
from pathlib import Path


class CSVExporter:
    """
    Export CSV des prospects qualifiés.
    """

    def export(
        self,
        prospects,
        filepath: str,
    ) -> Path:

        path = Path(filepath)

        with path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.writer(file)

            writer.writerow(
                [
                    "linkedin_url",
                    "name",
                    "headline",
                    "profession",
                    "sector",
                    "target_market",
                    "offer_detected",
                    "icp_match",
                    "confidence",
                    "authority_signals",
                    "content_signals",
                    "commercial_signals",
                    "evidence",
                    "exclusion_reason",
                ]
            )

            for prospect in prospects:
                if hasattr(prospect, "url"):
                    writer.writerow(
                        [
                            prospect.url,
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                            "",
                        ]
                    )
                else:
                    writer.writerow(
                        [
                            prospect.linkedin_url,
                            prospect.name,
                            prospect.headline,
                            prospect.profession,
                            prospect.sector,
                            prospect.target_market,
                            prospect.offer_detected,
                            prospect.icp_match,
                            prospect.confidence,
                            ", ".join(
                                prospect.authority_signals
                            ),
                            ", ".join(
                                prospect.content_signals
                            ),
                            ", ".join(
                                prospect.commercial_signals
                            ),
                            ", ".join(
                                prospect.evidence
                            ),
                            prospect.exclusion_reason,
                        ]
                    )

        return path