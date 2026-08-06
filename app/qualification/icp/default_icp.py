from app.qualification.icp.icp_definition import ICPDefinition


DEFAULT_BUSINESS_ICP = ICPDefinition(
    professions=[
        "Business Coach",
        "Consultant",
        "Trainer",
        "Freelancer",
    ],

    sectors=[
        "Consulting",
        "Coaching",
        "Training",
    ],

    target_markets=[
        "B2B",
    ],

    required_keywords=[
        "coaching",
        "consulting",
        "training",
    ],

    forbidden_keywords=[
        "student",
        "job seeker",
        "internship",
    ],

    minimum_confidence=0.70,
)