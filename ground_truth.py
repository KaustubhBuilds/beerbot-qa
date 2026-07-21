"""
Constructed ground truth for judge validation.

These 5 recommendation-and-score pairs are hand-designed to test whether
the LLM judge can discriminate between good, mediocre, and bad recommendations.

IMPORTANT: These scores are NOT sourced from real beer sommeliers. They are
synthesized to give the validation methodology something to measure against.
The purpose is to demonstrate the workflow, not to establish beer authority.
"""

GROUND_TRUTH_CASES = [
    {
        "id": "case_1_excellent_match",
        "user_prompt": "I'm celebrating with friends, it's warm in Munich, I ate pretzels, it's 6pm",
        "beer_name": "Weihenstephaner Hefeweissbier",
        "beer_reason": (
            "A classic Bavarian Weissbier with banana and clove notes — "
            "perfect for a warm celebratory evening in Munich. Its "
            "creamy body pairs beautifully with soft pretzels, and its "
            "celebratory mood tags match the festive spirit."
        ),
        "expert_scores": {
            "mood_match": 5,
            "weather_appropriateness": 5,
            "food_pairing": 5,
            "reasoning_quality": 5,
        },
        "why": "Textbook Bavarian pairing — Weissbier + pretzels + Munich summer is iconic.",
    },
    {
        "id": "case_2_terrible_mismatch",
        "user_prompt": "It's a hot summer day in Berlin, I want something light, I ate salad, it's 3pm",
        "beer_name": "Ayinger Celebrator Doppelbock",
        "beer_reason": (
            "A rich, warming Doppelbock with dark caramel and plum notes. "
            "The malty body pairs with your salad, and the higher ABV gives "
            "you a solid afternoon buzz."
        ),
        "expert_scores": {
            "mood_match": 2,
            "weather_appropriateness": 1,
            "food_pairing": 1,
            "reasoning_quality": 1,
        },
        "why": "Doppelbock at 6.7% ABV is completely wrong for hot day + light salad + wanting something light.",
    },
    {
        "id": "case_3_defensible_but_generic",
        "user_prompt": "I want to chill after work, it's cool in Stuttgart, I ate wurst, it's 5pm",
        "beer_name": "Bitburger Premium Pils",
        "beer_reason": (
            "A crisp, hoppy Pilsner that's perfect for after work. Its "
            "clean finish pairs with wurst and its easy-drinking profile "
            "suits your relaxed mood."
        ),
        "expert_scores": {
            "mood_match": 4,
            "weather_appropriateness": 3,
            "food_pairing": 3,
            "reasoning_quality": 3,
        },
        "why": "Generic recommendation — a Rothaus Pils or Kölsch would show more thought, and reasoning is boilerplate.",
    },
    {
        "id": "case_4_good_but_not_classic",
        "user_prompt": "I want something cozy, it's cold in Hamburg, I ate schnitzel, it's 8pm",
        "beer_name": "Köstritzer Schwarzbier",
        "beer_reason": (
            "A smooth, roasty Schwarzbier with subtle chocolate hints. "
            "Its cold-weather friendly profile fits a Hamburg winter evening, "
            "and the malty depth complements the crispy schnitzel."
        ),
        "expert_scores": {
            "mood_match": 4,
            "weather_appropriateness": 4,
            "food_pairing": 4,
            "reasoning_quality": 4,
        },
        "why": "Solid pairing but not classic — Uerige Alt or a Doppelbock would be more traditional with schnitzel.",
    },
    {
        "id": "case_5_borderline_food_mismatch",
        "user_prompt": "I feel reflective, it's foggy in Hamburg, I ate light fish, it's 7pm",
        "beer_name": "Aecht Schlenkerla Rauchbier",
        "beer_reason": (
            "An intensely smoky Rauchbier that's a conversation starter. "
            "The bold flavor matches your reflective mood on a foggy evening, "
            "and its adventurous character pairs with fish."
        ),
        "expert_scores": {
            "mood_match": 3,
            "weather_appropriateness": 3,
            "food_pairing": 2,
            "reasoning_quality": 3,
        },
        "why": "Smoky Rauchbier overwhelms delicate fish — food is a real mismatch, other dimensions are OK-not-great.",
    },
]
