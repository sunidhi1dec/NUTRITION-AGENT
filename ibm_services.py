from dotenv import load_dotenv

load_dotenv()

import os
import json
import demjson3
import re
from ibm_watsonx_ai.foundation_models import ModelInference

api_key = os.getenv("WATSONX_APIKEY")
url = os.getenv("WATSONX_URL")
project_id = os.getenv("PROJECT_ID")

if not api_key or not url or not project_id:
    raise ValueError("Missing WatsonX credentials in environment variables.")

credentials = {
    "url": url,
    "apikey": api_key
}

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


def extract_and_combine_json_objects(text):

    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    json_matches = re.findall(json_pattern, text, re.DOTALL)

    combined_days = []

    for match in json_matches:
        try:
            obj = json.loads(match)
            if 'days' in obj and isinstance(obj['days'], list):
                for day in obj['days']:
                    existing_day = None
                    for existing in combined_days:
                        if existing.get('day') == day.get('day'):
                            existing_day = existing
                            break

                    if existing_day:
                        existing_day['meals'].extend(day.get('meals', []))
                    else:
                        combined_days.append(day)
        except:
            continue

    if combined_days:
        return {"days": combined_days}

    return None


def try_parse_json(output_text):

    try:
        return json.loads(output_text)
    except:
        pass

    try:
        return demjson3.decode(output_text)
    except:
        pass

    try:
        combined = extract_and_combine_json_objects(output_text)
        if combined:
            return combined
    except:
        pass

    try:
        start = output_text.find('{')
        if start != -1:
            brace_count = 0
            for i, char in enumerate(output_text[start:], start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        json_str = output_text[start:i + 1]
                        return json.loads(json_str)
    except:
        pass

    return None


def generate_meal_plan(goals, conditions, preferences, days=3):
    prompt = f"""
You are an AI nutritionist. Generate a {days}-day meal plan in JSON format with this EXACT structure:
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
        }},
        {{
          "type": "Lunch",
          "item": "Meal name",
          "why": "Short explanation",
          "calories": 500,
          "macros": {{"protein": 25, "carbs": 60, "fat": 15}}
        }},
        {{
          "type": "Dinner",
          "item": "Meal name",
          "why": "Short explanation",
          "calories": 600,
          "macros": {{"protein": 30, "carbs": 70, "fat": 20}}
        }}
      ]
    }},
    {{
      "day": "Day 2",
      "meals": [
        {{
          "type": "Breakfast",
          "item": "Different meal",
          "why": "Short explanation",
          "calories": 350,
          "macros": {{"protein": 20, "carbs": 40, "fat": 10}}
        }},
        {{
          "type": "Lunch",
          "item": "Different meal",
          "why": "Short explanation", 
          "calories": 500,
          "macros": {{"protein": 25, "carbs": 60, "fat": 15}}
        }},
        {{
          "type": "Dinner",
          "item": "Different meal",
          "why": "Short explanation",
          "calories": 600,
          "macros": {{"protein": 30, "carbs": 70, "fat": 20}}
        }}
      ]
    }}
  ]
}}

Requirements:
- Goal: {goals}
- Conditions: {conditions}
- Preferences: {preferences}
- Include ALL {days} days in a SINGLE JSON object
- Each day should have 3 meals: Breakfast, Lunch, Dinner
- Output ONLY the JSON structure, no other text
- Start with {{ and end with }}
"""

    response = chat.generate_text(prompt=prompt)
    raw_output = response.get("results", [{}])[0].get("generated_text", "") if isinstance(response, dict) else str(
        response)

    raw_output = raw_output.strip()

    meal_plan = try_parse_json(raw_output)
    if not meal_plan:
        raise Exception(f"Failed to parse AI output. Raw output: {raw_output}")

    if not isinstance(meal_plan, dict) or 'days' not in meal_plan:
        raise Exception(f"Invalid meal plan structure. Expected 'days' key in output.")

    if meal_plan['days']:
        try:
            meal_plan['days'] = sorted(meal_plan['days'], key=lambda x: int(x.get('day', 'Day 0').split()[-1]))
        except:
            pass
    return meal_plan
