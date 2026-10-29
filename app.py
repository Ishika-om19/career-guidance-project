from flask import Flask,render_template, request, session, redirect, url_for
from dotenv import load_dotenv
from google import genai
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import date
import certifi
import bcrypt
import os
import time
import re

load_dotenv()

mongo_client = MongoClient(
    os.getenv("MONGO_URL"),
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=30000
)

mongo_client.admin.command("ping")
print("MongoDB connected successfully!")

db = mongo_client["career_guidance"]

users_collection = db["users"]

client = genai.Client()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        # Check whether email already exists
        existing_user = users_collection.find_one({"email": email})

        if existing_user:
            return "Email already registered!"

        # Hash password before storing it
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        # Save user in MongoDB
        users_collection.insert_one({
            "name": name,
            "email": email,
            "password": hashed_password
        })

        return "Registration successful!"

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        # Find user by email
        user = users_collection.find_one({"email": email})

        if not user:
            return "Invalid email or password!"

        # Check password
        if bcrypt.checkpw(
            password.encode("utf-8"),
            user["password"]
        ):
            session["user_id"] = str(user["_id"])
            session["user_name"] = user["name"]

            return redirect("/dashboard")

        return "Invalid email or password!"

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")
    print("USER NAME:",session.get("user_name"))
    return render_template(
        "dashboard.html",
        name=session["user_name"]
    )

@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect("/login")

    user = users_collection.find_one(
        {"_id": ObjectId(session["user_id"])}
    )

    return render_template(
        "profile.html",
        user=user
    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

@app.route("/daily-routine", methods=["GET", "POST"])
def daily_routine():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        # POST wala code
        time = request.form["time"]
        target = request.form["target"]
        duration = request.form["duration"]
        category = request.form["category"]
        routine_date = request.form["date"]

        routine_item = {
            "_id": ObjectId(),

            "date": routine_date,
            "time": time,
            "target": target,
            "duration": duration,
            "category": category,
            "completed": False
        }

        users_collection.update_one(
            {"_id": ObjectId(session["user_id"])},
            {"$push": {"daily_routine": routine_item}}
        )

        return redirect(url_for("daily_routine",date=routine_date)
                    )

    user = users_collection.find_one(
        {"_id": ObjectId(session["user_id"])}
    )

    routine = user.get("daily_routine", [])

    selected_date = request.args.get("date")
    if not selected_date:
        selected_date = date.today().isoformat()

    routine = [
        item for item in routine
        if item.get("date") == selected_date
    ]

    total_targets = len(routine)

    completed_targets = sum(
        1 for item in routine if item.get("completed", False)
    )

    if total_targets > 0:
        progress = int((completed_targets / total_targets) * 100)
    else:
        progress = 0

    return render_template(
        "daily_planner.html",
        name=session["user_name"],
        routine=routine,
        progress=progress,
        total_targets=total_targets,
        completed_targets=completed_targets,
        selected_date=selected_date
    )

@app.route("/complete-target", methods=["POST"])
def complete_target():

    if "user_id" not in session:
        return redirect("/login")

    target_id = request.form["target_id"]

    selected_date = request.form.get("selected_date")

    user_id = ObjectId(session["user_id"])

    user = users_collection.find_one({
        "_id": user_id
    })

    routine = user.get("daily_routine", [])

    for item in routine:

        if str(item["_id"]) == target_id:

            # Toggle completed status
            item["completed"] = not item.get("completed", False)

            break

    users_collection.update_one(
        {"_id": user_id},
        {"$set": {"daily_routine": routine}}
    )

    return redirect(
    url_for("daily_routine", date=selected_date)
)

@app.route("/delete-target", methods=["POST"])
def delete_target():

    if "user_id" not in session:
        return redirect("/login")

    target_id = request.form["target_id"]
    selected_date = request.form.get("selected_date")

    users_collection.update_one(
        {"_id": ObjectId(session["user_id"])},
        {
            "$pull": {
                "daily_routine": {
                    "_id": ObjectId(target_id)
                }
            }
        }
    )

    return redirect(
        url_for("daily_routine", date=selected_date)
    )

@app.route("/edit-target", methods=["GET", "POST"])
def edit_target():

    if "user_id" not in session:
        return redirect("/login")

    user_id = ObjectId(session["user_id"])

    if request.method == "POST":
        target_id = request.form["target_id"]
        selected_date = request.form.get("selected_date")
    else:
        target_id = request.args.get("target_id")
        selected_date = request.args.get("date")

    user = users_collection.find_one({
        "_id": user_id
    })

    if not user:
        return redirect("/login")

    routine = user.get("daily_routine", [])
    target = None

    for item in routine:
        if str(item["_id"]) == target_id:
            target = item
            break

    if not target:
        return "Target not found!", 404

    if request.method == "POST":

        target["time"] = request.form["time"]
        target["target"] = request.form["target"]
        target["duration"] = request.form["duration"]
        target["category"] = request.form["category"]

        users_collection.update_one(
            {"_id": user_id},
            {"$set": {"daily_routine": routine}}
        )

        return redirect(
            url_for("daily_routine", date=selected_date)
        )

    return render_template(
        "edit_target.html",
        target=target,
        selected_date=selected_date or target.get("date")
    )

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

@app.route("/daily-planner")
def daily_planner():
    return render_template("daily_planner.html")


if __name__ == "__main__":
    app.run(debug=True)