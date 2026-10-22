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

@app.route("/guidance/10th",methods=["GET", "POST"])
def guidance_10th():
    guidance = ""
    if request.method == "POST":
        name = request.form.get("name")
        subjects = request.form.get("subjects")
        interests = request.form.get("interests")
        strengths = request.form.get("strengths")
        career_interest = request.form.get("career_interest")

        prompt = f"""
You are an AI career guidance counselor for students who have passed 10th grade.

Student Name: {name}
Favorite Subjects: {subjects}
Interests: {interests}
Strengths: {strengths}
Career Interest: {career_interest}

Based on this information, provide personalized career guidance.

Include:
1. Suitable education streams after 10th
2. Suitable career options
3. Why these options may suit the student
4. Important subjects and skills to focus on
5. A simple roadmap for the next few years
6. Practical advice for the student

Keep the guidance clear, realistic and easy for a student to understand.
"""

        try:
            interaction = client.interactions.create(
                model="gemini-3.8-flash",
                input=prompt
            )

            guidance = interaction.output_text
            guidance = guidance.replace("###", "").replace("**", "")

        except Exception as e:
            print("Gemini attempt failed:", e)
            guidance = "Sorry, the AI service is temporarily unavailable. Please try again later."

    print(guidance)

    if request.method == "POST":
        return render_template("career_result.html", guidance=guidance)  
    return render_template("guidance_10th.html")

@app.route("/guidance/12th", methods=["GET", "POST"])
def guidance_12th():

    guidance = ""

    if request.method == "POST":

        name = request.form.get("name")
        stream = request.form.get("stream")
        interests = request.form.get("interests")
        strengths = request.form.get("strengths")
        career_goal = request.form.get("career_goal")

        prompt = f"""
You are an AI career guidance counselor for students who have completed 12th grade.

Student Name: {name}
12th Stream: {stream}
Interests: {interests}
Strengths: {strengths}
Career Goal: {career_goal}

Based on this information, provide personalized career guidance.

Include:

1. Suitable courses and degree options
2. Suitable career options
3. Why these careers may suit the student
4. Skills and subjects to focus on
5. A simple career roadmap
6. Practical advice for the student

Keep the guidance clear, realistic and easy to understand.
"""

        try:
            interaction = client.interactions.create(
                model="gemini-3.8-flash",
                input=prompt
            )

            guidance = interaction.output_text
            guidance = guidance.replace("###", "").replace("**", "")

        except Exception as e:
            print("Gemini attempt failed:", e)
            guidance = "Sorry, the AI service is temporarily unavailable. Please try again later."

    print(guidance)

    if request.method == "POST":
        return render_template("career_result.html", guidance=guidance, name=name)  
    return render_template("guidance_12th.html")

@app.route("/guidance/college",methods=["GET", "POST"])
def guidance_college():
    guidance = ""
    if request.method == "POST":
        name = request.form.get("name")
        course = request.form.get("course")
        year_semester = request.form.get("year_semester")
        skills = request.form.get("skills")
        interests = request.form.get("interests")
        subjects = request.form.get("subjects")
        strengths = request.form.get("strengths")
        career_preference = request.form.get("career_preference")
        goal = request.form.get("goal")

        prompt = f"""
You are an AI career guidance counselor for students who have passed 10th grade.

Student Name: {name}
Course: {course}
Year/Semester: {year_semester}
Skills: {skills}
Interests: {interests}
Favorite Subjects: {subjects}
Strengths: {strengths}
Career Preference: {career_preference}
Goal: {goal}

Based on this information, provide personalized career guidance.

Include:
1. Suitable Recommended career options
2. Skills and technologies to learn
3. Why these options may suit the student
4. Project & Practical Experience ideas to work on
5. A simple roadmap for the next few years and career opportunities & preparation
6. Practical advice for the student with respect to their current course and year/semester

Keep the guidance clear, realistic and easy for a student to understand.
"""

        try:
            interaction = client.interactions.create(
                model="gemini-3.8-flash",
                input=prompt
            )

            guidance = interaction.output_text
            guidance = guidance.replace("###", "").replace("**", "")

        except Exception as e:
            print("Gemini attempt failed:", e)
            guidance = "Sorry, the AI service is temporarily unavailable. Please try again later."

    print(guidance)

    if request.method == "POST":
        return render_template("career_result.html", guidance=guidance)  
    return render_template("guidance_college.html")

@app.route("/guidance/graduates",methods=["GET", "POST"])
def guidance_graduates():
    guidance = ""

    if request.method == "POST":

        name = request.form.get("name")
        qualification = request.form.get("qualification")
        skills = request.form.get("skills")
        interests = request.form.get("interests")
        strengths = request.form.get("strengths")
        career_preference = request.form.get("career_preference")
        goal = request.form.get("goal")
        additional_info = request.form.get("additional_info")

        prompt = f"""
You are an AI career guidance counselor for students who have completed 12th grade.

Student Name: {name}
Qualification: {qualification}
Skills: {skills}
Interests: {interests}
Strengths: {strengths}
Career Preference: {career_preference}
Goal: {goal}
Additional Information: {additional_info}

Based on this information, provide personalized career guidance.

Include:

1. personalized career options based on the student's qualification, skills, interests, and strengths
2. skills gap analysis and development recommendations
3. job, internship, and further industry opportunities based on the student's career preference and goal
4. projects, resume and interview preparation guidance
5. Why these careers may suit the student
6. personalized roadmap for the next few years and career opportunities & preparation

Keep the guidance clear, realistic and easy to understand.
"""

        try:
            interaction = client.interactions.create(
                model="gemini-3.8-flash",
                input=prompt
            )

            guidance = interaction.output_text
            guidance = guidance.replace("###", "").replace("**", "")

        except Exception as e:
            print("Gemini attempt failed:", e)
            guidance = "Sorry, the AI service is temporarily unavailable. Please try again later."

    print(guidance)

    if request.method == "POST":
        return render_template("career_result.html", guidance=guidance, name=name)  
    return render_template("guidance_graduates.html")

@app.route("/career-guidance", methods=["GET", "POST"])
def career_guidance():
    if request.method == "POST":

        education_level = request.form.get("education_level")
        name = request.form["name"]

        if education_level == "10th":

            favorite_subjects = request.form.get("favorite_subjects_10th", "")
            interests = request.form.get("interests_10th", "")
            strengths = request.form.get("strengths_10th", "")
            preferred_stream = request.form.get("preferred_stream", "")

            student_info = f"""
Education Level: 10th Passed
Favorite Subjects: {favorite_subjects or "Not provided"}
Interests: {interests or "Not provided"}
Strengths: {strengths or "Not provided"}
Preferred Stream: {preferred_stream or "Not provided"}
"""

        elif education_level == "12th":

            stream_12th = request.form.get("stream_12th", "")
            favorite_subjects = request.form.get("favorite_subjects_12th", "")
            interests = request.form.get("interests_12th", "")
            preferred_course = request.form.get("preferred_course", "")

            student_info = f"""
Education Level: 12th Passed
12th Stream: {stream_12th or "Not provided"}
Favorite Subjects: {favorite_subjects or "Not provided"}
Interests: {interests or "Not provided"}
Preferred Course: {preferred_course or "Not provided"}
"""

        elif education_level == "college":

            course_college = request.form.get("course_college", "")
            year_semester = request.form.get("year_semester", "")
            skills_college = request.form.get("skills_college", "")
            favorite_subjects = request.form.get("favorite_subjects_college", "")
            interests = request.form.get("interests_college", "")
            strengths = request.form.get("strengths_college", "")
            goal_college = request.form.get("goal_college", "")

            student_info = f"""
Education Level: College Student
Course: {course_college or "Not provided"}
Year/Semester: {year_semester or "Not provided"}
Technologies/Skills Known: {skills_college or "Not provided"}
Favorite Subjects: {favorite_subjects or "Not provided"}
Interests: {interests or "Not provided"}
Strengths: {strengths or "Not provided"}
Current Goal: {goal_college or "Not provided"}
"""

        elif education_level == "graduate":

            qualification = request.form.get("qualification", "")
            skills_graduate = request.form.get("skills_graduate", "")
            interests = request.form.get("interests_graduate", "")
            strengths = request.form.get("strengths_graduate", "")
            career_goal = request.form.get("career_goal_graduate", "")
            additional_info = request.form.get("additional_info", "")

            student_info = f"""
Education Level: Graduate
Qualification: {qualification or "Not provided"}
Skills: {skills_graduate or "Not provided"}
Interests: {interests or "Not provided"}
Strengths: {strengths or "Not provided"}
Career Goal: {career_goal or "Not provided"}
Additional Information: {additional_info or "Not provided"}
"""

        else:
            student_info = "Education level was not provided."

        prompt = f"""
You are an AI career guidance counselor.

Student Name: {name}

{student_info}

Based on the information provided, give personalized career guidance to {name}.

Important:
- Do not assume information that the student did not provide.
- Use only the information provided by the student.
- If optional information is missing, make recommendations using the information that is available.
- If the student is unsure about a career preference or goal, help them explore suitable options.
- Keep recommendations realistic for the student's current education level.
- Do not recommend careers only because they are popular.
- Explain why each recommendation matches the student's information.

Include:

1. Recommended Career Options
2. Why These Careers Suits You
3. Skills and Technologies to Learn
4. Career Roadmap
5. Project Ideas if Project exist otherwise skip this point
6. Short-Term goals
7. Medium-Term goals
8. Long-Term goals

Keep the guidance practical, clear, personalized and suitable for the student's education level.

Format the response with these headings exactly:

1. Recommended Career Options
2. Why These Careers Suits You
3. Skills and Technologies to Learn
4. Career Roadmap
5. Project Ideas
6. Short-Term goals
7. Medium-Term goals
8. Long-Term goals
"""

        guidance = ""

        for attempt in range(2):
            try:
                interaction = client.interactions.create(
                    model="gemini-3.8-flash",
                    input=prompt
                )

                guidance = interaction.output_text
                break

            except Exception as e:
                print("Gemini attempt failed:", e)

                if attempt < 1:
                    time.sleep(5)
                else:
                    guidance = "Sorry, AI service is temporarily busy. Please try again after some time."

        if "Sorry, AI service" not in guidance:
            guidance = guidance.replace("###", "").replace("**", "")

        sections = re.split(r'\n(?=\d+\.\s)', guidance)

        return render_template(
            "career_result.html",
            guidance=guidance,
            sections=sections,
            name=name
        )

    return render_template("index.html")


app.run(debug=True)