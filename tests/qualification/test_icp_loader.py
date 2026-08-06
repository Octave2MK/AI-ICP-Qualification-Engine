from pathlib import Path

from app.qualification.config.icp_loader import ICPLoader


def test_config_exists():
    assert Path("configs/business_coach.json").exists()


def test_load_business_coach_icp():

    loader = ICPLoader()

    icp = loader.load("business_coach")

    assert "Business Coach" in icp.professions

    assert "Consulting" in icp.sectors

    assert "B2B" in icp.target_markets

import pytest


def test_unknown_icp():

    loader = ICPLoader()

    with pytest.raises(FileNotFoundError):
        loader.load("unknown_icp")