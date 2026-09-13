from flask import Flask,render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/career-guidance", methods=["GET", "POST"])
def career_guidance():
    if request.method == "POST":
        name = request.form["name"]
        education = request.form["education"]
        skills = request.form["skills"]
        interests =  request.form["interests"]
        subjects = request.form["subjects"]
        strengths = request.form["strengths"]
        career_preference = request.form["career_preference"]
        goal = request.form["goal"]

        print(name)
        print(education)
        print(skills)
        print(interests)
        print(subjects)
        print(strengths)
        print(career_preference)
        print(goal)

    return render_template("index.html")

app.run(debug=True)