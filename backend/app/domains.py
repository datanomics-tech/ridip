"""The sectors RIDIP covers, how each lines up with national priorities, and sourced national targets.

Policy wording follows MINECOFIN's official NST2 presentation (January 2025) where it states the point;
figures reported only in press coverage of the NST2 launch are labelled as such.
"""

NST2_DECK = "https://www.social-protection.org/gimi/Media.action?id=20501"
NST2_PRESS = "https://www.newtimes.co.rw/article/19487/news/rwanda/unpacking-rwandas-five-year-development-strategy-here-are-the-14-goals/amp"

DOMAINS = {
    "agriculture": {
        "title": "Agriculture",
        "track": "Track 1: Agricultural Productivity",
        "question": "Where are farmers furthest from modern inputs, irrigation and good yields?",
        "decision": "Where should input, irrigation and soil-conservation programmes be assessed first?",
        "nst2": "NST2 (2024-2029) aims for over 6% annual agriculture growth and a modernised sector "
                "(MINECOFIN). Press coverage of the launch also reports aims to raise productivity by over "
                "50% and expand irrigated land by 85%.",
    },
    "finance_poverty": {
        "title": "Finance & poverty",
        "track": "Track 2: Financial Inclusion & Poverty Reduction",
        "question": "Where is poverty highest, and who is left out of formal finance and basic services?",
        "decision": "Where should graduation, financial-access and connectivity programmes be assessed first?",
        "nst2": "NST2 aims to reduce poverty by helping households graduate sustainably, increase access to "
                "finance for youth, women and MSMEs, and bring electricity to every cell (MINECOFIN). "
                "Vision 2050 commits Rwanda to eradicating poverty.",
    },
    "employment": {
        "title": "Employment",
        "track": "Track 3: Open Innovation · Employment",
        "question": "Where are young people and workers left without decent work?",
        "decision": "Where should youth employment and skills programmes be assessed first?",
        "nst2": "NST2 aims to create 1.25 million productive and decent jobs (250,000 a year) by 2029 "
                "(MINECOFIN).",
    },
    "health": {
        "title": "Health",
        "track": "Track 3: Open Innovation · Health",
        "question": "Where are children and mothers least reached by nutrition and health services?",
        "decision": "Where should nutrition and community-health programmes be assessed first?",
        "nst2": "NST2 aims to reduce stunting among children under five from 33% to 15% (MINECOFIN). Press "
                "coverage also reports aims to quadruple registered health workers.",
    },
    "education": {
        "title": "Education",
        "track": "Track 3: Open Innovation · Education",
        "question": "Where are children not attending, repeating or completing school, and where are digital skills lowest?",
        "decision": "Where should school-retention, remedial and digital-skills programmes be assessed first?",
        "nst2": "Press coverage of the NST2 launch reports aims to raise pre-primary enrolment from 35% to 65% "
                "and train 1 million coders and 500,000 people in advanced ICT.",
    },
    "transport": {
        "title": "Transport",
        "track": "Track 3: Open Innovation · Transport",
        "question": "Where are households furthest from all-weather roads and public transport?",
        "decision": "Where should feeder-road, route and transport-stage planning be assessed first?",
        "nst2": "Access to roads and public transport links households to the markets, jobs and services "
                "NST2's agriculture, jobs and health goals depend on. No district transport target is used.",
    },
}

# Only targets verified in the official text, with their level and horizon. A national target is a
# benchmark for comparison, not an obligation assigned to any district.
TARGETS = {
    "health_stunting": {
        "value": 15.0,
        "baseline": 33.0,
        "year": 2029,
        "level": "national",
        "label": "NST2 national target",
        "source": "MINECOFIN, NST2 2024-2029 presentation (January 2025), Social Transformation priority 2",
        "source_url": NST2_DECK,
    },
}
