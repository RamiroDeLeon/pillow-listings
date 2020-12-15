from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from wtforms import(
    StringField,
    IntegerField,
    SubmitField,
    TextAreaField,
    PasswordField,
    SelectField,
    TextAreaField
)
from wtforms.validators import (
    InputRequired,
    DataRequired,
    NumberRange,
    Length,
    Email,
    EqualTo,
    ValidationError,
)


from .models import User


class SearchForm(FlaskForm):
    search_query = StringField(
        "Query", validators=[InputRequired(), Length(min=1, max=100)]
    )
    submit = SubmitField("Search")


class MovieReviewForm(FlaskForm):
    text = TextAreaField(
        "Comment", validators=[InputRequired(), Length(min=5, max=500)]
    )
    submit = SubmitField("Enter Comment")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user is not None:
            raise ValidationError("Username is taken")

    def validate_email(self, email):
        user = User.objects(email=email.data).first()
        if user is not None:
            raise ValidationError("Email is taken")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")


class UpdateUsernameForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    submit = SubmitField("Update Username")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.objects(username=username.data).first()
            if user is not None:
                raise ValidationError("That username is already taken")


class PostItemForm(FlaskForm):
    roomOptions = ["0 (Studio)+", "1+", "2+", "3+", "4+", "5+"]
    restroomOptions = ["1+", "2+", "3+", "4+", "5+"]
    typeOptions = ["Home", "Apartment", "Condo", "Townhome"]
    price = StringField("Price (in USD):", validators=[InputRequired()])
    rooms = SelectField("Number of rooms:", choices=roomOptions)
    restrooms = SelectField("Number of bathrooms:", choices=restroomOptions)
    propertyType = SelectField("Property type:", choices=typeOptions)
    description = TextAreaField("Describe your lising:", validators=[InputRequired(), Length(min=1, max=1000)])
    submit = SubmitField("Publish your listing")

    def validate_price(self, price):
        return True


class UpdateProfilePicForm(FlaskForm):
    photo = FileField(
        "New profile picture", 
        validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png'], 'Images Only!')]
    )
    submit = SubmitField("Update profile picture")