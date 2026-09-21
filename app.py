from flask import Flask,render_template, request
from dotenv import load_dotenv
from google import genai
import os
import time
import re

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
        course = request.form["course"]
        year_semester = request.form["year_semester"]
        technologies = request.form.get("technologies","")
        interests =  request.form["interests"]
        subjects = request.form.get("subjects","")
        strengths = request.form.get("strengths","")
        career_preference = request.form.get("career_preference","")
        goal = request.form.get("goal","")
        additional_info = request.form.get("additional_info","")

        print(name)
        print(course)
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
Course: {course}
Year/Semester: {year_semester}
Technologies/Tools Known: {technologies or "Not provided"}
Interests: {interests or "Not provided"}
Favorite Subjects: {subjects or "Not provided"}
Strengths: {strengths or "Not provided"}
Career Preference: {career_preference or "Not provided"}
Current Goal: {goal or "Not provided"}
Additional Information: {additional_info or "Not provided"}

Based on the information provided, give personalized career guidance to {name}.

Important:
- Do not assume information that the student did not provide.
- Use the student's course, year/semester, skills, interests and other available information.
- If optional information is missing, make recommendations using the information that is available.
- If the student is unsure about a career preference or goal, help them explore suitable options.
- Keep recommendations realistic for the student's current academic level.

Include:

1. Recommended career options
2. Why each career is suitable
3. Skills and technologies to learn
4. Step-by-step career roadmap
5. Suitable project ideas
6. Short-term goals (0-6 months)
7. Medium-term goals (6-18 months)
8. Long-term goals (18+ months)


Keep the guidance practical, clear, personalized and suitable for the student's current course and year/semester.

Format the response with clear heading and bullet point. Use these headings exactly:
1. Recommended Career Options 
2. Why These Careers Suits You 
3. Skills and Technologies to Learn
4. Career Roadmap
5. Project Ideas if Project exist other wise skip this point
6. Short-Term goals
7. Long-Term goals

"""

    for attempt in range(3):
        try:
            interaction = client.interactions.create(
                model="gemini-3.7-flash",
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

    guidance = guidance.replace("###", "").replace("**", "")
    sections = re.split(r'\n(?=\d+\.\s)', guidance)

    return render_template("career_result.html", sections=sections,name=name)

    return render_template("index.html")

app.run(debug=True)