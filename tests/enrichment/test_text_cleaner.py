from app.enrichment.text_cleaner import TextCleaner


def test_remove_urls():
    cleaner = TextCleaner()

    text = cleaner.clean(
        "Visitez https://example.com maintenant"
    )

    assert "https://" not in text


def test_remove_hashtags():
    cleaner = TextCleaner()

    text = cleaner.clean(
        "Coach #marketing #linkedin"
    )

    assert "#" not in text


def test_normalize_spaces():
    cleaner = TextCleaner()

    text = cleaner.clean(
        "Bonjour      tout\n\nle     monde"
    )

    assert text == "Bonjour tout le monde"


def test_empty_text():
    cleaner = TextCleaner()

    assert cleaner.clean("") == ""