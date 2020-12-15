from flask_login import UserMixin
from datetime import datetime
from . import db, login_manager
from . import config
from .utils import current_time
import base64


@login_manager.user_loader
def load_user(user_id):
    return User.objects(username=user_id).first()


class User(db.Document, UserMixin):
    username = db.StringField(
        unique=True, 
        required=True,
        min_length=1,
        max_length=40
    )
    email = db.EmailField(
        required=True,
        unique=True
    )
    password = db.StringField(
        required=True
    )
    profilePic = db.ImageField()
    # Returns unique string identifying our object
    def get_id(self):
        return self.username


class Review(db.Document):
    commenter = db.ReferenceField(User, required=True)
    content = db.StringField(required=True, min_length=5, max_length=500)
    date = db.StringField(required=True)
    imdb_id = db.StringField(required=True, min_length=9, max_length=9)
    movie_title = db.StringField(required=True, min_length=1, max_length=100)

class Item(db.Document):
    poster = db.ReferenceField(User, required=True)
    price = db.StringField(required=True)
    rooms = db.StringField(required=True)
    restrooms = db.StringField(required=True)
    propertyType = db.StringField(required=True)
    description = db.StringField(required=True, min_length=5, max_length=1000)
    date = db.StringField(required=True)
    # id could be ObjectId()