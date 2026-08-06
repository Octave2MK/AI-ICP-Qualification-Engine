from app.qualification.config.icp_loader import ICPLoader


def test_loader_returns_business_coach():

    loader = ICPLoader()

    icp = loader.load("business_coach")

    assert icp.professions[0] == "Business Coach"