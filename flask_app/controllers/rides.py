from flask import render_template, redirect, request, session
from flask_bcrypt import Bcrypt

from flask_app import app
from flask_app.models import ride

bcrypt = Bcrypt(app)


@app.route("/dashboard")
def get_dashboard():
    all_requests = ride.Ride.get_all_requests()
    all_booked_rides = ride.Ride.get_all_booked_rides()
    return render_template("dashboard.html", all_requests=all_requests, all_booked_rides=all_booked_rides)


@app.route("/rides/request")
def get_request_form():
    return render_template("request_form.html")


@app.route("/request_ride", methods=["POST"])
def request_ride():
    data = {
        "passenger_id": request.form["passenger_id"],
        "destination": request.form["destination"],
        "pickup_location": request.form["pickup_location"],
        "ride_date": request.form["ride_date"],
        "details": request.form["details"]
    }

    session["data"] = data
    if not ride.Ride.validate_ride(data):
        return redirect("/rides/request")
    session.pop("data")
    ride.Ride.request(data)
    return redirect("/dashboard")


@app.route("/requests/<int:request_id>/accept")
def accept_request(request_id):
    data = {
        "id": request_id,
        "driver_id": session["current_user"]["id"]
        }
    ride.Ride.accept_request(data)
    return redirect("/dashboard")


@app.route("/requests/<int:request_id>/delete")
def delete_request(request_id):
    data = {"id": request_id}
    ride.Ride.delete_request(data)
    return redirect("/dashboard")


@app.route("/rides/<int:ride_id>")
def get_booked_ride(ride_id):
    data = {"id": ride_id}
    current_ride = ride.Ride.get_one_booking(data)
    ride_messages = ride.Ride.get_one_ride_with_messages(data).messages
    return render_template("ride.html", ride=current_ride, ride_messages=ride_messages)


@app.route("/rides/<int:ride_id>/cancel")
def cancel_booking(ride_id):
    data = {"id": ride_id}
    ride.Ride.driver_cancel(data)
    return redirect("/dashboard")


@app.route("/rides/edit/<int:ride_id>")
def get_edit_form(ride_id):
    data = {"id": ride_id}
    current_ride = ride.Ride.get_one_booking(data)
    return render_template("ride_edit_form.html", ride=current_ride)


@app.route("/edit_ride", methods=["POST"])
def edit_booked_ride():
    data = {
        "id": request.form["ride_id"],
        "pickup_location": request.form["pickup_location"],
        "details": request.form["details"]
    }

    if not ride.Ride.validate_booking_edit(data):
        return redirect(f"/rides/edit/{data['id']}")
    ride.Ride.edit_booking(data)
    return redirect("/dashboard")


@app.route("/rides/delete/<int:ride_id>")
def delete_booking(ride_id):
    data = {"id": ride_id}
    ride.Ride.delete_booking(data)
    return redirect("/dashboard")
