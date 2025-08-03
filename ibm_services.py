from dotenv import load_dotenv
load_dotenv()

import os
import json
import demjson3
from ibm_watsonx_ai.foundation_models import ModelInference

# Load credentials from environment variables
api_key = os.getenv("WATSONX_APIKEY")
url = os.getenv("WATSONX_URL")
project_id = os.getenv("PROJECT_ID")

if not api_key or not url or not project_id:
    raise ValueError("Missing WatsonX credentials in environment variables.")

credentials = {
    "url": url,
    "apikey": api_key
}

# Initialize Granite model
chat = ModelInference(
    model_id="ibm/granite-3-8b-instruct",
    params={
        "decoding_method": "greedy",
        "temperature": 0,
        "max_new_tokens": 1200,
    },
    credentials=credentials,
    project_id=project_id,
)

def try_parse_json(output_text):
    """Try to fix JSON using demjson3 if it's malformed."""
    try:
        return json.loads(output_text)
    except Exception:
        try:
            return demjson3.decode(output_text)
        except Exception:
            return None

def generate_meal_plan(goals, conditions, preferences, days=3):
    prompt = f"""
You are an AI nutritionist. Generate a {days}-day meal plan in JSON format with this structure:
{{
  "days": [
    {{
      "day": "Day 1",
      "meals": [
        {{
          "type": "Breakfast",
          "item": "Meal name",
          "why": "Short explanation",
          "calories": 350,
          "macros": {{"protein": 20, "carbs": 40, "fat": 10}}
        }}
      ]
    }}
  ]
}}
Requirements:
- Goal: {goals}
- Conditions: {conditions}
- Preferences: {preferences}
Strictly output only JSON.
"""

    response = chat.generate_text(prompt=prompt)
    raw_output = response.get("results", [{}])[0].get("generated_text", "") if isinstance(response, dict) else str(response)

    meal_plan = try_parse_json(raw_output)
    if not meal_plan:
        raise Exception(f"Failed to parse AI output. Raw output: {raw_output}")

    return meal_plan
