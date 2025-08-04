from flask import Flask, render_template, request, make_response, session
from ibm_services import generate_meal_plan
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'


def create_meal_plan_pdf(meal_plan, goals, conditions, preferences, days):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#2c3e50'),
        alignment=1
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#34495e')
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )

    story = []


    story.append(Paragraph("AI Generated Meal Plan", title_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Plan Details", heading_style))
    details_data = [
        ['Goals:', goals],
        ['Conditions:', conditions],
        ['Preferences:', preferences],
        ['Duration:', f"{days} days"]
    ]

    details_table = Table(details_data, colWidths=[1.5 * inch, 4 * inch])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    story.append(details_table)
    story.append(Spacer(1, 20))

    for i, day in enumerate(meal_plan.get('days', []), 1):
        story.append(Paragraph(f"Day {i}", heading_style))

        meal_data = [['Meal Type', 'Item', 'Calories', 'Protein', 'Carbs', 'Fat', 'Why']]

        for meal in day.get('meals', []):
            macros = meal.get('macros', {})
            meal_data.append([
                meal.get('type', 'N/A'),
                meal.get('item', 'N/A'),
                str(meal.get('calories', 'N/A')),
                f"{macros.get('protein', 'N/A')}g",
                f"{macros.get('carbs', 'N/A')}g",
                f"{macros.get('fat', 'N/A')}g",
                meal.get('why', 'N/A')[:50] + '...' if len(meal.get('why', '')) > 50 else meal.get('why', 'N/A')
            ])

        meal_table = Table(meal_data,
                           colWidths=[0.8 * inch, 1.5 * inch, 0.6 * inch, 0.6 * inch, 0.6 * inch, 0.6 * inch, 2 * inch])
        meal_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        story.append(meal_table)
        story.append(Spacer(1, 15))

    doc.build(story)
    buffer.seek(0)
    return buffer


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        goals = request.form.get("goals", "")
        conditions = request.form.get("conditions", "")
        preferences = request.form.get("preferences", "")
        days = int(request.form.get("days", 3))

        try:
            meal_plan = generate_meal_plan(goals, conditions, preferences, days)

            session['current_meal_plan'] = {
                'meal_plan': meal_plan,
                'goals': goals,
                'conditions': conditions,
                'preferences': preferences,
                'days': days
            }

            return render_template("result.html",
                                   meal_plan=meal_plan,
                                   goals=goals,
                                   conditions=conditions,
                                   preferences=preferences,
                                   days=days)
        except Exception as e:
            fallback_meal_plan = {
                "days": []
            }
            return render_template("result.html",
                                   error="Error generating meal plan",
                                   meal_plan=fallback_meal_plan,
                                   raw_output_debug=str(e))

    return render_template("index.html",
                           preference_options=[
                               "Vegetarian", "Non Vegetarian", "Vegan", "Keto", "Paleo"
                           ])


@app.route("/download_pdf", methods=["POST", "GET"])
def download_pdf():
    try:
        if 'current_meal_plan' in session:
            data = session['current_meal_plan']
            meal_plan = data['meal_plan']
            goals = data['goals']
            conditions = data['conditions']
            preferences = data['preferences']
            days = data['days']
        else:
            meal_plan_json = request.form.get("meal_plan")
            goals = request.form.get("goals", "")
            conditions = request.form.get("conditions", "")
            preferences = request.form.get("preferences", "")
            days = int(request.form.get("days", 3))

            print(f"Received meal_plan_json: {meal_plan_json}")

            try:
                meal_plan = json.loads(meal_plan_json)
            except json.JSONDecodeError as json_error:
                print(f"JSON decode error: {json_error}")
                if meal_plan_json:
                    import html
                    cleaned_json = html.unescape(meal_plan_json)
                    try:
                        meal_plan = json.loads(cleaned_json)
                    except:
                        meal_plan = {
                            "days": [
                                {
                                    "day": "Day 1",
                                    "meals": [
                                        {
                                            "type": "Breakfast",
                                            "item": "Sample Meal",
                                            "why": "Error occurred while parsing meal plan",
                                            "calories": 0,
                                            "macros": {"protein": 0, "carbs": 0, "fat": 0}
                                        }
                                    ]
                                }
                            ]
                        }
                else:
                    raise Exception("No meal plan data received and no session data available")


        pdf_buffer = create_meal_plan_pdf(meal_plan, goals, conditions, preferences, days)

        response = make_response(pdf_buffer.read())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=meal_plan.pdf'

        return response

    except Exception as e:
        print(f"PDF generation error: {str(e)}")
        return f"Error generating PDF: {str(e)}", 500


if __name__ == "__main__":
    app.run(debug=True)
