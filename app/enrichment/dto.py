from dataclasses import dataclass


@dataclass(slots=True)
class ProfileData:
    linkedin_url: str
    name: str
    headline: str
    about: str
    raw_text: str
    clean_text: str = ""