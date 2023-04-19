from flask import render_template, redirect, request, session

from flask_app import app
from flask_app.models import message

@app.route("/send_message", methods=["POST"])
def send_message():
    print("request.form:", request.form)
    data = {
        "content": request.form["content"],
        "user_id": request.form["user_id"],
        "ride_id": request.form["ride_id"]
    }
    message.Message.save(data)
    return redirect(f"/rides/{ data['ride_id'] }")
