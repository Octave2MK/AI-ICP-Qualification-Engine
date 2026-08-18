from app.enrichment.text_cleaner import TextCleaner


class CleanTextPipeline:
    """Populates `clean_text` the same way EnrichmentService.enrich() does
    for the legacy (requests + BeautifulSoup) path, so both engines produce
    equivalent ProfileData output."""

    def __init__(self):
        self._cleaner = TextCleaner()

    def process_item(self, item):
        item["clean_text"] = self._cleaner.clean(item.get("raw_text", ""))
        return item
