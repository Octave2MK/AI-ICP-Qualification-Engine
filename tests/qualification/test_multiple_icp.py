from app.qualification.icp.icp_definition import ICPDefinition


def test_multiple_icp_are_independent():

    coach_icp = ICPDefinition(
        professions=[
            "Business Coach"
        ]
    )


    consultant_icp = ICPDefinition(
        professions=[
            "Consultant"
        ]
    )


    assert coach_icp.professions != consultant_icp.professions