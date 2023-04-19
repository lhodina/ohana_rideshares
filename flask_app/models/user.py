from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_bcrypt import Bcrypt
import re

from flask_app import app
bcrypt = Bcrypt(app)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PASSWORD_REGEX = re.compile(r'^(?=.*[A-Z])(?=.*\d)[a-zA-Z\d\-\#\$\.\%\&\*\@\!]{8,}$')

class User:
    DB = "ohana_rideshares"
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.rides = []

    @classmethod
    def save(cls, data):
        query = """
        INSERT INTO users (first_name, last_name, email, password)
        VALUES ( %(first_name)s, %(last_name)s, %(email)s, %(password)s )
        """
        return connectToMySQL(cls.DB).query_db(query, data)

    @classmethod
    def get_all(cls):
        query = "SELECT * FROM users;"
        users = connectToMySQL(cls.DB).query_db(query)
        all_users = []
        for user in users:
            all_users.append(cls(user))
        return all_users

    @classmethod
    def get_one(cls, user_id):
        query = "SELECT * FROM users WHERE id = %(id)s"
        data = { "id": user_id }
        return connectToMySQL(cls.DB).query_db(query, data)

    @classmethod
    def get_by_email(cls, user_email):
        query = "SELECT * FROM users WHERE email = %(email)s;"
        return connectToMySQL(cls.DB).query_db(query, user_email)

    @staticmethod
    def validate_user(user):
        is_valid = True
        if not user["first_name"]:
            flash("First name required")
            is_valid = False
        elif len(user["first_name"]) < 2:
            flash("First name must be at least two characters")
            is_valid = False
        if not user["last_name"]:
            flash("Last name required")
            is_valid = False
        elif len(user["last_name"]) < 2:
            flash("Last name must be at least two characters")
            is_valid = False
        if not user["email"]:
            flash("Email required")
            is_valid = False
        elif not EMAIL_REGEX.match(user["email"]):
            flash("Invalid email address")
            is_valid = False
        query = "SELECT * FROM users WHERE email = %(email)s;"
        data = {"email": user["email"]}
        res = connectToMySQL("ohana_rideshares").query_db(query, data)
        if res:
            flash("Email already in use")
            is_valid = False
        if not user["password"]:
            flash("Password required")
        elif user["password"] != user["confirm_password"]:
            flash("Passwords do not match")
            is_valid = False
        elif not PASSWORD_REGEX.match(user["password"]):
            flash("Invalid password")
            is_valid = False
        return is_valid


    @staticmethod
    def validate_login(data):
        is_valid = True
        if not data["email"]:
            flash("Email Required")
            is_valid = False
        elif not EMAIL_REGEX.match(data["email"]):
            flash("Invalid email format")
            is_valid = False
        else:
            query = "SELECT * FROM users WHERE email = %(email)s;"
            result = connectToMySQL("ohana_rideshares").query_db(query, {"email": data["email"]})
            current_user = None
            if not result:
                flash("Email not found")
                is_valid = False
            else:
                current_user = result[0]
            if current_user and not bcrypt.check_password_hash(current_user["password"], data["password"]):
                flash("Invalid password")
                is_valid = False
        if not data["password"]:
            flash("Password required")
            is_valid = False
        return is_valid
