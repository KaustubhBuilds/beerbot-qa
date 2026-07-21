"""
LLM-as-judge for BeerBot recommendations.

Uses a second LLM to score BeerBot's output against a rubric.
Returns structured scores per dimension.
"""
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq()

# Use the same model as BeerBot for now.
# In real production, judges often use a DIFFERENT model to reduce self-preference bias.
JUDGE_MODEL = "llama-3.3-70b-versatile"

RUBRIC = """You are an impartial, strict German beer expert grading a beer recommendation.

Important calibration guidance:
- Only give 5/5 for genuinely exceptional matches. In practice, only ~20% of recommendations deserve a 5.
- Give 3/5 for "acceptable but not thoughtful" — a beer that doesn't clash but isn't specifically chosen for the context.
- Give 1-2 for recommendations that clearly ignore or misread the user's input.
- Do NOT default to high scores. Be honest and critical.
- A generic recommendation that could apply to many situations should score 2-3, not 4-5.

Grade the recommendation on 4 dimensions, each on a scale of 1-5:

1. mood_match: Does the beer fit the user's stated mood?
   - 1 = the beer's character clashes with the mood (e.g., heavy Doppelbock for someone celebrating a summer party)
   - 3 = the beer is neutral/generic — doesn't clash but no specific mood alignment
   - 5 = the beer's mood tags directly and specifically match the user's stated mood

2. weather_appropriateness: Does the beer suit the weather?
   - 1 = clearly wrong (heavy dark warming beer for hot summer, light Berliner Weisse for freezing winter)
   - 3 = OK, wouldn't be strange in the weather but not specifically chosen for it
   - 5 = ideally matched — the ABV, body, and temperature-of-serving all align with the weather

3. food_pairing: Does the beer pair well with the user's food?
   - 1 = clashing pairing (hoppy Pilsner overwhelming delicate sushi, or dark Doppelbock with a light salad)
   - 3 = neutral, doesn't clash but not a classic pairing
   - 5 = classic, thoughtful pairing (Weissbier with Weisswurst, Kölsch with light fish, etc.)

4. reasoning_quality: Is the reason field a good explanation?
   - 1 = incoherent, contradicts itself, or invents facts not in the catalog
   - 3 = plausible but generic — could apply to many beers, no specific catalog reference
   - 5 = specific — references the actual catalog properties (ABV, style, tasting notes, mood tags)
     and connects them concretely to the user's input

Return your grades using the submit_grades tool. Include a brief, honest justification for each score.
Do not inflate. Be strict."""

JUDGE_TOOL_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "submit_grades",
            "description": "Submit your grades for the beer recommendation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mood_match": {"type": "integer", "description": "1-5"},
                    "mood_match_reason": {"type": "string"},
                    "weather_appropriateness": {"type": "integer", "description": "1-5"},
                    "weather_appropriateness_reason": {"type": "string"},
                    "food_pairing": {"type": "integer", "description": "1-5"},
                    "food_pairing_reason": {"type": "string"},
                    "reasoning_quality": {"type": "integer", "description": "1-5"},
                    "reasoning_quality_reason": {"type": "string"},
                },
                "required": [
                    "mood_match", "mood_match_reason",
                    "weather_appropriateness", "weather_appropriateness_reason",
                    "food_pairing", "food_pairing_reason",
                    "reasoning_quality", "reasoning_quality_reason",
                ],
            },
        },
    }
]


def judge_recommendation(user_prompt: str, beer_name: str, reason: str) -> dict:
    """Grade a BeerBot recommendation using an LLM judge.

    Returns a dict with scores and justifications for each dimension,
    plus a computed average.
    """
    context = f"""USER PROMPT:
{user_prompt}

BEERBOT'S RECOMMENDATION:
Beer: {beer_name}
Reason: {reason}"""

    messages = [
        {"role": "system", "content": RUBRIC},
        {"role": "user", "content": context},
    ]

    # Retry loop for format errors (same as BeerBot)
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=JUDGE_MODEL,
                messages=messages,
                tools=JUDGE_TOOL_SCHEMA,
                tool_choice={"type": "function", "function": {"name": "submit_grades"}},
            )
            break
        except Exception as e:
            if "tool_use_failed" in str(e) and attempt < 2:
                continue
            return {"error": str(e)[:200], "average": None}

    msg = response.choices[0].message
    if not msg.tool_calls:
        return {"error": "Judge did not submit grades", "average": None}

    grades = json.loads(msg.tool_calls[0].function.arguments)

    scores = [
        grades["mood_match"],
        grades["weather_appropriateness"],
        grades["food_pairing"],
        grades["reasoning_quality"],
    ]
    grades["average"] = sum(scores) / len(scores)

    return grades


# ---------- Quick sanity check ----------

if __name__ == "__main__":
    # Example recommendation to test the judge on
    test_prompt = "I'm tired, it's cold in Heilbronn, I just ate döner, it's 9pm"
    test_beer = "Köstritzer Schwarzbier"
    test_reason = (
        "A smooth, roasty Schwarzbier is perfect for a cold Heilbronn night. "
        "Its chocolate notes complement the savory döner spices, and the low "
        "ABV suits your tired mood."
    )

    print("Judging a sample recommendation...\n")
    result = judge_recommendation(test_prompt, test_beer, test_reason)

    print(f"Mood match: {result['mood_match']}/5 — {result['mood_match_reason']}")
    print(f"Weather:    {result['weather_appropriateness']}/5 — {result['weather_appropriateness_reason']}")
    print(f"Food:       {result['food_pairing']}/5 — {result['food_pairing_reason']}")
    print(f"Reasoning:  {result['reasoning_quality']}/5 — {result['reasoning_quality_reason']}")
    print(f"\nAverage: {result['average']:.2f}/5")
