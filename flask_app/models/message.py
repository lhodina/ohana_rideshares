from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash

from flask_app import app
from flask_app.models import ride, user

class Message:
    DB = "ohana_rideshares"
    def __init__(self, data):
        self.id = data['id']
        self.content = data['content']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.sender = None

    @classmethod
    def save(cls, data):
        query = """
        INSERT INTO messages(content, user_id, ride_id)
        VALUES ( %(content)s, %(user_id)s, %(ride_id)s );
        """
        return connectToMySQL(cls.DB).query_db(query, data)
