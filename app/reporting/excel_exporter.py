from pathlib import Path
from openpyxl import Workbook


class ExcelExporter:
    """
    Export Excel des prospects qualifiés.
    """

    HEADERS = [
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

    def export(
        self,
        prospects,
        filepath: str,
    ) -> Path:

        path = Path(filepath)

        workbook = Workbook()

        sheet = workbook.active

        sheet.title = "Prospects"

        sheet.append(
            self.HEADERS
        )

        for prospect in prospects:
            if hasattr(prospect, "url"):
                sheet.append(
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
                sheet.append(
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

        workbook.save(path)

        return path