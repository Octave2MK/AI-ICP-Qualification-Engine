import pytest

from app.api.job_service import _normalize_linkedin_url, _serialize_result


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("", ""),
        (None, ""),
        ("https://www.linkedin.com/in/john-doe", "https://www.linkedin.com/in/john-doe"),
        ("http://linkedin.com/in/john-doe", "http://linkedin.com/in/john-doe"),
        ("linkedin.com/in/john-doe", "https://linkedin.com/in/john-doe"),
        ("  linkedin.com/in/john-doe  ", "https://linkedin.com/in/john-doe"),
    ],
)
def test_normalize_linkedin_url(raw, expected):
    assert _normalize_linkedin_url(raw) == expected


class _FakeProspect:
    def __init__(self, fullname="", linkedin_url="", job_title=""):
        self.fullname = fullname
        self.linkedin_url = linkedin_url
        self.job_title = job_title


def test_serialize_result_produces_a_clickable_absolute_url():
    item = {
        "prospect": _FakeProspect(
            fullname="John Doe",
            linkedin_url="linkedin.com/in/john-doe",
            job_title="Business Coach",
        ),
        "error": None,
    }

    serialized = _serialize_result(item)

    assert serialized["linkedin_url"] == "https://linkedin.com/in/john-doe"
    assert serialized["name"] == "John Doe"
