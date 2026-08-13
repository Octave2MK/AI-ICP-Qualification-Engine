import pytest

pytestmark = pytest.mark.integration

from ddgs import DDGS


def test_ddg_direct():

    with DDGS() as ddgs:

        results = list(
            ddgs.text(
                "Business Coach France",
                max_results=5
            )
        )

        print("\nRESULTS:")
        for result in results:
            print(result)

        assert len(results) > 0