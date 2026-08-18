from app.scoring.rules import (
    COUNTRY_RULES,
    FOLLOWERS_RULES,
    JOB_TITLE_RULES,
)


def test_job_title_rules_keys_are_lowercase():
    """ScoringEngine looks up keywords against a lowercased job title, so a
    non-lowercase key here could never match and would be dead weight."""
    for keyword in JOB_TITLE_RULES:
        assert keyword == keyword.lower()


def test_job_title_rules_points_are_positive_integers():
    for points in JOB_TITLE_RULES.values():
        assert isinstance(points, int)
        assert points > 0


def test_country_rules_keys_are_lowercase():
    for country in COUNTRY_RULES:
        assert country == country.lower()


def test_country_rules_points_are_positive_integers():
    for points in COUNTRY_RULES.values():
        assert isinstance(points, int)
        assert points > 0


def test_followers_rules_ranges_are_well_formed_and_non_overlapping():
    ranges = sorted(FOLLOWERS_RULES, key=lambda rule: rule[0])

    previous_maximum = None
    for minimum, maximum, points in ranges:
        assert minimum <= maximum
        assert isinstance(points, int)

        if previous_maximum is not None:
            assert minimum > previous_maximum, (
                "Follower ranges must not overlap, otherwise only the "
                "first matching rule in declaration order would ever apply."
            )
        previous_maximum = maximum


def test_followers_rules_start_at_zero():
    minimums = [minimum for minimum, _maximum, _points in FOLLOWERS_RULES]
    assert min(minimums) == 0
