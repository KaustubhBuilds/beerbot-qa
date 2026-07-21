"""
BeerBot : recommends a German beer based on your mood, the weather,
what you ate, and the time of day.

Built for fun, tested seriously. This is a playground for learning
agent evaluation.
"""
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq()
MODEL = "openai/gpt-oss-120b"


# ---------- FAKE DATA ----------

FAKE_WEATHER = {
    "Heilbronn": "8°C, drizzly and grey",
    "Berlin": "3°C, cold and windy",
    "Munich": "12°C, sunny and crisp",
    "Hamburg": "6°C, foggy with light rain",
    "Stuttgart": "10°C, cloudy but mild",
}

BEER_CATALOG = [
    {"name": "Weihenstephaner Hefeweissbier", "style": "Weissbier", "abv": 5.4,
     "notes": "banana, clove, creamy", "moods": ["celebratory", "warm-weather", "brunch"]},
    {"name": "Augustiner Helles", "style": "Helles Lager", "abv": 5.2,
     "notes": "clean, bready, subtle floral", "moods": ["relaxing", "afterwork", "food-friendly"]},
    {"name": "Ayinger Celebrator Doppelbock", "style": "Doppelbock", "abv": 6.7,
     "notes": "dark caramel, plum, warming", "moods": ["cold-weather", "cozy", "contemplative"]},
    {"name": "Schneider Weisse TAP7", "style": "Weissbier", "abv": 5.4,
     "notes": "bubblegum, spice, refreshing", "moods": ["celebratory", "warm-weather"]},
    {"name": "Andechser Doppelbock Dunkel", "style": "Doppelbock", "abv": 7.1,
     "notes": "molasses, dried fruit, malty", "moods": ["cold-weather", "cozy", "reflective"]},
    {"name": "Rothaus Tannenzäpfle", "style": "Pilsner", "abv": 5.1,
     "notes": "crisp, herbal, dry finish", "moods": ["afterwork", "food-friendly", "sharp"]},
    {"name": "Köstritzer Schwarzbier", "style": "Schwarzbier", "abv": 4.8,
     "notes": "roasty, smooth, chocolate hints", "moods": ["evening", "reflective", "food-friendly"]},
    {"name": "Paulaner Salvator", "style": "Doppelbock", "abv": 7.9,
     "notes": "rich malt, raisin, warming", "moods": ["cold-weather", "cozy", "celebratory"]},
    {"name": "Franziskaner Hefeweissbier", "style": "Weissbier", "abv": 5.0,
     "notes": "wheat, mild banana, easy", "moods": ["warm-weather", "brunch", "easy-drinking"]},
    {"name": "Erdinger Urweisse", "style": "Weissbier", "abv": 5.2,
     "notes": "yeasty, traditional, smooth", "moods": ["warm-weather", "food-friendly"]},
    {"name": "Bitburger Premium Pils", "style": "Pilsner", "abv": 4.8,
     "notes": "crisp, hoppy, refreshing", "moods": ["afterwork", "sports", "easy-drinking"]},
    {"name": "Warsteiner Premium", "style": "Pilsner", "abv": 4.8,
     "notes": "light, clean, slightly bitter", "moods": ["easy-drinking", "food-friendly"]},
    {"name": "Aecht Schlenkerla Rauchbier", "style": "Rauchbier", "abv": 5.1,
     "notes": "intensely smoky, bacon, unique", "moods": ["adventurous", "grilling", "conversation-starter"]},
    {"name": "Uerige Alt", "style": "Altbier", "abv": 4.7,
     "notes": "malty, bitter, copper-red", "moods": ["evening", "reflective", "food-friendly"]},
    {"name": "Früh Kölsch", "style": "Kölsch", "abv": 4.8,
     "notes": "delicate, slightly fruity, crisp", "moods": ["afterwork", "easy-drinking", "warm-weather"]},
    {"name": "Radeberger Pilsner", "style": "Pilsner", "abv": 4.8,
     "notes": "clean, hoppy, well-balanced", "moods": ["afterwork", "food-friendly"]},
    {"name": "Berliner Kindl Weisse", "style": "Berliner Weisse", "abv": 3.0,
     "notes": "tart, refreshing, low-alcohol", "moods": ["warm-weather", "brunch", "light"]},
    {"name": "Krombacher Pils", "style": "Pilsner", "abv": 4.8,
     "notes": "crisp, herbal, clean", "moods": ["afterwork", "sports", "easy-drinking"]},
    {"name": "Tucher Bajuvator", "style": "Doppelbock", "abv": 7.2,
     "notes": "sweet malt, caramel, warming", "moods": ["cold-weather", "cozy"]},
    {"name": "Flensburger Pilsener", "style": "Pilsner", "abv": 4.8,
     "notes": "crisp, dry, coastal character", "moods": ["afterwork", "food-friendly"]},
]


# ---------- TOOLS ----------

def get_weather(city: str) -> str:
    return FAKE_WEATHER.get(city, f"No data for {city}")


def get_beer_catalog() -> list:
    return BEER_CATALOG


LAST_RECOMMENDATION = {}

def recommend_beer(name: str, reason: str) -> str:
    global LAST_RECOMMENDATION
    LAST_RECOMMENDATION = {"name": name, "reason": reason}
    print(f"\n🍺 BeerBot recommends: {name}")
    print(f"   Because: {reason}")
    return f"Recommendation saved: {name}"


TOOL_FUNCTIONS = {
    "get_weather": get_weather,
    "get_beer_catalog": get_beer_catalog,
    "recommend_beer": recommend_beer,
}

TOOL_SCHEMAS = [
    {"type": "function", "function": {
        "name": "get_weather",
        "description": "Get current weather for a German city.",
        "parameters": {"type": "object",
                       "properties": {"city": {"type": "string", "description": "e.g. 'Heilbronn'"}},
                       "required": ["city"]}}},
    {"type": "function", "function": {
        "name": "get_beer_catalog",
        "description": "Get the full list of available German beers with styles, ABV, tasting notes and mood tags.",
        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {
        "name": "recommend_beer",
        "description": "Deliver your final beer recommendation. Call this once at the end.",
        "parameters": {"type": "object",
                       "properties": {
                           "name": {"type": "string", "description": "Exact beer name from the catalog"},
                           "reason": {"type": "string", "description": "Why this beer fits the user right now"},
                       },
                       "required": ["name", "reason"]}}},
]


# ---------- AGENT LOOP ----------

def run_beerbot(user_prompt: str, max_steps: int = 8, verbose: bool = True) -> dict:
    global LAST_RECOMMENDATION
    LAST_RECOMMENDATION = {}

    messages = [
        {"role": "system", "content": (
            "You are BeerBot, a friendly expert on German beer. "
            "The user will tell you their mood, what they ate, the time of day, and the city. "
            "Use get_weather to check the weather, get_beer_catalog to see available beers, "
            "then call recommend_beer EXACTLY ONCE with your final choice. "
            "Be thoughtful about matching mood, weather, food, and time of day. "
            "Always use the standard tool_calls JSON format."
        )},
        {"role": "user", "content": user_prompt},
    ]

    trace = []
    format_errors = 0

    for step in range(max_steps):
        if verbose:
            print(f"\n--- Step {step + 1} ---")

        # Retry loop for format errors (Llama sometimes outputs bad syntax)
        response = None
        for attempt in range(3):
            try:
                response = client.chat.completions.create(
                    model=MODEL, messages=messages, tools=TOOL_SCHEMAS,
                )
                break
            except Exception as e:
                if "tool_use_failed" in str(e) and attempt < 2:
                    format_errors += 1
                    if verbose:
                        print("⚠️  Format error, retrying...")
                    continue
                return {"status": "crashed", "error": str(e)[:200], "trace": trace,
                        "recommendation": LAST_RECOMMENDATION, "format_errors": format_errors}

        msg = response.choices[0].message

        if msg.tool_calls:
            messages.append(msg)
            for tool_call in msg.tool_calls:
                tool_name = tool_call.function.name
                # Handle None or empty args safely
                raw_args = tool_call.function.arguments
                tool_args = json.loads(raw_args) if raw_args else {}
                if tool_args is None:
                    tool_args = {}
                if verbose:
                    print(f"→ {tool_name}({tool_args})")
                try:
                    result = TOOL_FUNCTIONS[tool_name](**tool_args)
                except Exception as e:
                    result = f"Tool error: {e}"
                    if verbose:
                        print(f"   ⚠️  Tool crashed: {e}")
                trace.append({"step": step + 1, "tool": tool_name, "args": tool_args})
                messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(result)})
            continue

        # Agent finished with text — decide status based on whether recommend_beer was called
        recommend_called = any(step["tool"] == "recommend_beer" for step in trace)
        status = "success" if recommend_called else "no_recommendation"
        if verbose and not recommend_called:
            print("\n⚠️  Agent finished without calling recommend_beer.")
            print(f"   It said: {msg.content}")
        return {"status": status, "trace": trace,
                "recommendation": LAST_RECOMMENDATION, "text": msg.content,
                "format_errors": format_errors,
                "extra_chatter": msg.content if recommend_called else None}

    # Max steps
    recommend_called = any(step["tool"] == "recommend_beer" for step in trace)
    return {"status": "max_steps_exceeded" if not recommend_called else "success_but_overran",
            "trace": trace, "recommendation": LAST_RECOMMENDATION,
            "format_errors": format_errors}


# ---------- PLAY ----------

if __name__ == "__main__":
    prompt = input("\nTell BeerBot how you feel (mood, weather, food, time, city):\n> ")
    result = run_beerbot(prompt)
    print(f"\nStatus: {result['status']}, Tool calls: {len(result['trace'])}")
