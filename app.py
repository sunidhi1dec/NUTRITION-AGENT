from flask import Flask, render_template, request
from ibm_services import generate_meal_plan

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        goals = request.form.get("goals", "")
        conditions = request.form.get("conditions", "")
        preferences = request.form.get("preferences", "")
        days = int(request.form.get("days", 3))

        try:
            meal_plan = generate_meal_plan(goals, conditions, preferences, days)
            return render_template("result.html",
                                   meal_plan=meal_plan,
                                   goals=goals,
                                   conditions=conditions,
                                   preferences=preferences,
                                   days=days)
        except Exception as e:
            # Ensure meal_plan is defined (fallback to empty plan)
            fallback_meal_plan = {
                "days": []
            }
            return render_template("result.html",
                                   error="Error generating meal plan",
                                   meal_plan=fallback_meal_plan,
                                   raw_output_debug=str(e))

    # Render index page
    return render_template("index.html",
                           preference_options=[
                               "Vegetarian", "Non Vegetarian", "Vegan", "Keto", "Paleo"
                           ])

if __name__ == "__main__":
    app.run(debug=True)
