from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash

from flask_app import app
from flask_app.models import user, message

class Ride:
    DB = "ohana_rideshares"
    def __init__(self, data):
        self.id = data['id']
        self.destination = data['destination']
        self.pickup_location = data['pickup_location']
        self.ride_date = data['ride_date']
        self.details = data['details']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.passenger = None
        self.driver = None
        self.messages = []

    @classmethod
    def request(cls, data):
        query = """
        INSERT INTO rides(destination, pickup_location, ride_date, details, passenger_id)
        VALUES ( %(destination)s, %(pickup_location)s, %(ride_date)s, %(details)s, %(passenger_id)s );
        """
        return connectToMySQL(cls.DB).query_db(query, data)

    @classmethod
    def get_all_requests(cls):
        query = """
        SELECT * FROM rides
        JOIN users ON rides.passenger_id = users.id
        WHERE driver_id IS NULL;
        """
        results = connectToMySQL(cls.DB).query_db(query)
        all_requests = []
        for row in results:
            current_request = cls(row)
            current_request_passenger_data = {
                "id": row["users.id"],
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "email": row["email"],
                "password": row["password"],
                "created_at": row["users.created_at"],
                "updated_at": row["users.updated_at"]
            }
            passenger = user.User(current_request_passenger_data)
            current_request.passenger = passenger
            all_requests.append(current_request)
        return all_requests

    @classmethod
    def accept_request(cls, data):
        query = """
        UPDATE rides
        SET driver_id=%(driver_id)s
        WHERE id = %(id)s;
        """
        return connectToMySQL(cls.DB).query_db(query, data)

    @classmethod
    def delete_request(cls, data):
        query = "DELETE FROM rides WHERE id = %(id)s;"
        return connectToMySQL(cls.DB).query_db(query, data)

    @classmethod
    def get_all_booked_rides(cls):
        query = """
        SELECT * FROM rides
        JOIN users passengers ON rides.passenger_id = passengers.id
        JOIN users drivers ON rides.driver_id = drivers.id;
        """
        results = connectToMySQL(cls.DB).query_db(query)

        all_booked_rides = []
        for row in results:
            current_booking = cls(row)
            current_booking_passenger_data = {
                "id": row["passengers.id"],
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "email": row["email"],
                "password": row["password"],
                "created_at": row["passengers.created_at"],
                "updated_at": row["passengers.updated_at"]
            }
            passenger = user.User(current_booking_passenger_data)
            current_booking.passenger = passenger

            current_booking_driver_data = {
                "id": row["drivers.id"],
                "first_name": row["drivers.first_name"],
                "last_name": row["drivers.last_name"],
                "email": row["drivers.email"],
                "password": row["drivers.password"],
                "created_at": row["drivers.created_at"],
                "updated_at": row["drivers.updated_at"]
            }
            driver = user.User(current_booking_driver_data)
            current_booking.driver = driver

            all_booked_rides.append(current_booking)
        return all_booked_rides

    @classmethod
    def get_one_booking(cls, data):
        query = """
        SELECT * FROM rides
        JOIN users passengers ON rides.passenger_id = passengers.id
        JOIN users drivers ON rides.driver_id = drivers.id
        WHERE rides.id = %(id)s;
        """
        result = connectToMySQL(cls.DB).query_db(query, data)[0]
        current_booking = cls(result)
        current_booking_passenger_data = {
                "id": result["passengers.id"],
                "first_name": result["first_name"],
                "last_name": result["last_name"],
                "email": result["email"],
                "password": result["password"],
                "created_at": result["passengers.created_at"],
                "updated_at": result["passengers.updated_at"]
            }
        passenger = user.User(current_booking_passenger_data)
        current_booking.passenger = passenger

        current_booking_driver_data = {
            "id": result["drivers.id"],
            "first_name": result["drivers.first_name"],
            "last_name": result["drivers.last_name"],
            "email": result["drivers.email"],
            "password": result["drivers.password"],
            "created_at": result["drivers.created_at"],
            "updated_at": result["drivers.updated_at"]
        }
        driver = user.User(current_booking_driver_data)
        current_booking.driver = driver
        return current_booking

    @classmethod
    def get_one_ride_with_messages(cls, data):
        query = """
        SELECT * FROM rides
        LEFT JOIN messages ON rides.id = messages.ride_id
        LEFT JOIN users ON messages.user_id = users.id
        WHERE rides.id = %(id)s;
        """
        results = connectToMySQL(cls.DB).query_db(query, data)
        ride = cls(results[0])
        for row in results:
            message_data = {
                "id": row["messages.id"],
                "content": row["content"],
                "created_at": row["messages.created_at"],
                "updated_at": row["messages.updated_at"],
                "user_id": row["user_id"],
                "ride_id": row["ride_id"],
            }

            current_message = message.Message(message_data)

            sender_data = {
                "id": row["users.id"],
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "email": row["email"],
                "password": row["password"],
                "created_at": row["users.created_at"],
                "updated_at": row["users.updated_at"]
            }

            current_user = user.User(sender_data)
            current_message.sender = current_user

            ride.messages.append(current_message)
        return ride

    @classmethod
    def edit_booking(cls, data):
        query = """
        UPDATE rides
        SET pickup_location = %(pickup_location)s,
        details = %(details)s
        WHERE id = %(id)s;
        """
        return connectToMySQL(cls.DB).query_db(query, data)

    @classmethod
    def driver_cancel(cls, data):
        query = """
        UPDATE rides
        SET driver_id = Null
        WHERE id = %(id)s;
        """
        return connectToMySQL(cls.DB).query_db(query, data)

    @classmethod
    def delete_booking(cls, data):
        query = "DELETE FROM rides WHERE id = %(id)s;"
        return connectToMySQL(cls.DB).query_db(query, data)

    @staticmethod
    def validate_ride(ride):
        is_valid = True
        if not ride["destination"]:
            flash("Destination required")
            is_valid = False
        elif len(ride["destination"]) < 3:
            flash("Destination must be at least three characters")
            is_valid = False
        if not ride["pickup_location"]:
            flash("Pickup location required")
            is_valid = False
        elif len(ride["pickup_location"]) < 3:
            flash("Pickup location must be at least three characters")
            is_valid = False
        if not ride["ride_date"]:
            flash("Ride date required")
            is_valid = False
        if not ride["details"]:
            flash("Details required")
            is_valid = False
        elif len(ride["details"]) < 10:
            flash("Details must be at least 10 characters")
            is_valid = False
        return is_valid

    @staticmethod
    def validate_booking_edit(booking_edit):
        is_valid = True
        if not booking_edit["pickup_location"]:
            flash("Pickup location required")
            is_valid = False
        elif len(booking_edit["pickup_location"]) < 3:
            flash("Pickup location must be at least three characters")
            is_valid = False
        if not booking_edit["details"]:
            flash("Details required")
            is_valid = False
        elif len(booking_edit["details"]) < 10:
            flash("Details must be at least 10 characters")
            is_valid = False
        return is_valid
