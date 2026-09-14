from flask import Flask,render_template, request
from dotenv import load_dotenv
from google import genai
import os
import time

load_dotenv()

client = genai.Client()

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/career-guidance", methods=["GET", "POST"])
def career_guidance():
    if request.method == "POST":
        name = request.form["name"]
        education = request.form["course"]
        year_semester = request.form["year_semester"]
        technologies = request.form.get("technologies","")
        interests =  request.form["interests"]
        subjects = request.form.get("subjects","")
        strengths = request.form.get("strengths","")
        career_preference = request.form.get("career_preference","")
        goal = request.form.get("goal","")
        additional_info = request.form.get("additional_info","")

        print(name)
        print(education)
        print(year_semester)
        print(technologies)
        print(interests)
        print(subjects)
        print(strengths)
        print(career_preference)
        print(goal)
        print(additional_info)
    prompt = f"""
    You are an AI career guidance counselor.

    Student Name: {name}
    Education: {education}
    Year Semester: {year_semester}
    Technologies: {technologies}
    Interests: {interests}
    Favorite Subjects: {subjects}
    Strengths: {strengths}
    Career Preference: {career_preference}
    Current Goal: {goal}
    Additional Info: {additional_info}

Based on this information, provide personalized career guidance.

Include:
1. Recommended career options
2. Why these careers are suitable 
3. Skills  the student should learn
4. A step-by-step career roadmap
5. If Project so, project Ideas
6. Short-term goals
7. Long-term goals

keep the guidance paractical,clear and suitable for a college student .
    """

    for attempt in range(3):
        try:
            interaction = client.interactions.create(
                model="gemini-3.8-flash",
                input=prompt
            )

            guidance = interaction.output_text
            break

        except Exception as e:
            print("Gemini attempt failed:", e)

            if attempt < 2:
                time.sleep(5)
            else:
                guidance = "Sorry, AI service is temporarily busy. Please try again agter some time."

    print(guidance)

    return render_template("index.html")

app.run(debug=True)