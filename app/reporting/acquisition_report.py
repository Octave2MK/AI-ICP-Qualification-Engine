from app.database.models import Prospect


class AcquisitionReport:
    """
    Génère un rapport lisible
    des prospects acquis.
    """

    def generate(
        self,
        prospects: list[Prospect],
        icp
    ) -> str:

        lines = []

        lines.append(
            "================================"
        )

        lines.append(
            "AI ICP Qualification Engine"
        )

        lines.append(
            "Acquisition Report"
        )

        lines.append(
            "================================"
        )

        lines.append("")

        lines.append(
            f"Roles: {', '.join(icp.job_titles)}"
        )

        lines.append(
            f"Countries: {', '.join(icp.countries)}"
        )

        lines.append("")

        lines.append(
            f"Prospects found: {len(prospects)}"
        )

        lines.append("")


        for index, prospect in enumerate(
            prospects,
            start=1
        ):
            lines.append(
                f"{index}."
            )

            lines.append(
                f"URL: {prospect.linkedin_url}"
            )

            lines.append(
                "Status: New"
            )

            lines.append(
                "Source: OSINT"
            )

            lines.append(
                "-----------------------------"
            )

        lines.append(
            "================================"
        )
        
        return "\n".join(lines)