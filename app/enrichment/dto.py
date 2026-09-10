from dataclasses import dataclass


@dataclass(slots=True)
class ProfileData:
    linkedin_url: str
    name: str
    headline: str
    about: str
    raw_text: str
    clean_text: str = ""
    acquisition_title: str = ""
    acquisition_snippet: str = ""
    latest_post_date: str = ""
    latest_post_text: str = ""

    def is_empty(self) -> bool:
        """True lorsque l'enrichissement n'a produit aucun contenu
        d'identité ou de bio exploitable (ex : LinkedIn a servi un mur de
        connexion au lieu du vrai profil).

        `raw_text` est volontairement exclu de cette vérification : un mur
        de connexion produit lui aussi une grande quantité de texte
        générique (boilerplate LinkedIn), donc sa seule présence n'est pas
        un signal fiable d'extraction réussie.
        """
        return not (self.name or self.headline or self.about)