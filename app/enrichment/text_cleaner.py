import re


class TextCleaner:
    """Nettoie le texte extrait d'une page."""

    URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
    HASHTAG_PATTERN = re.compile(r"#\w+")
    def clean(self, text: str) -> str:
        text = self.URL_PATTERN.sub("", text)

        text = self.HASHTAG_PATTERN.sub("", text)

        text = re.sub(r"\s+", " ", text)

        return text.strip()