from flask import render_template, redirect, request, session
from flask_bcrypt import Bcrypt

from flask_app import app
from flask_app.models import user

bcrypt = Bcrypt(app)

# Get both forms on the home page
@app.route("/")
def get_forms():
    return render_template("index.html")

# No need to pass in IDs through the route -- just use a form input
@app.route("/register", methods=["POST"])
def register_user():
    data = {
        "first_name": request.form["first_name"],
        "last_name": request.form["last_name"],
        "email": request.form["email"],
        "password": request.form["password"],
        "confirm_password": request.form["confirm_password"]
    }

    # Add data to session before form submit, in case there are validation errors and you want to persist input fields
    session["registering"] = True
    session["data"] = data
    if not user.User.validate_user(data):
        return redirect("/")
    # If you made it this far, congratulations -- remove all form input data
    session.clear()
    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    data["password"] = pw_hash
    user_id = user.User.save(data)
    # Get user by id and save to session to keep the user logged in
    current_user = user.User.get_one(user_id)[0]
    session["current_user"] = current_user
    return redirect("/dashboard")


@app.route("/login", methods=["POST"])
def login():
    data = {
        "email": request.form["email"],
        "password": request.form["password"]
    }

    session["data"] = data
    if not user.User.validate_login(data):
        return redirect("/")
    session.clear()
    current_user = user.User.get_by_email({"email": data["email"]})[0]
    session["current_user"] = current_user
    return redirect("/dashboard")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
