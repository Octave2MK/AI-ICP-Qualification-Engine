from app.qualification.dto import QualificationResult


class AIScoringEngine:

    @staticmethod
    def calculate_score(
        qualification: QualificationResult
    ):

        score = 0

        details = []


        # ----------------------
        # ICP Match
        # ----------------------

        if qualification.icp_match:

            score += 30

            details.append({
                "criterion": "ICP Match",
                "points": 30,
                "comment": "Profil correspondant à la cible"
            })


        # ----------------------
        # Offre détectée
        # ----------------------

        if qualification.offer_detected:

            score += 20

            details.append({
                "criterion": "Offer",
                "points": 20,
                "comment": "Offre de service détectée"
            })


        # ----------------------
        # Signaux autorité
        # ----------------------

        if qualification.authority_signals:

            score += 15

            details.append({
                "criterion": "Authority",
                "points": 15,
                "comment": "Signaux d'autorité détectés"
            })


        # ----------------------
        # Création contenu
        # ----------------------

        if qualification.content_signals:

            score += 15

            details.append({
                "criterion": "Content",
                "points": 15,
                "comment": "Création de contenu détectée"
            })


        # ----------------------
        # Signaux commerciaux
        # ----------------------

        if qualification.commercial_signals:

            score += 20

            details.append({
                "criterion": "Commercial",
                "points": 20,
                "comment": "Signaux commerciaux détectés"
            })


        return score, details