# ==========================================
# Job Title
# ==========================================

JOB_TITLE_RULES = {
    "business coach": 25,
    "coach business": 25,
    "consultant": 20,
    "consultant marketing": 20,
    "consultant b2b": 22,
    "coach mindset": 20,
    "freelance": 15,
    "conférencier": 15,
}


# ==========================================
# Pays
# ==========================================

COUNTRY_RULES = {
    "france": 10,
    "belgique": 8,
    "canada": 8,
    "suisse": 8,
    "bénin": 4,
    "benin": 4,
    "côte d'ivoire": 4,
    "cote d'ivoire": 4,
}


# ==========================================
# Followers
# ==========================================

FOLLOWERS_RULES = [
    (0, 499, -5),
    (500, 10000, 15),
    (10001, 50000, 8),
    (50001, 1000000, 5),
]