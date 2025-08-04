# Nutrition AI Agent Web Application

## 🚀 Overview
The Nutrition AI Agent is a personalized web application designed to generate meal plans using IBM Watsonx.ai's foundation models. Users can input their dietary goals, medical conditions, and food preferences to receive curated nutritional plans for 3 or 7 days.

---

## 🧠 Features
- ✅ AI-generated meal plans based on user inputs
- 📅 3-day plan with option to extend to 7 days
- 🖼️ Responsive UI with meal images
- 📊 Nutrition breakdown chart using Chart.js
- 🔒 Secure API key handling through environment variables
- 🌐 Modern dashboard interface with dropdowns and error handling

---

## 🔧 Tech Stack
- **Frontend**: HTML, CSS, Bootstrap, Jinja2
- **Backend**: Python (Flask), IBM Watsonx.ai (Granite model)
- **Visualization**: Chart.js
- **Version Control**: Git, GitHub

---

## 📁 Project Structure
```
├── app.py                  # Main Flask application
├── ibm_services.py         # IBM Watsonx model interaction
├── templates/
│   ├── index.html          # User input page
│   └── result.html         # Output dashboard
├── static/
│   ├── style.css           # Custom CSS
│   └── script.js           # Chart rendering logic
├── .env                    # API keys and project ID (not committed)
├── .gitignore              # Files to exclude from version control
└── README.md               # Project overview and documentation
```

---

## 📦 Setup Instructions
1. **Clone the repository**
```bash
git clone https://github.com/yourusername/NUTRITION-AGENT.git
cd NUTRITION-AGENT
```

2. **Create virtual environment and install dependencies**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

3. **Add your IBM Watsonx credentials to `.env` file**
```
WATSONX_APIKEY=your_ibm_api_key
WATSONX_URL=your_ibm_url
PROJECT_ID=your_project_id
```

4. **Run the application**
```bash
python app.py
```

---

## 📈 Future Enhancements
- Login system with user history
- Dietary restrictions & allergies filters
- Meal shopping list generation
- Integration with fitness trackers

---

## 📄 License
This project is licensed under the MIT License.

---

## 🤝 Contributions
Feel free to fork the repo and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

---

## 🙋‍♀️ Contact
For any queries, reach out via [GitHub Issues](https://github.com/sunidhi1dec/NUTRITION-AGENT/issues).

---

Built with ❤️ using IBM Watsonx and Flask.
