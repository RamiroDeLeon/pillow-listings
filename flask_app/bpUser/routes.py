import io
import base64
from flask import Blueprint, redirect, url_for, render_template, flash, request
from flask_login import current_user, login_required, login_user, logout_user
from .. import bcrypt
from werkzeug.utils import secure_filename
from ..models import User, Item
from ..utils import current_time
from ..forms import(
    RegistrationForm,
    LoginForm,
    UpdateUsernameForm,
    UpdateProfilePicForm,
    PostItemForm
)

bpUser = Blueprint("bpUser", __name__)

""" ************ User Management views ************ """


@bpUser.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("bpItem.index"))    #maybe diff? SADAS

    form = RegistrationForm() 
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed)
        user.save()
        return redirect(url_for("bpUser.login"))

    return render_template("register.html", title="Register", form=form)


@bpUser.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("bpItem.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(username=form.username.data).first()

        if user is not None and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("bpUser.account", username=current_user.username))
        else:
            flash("Login failed. Check your username and/or password")
            return redirect(url_for("bpUser.login"))

    return render_template("login.html", title="Login", form=form)


@bpUser.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("bpItem.index"))


@bpUser.route("/account/<username>", methods=["GET", "POST"])
@login_required
def account(username):
    if current_user.is_authenticated:
        print("user auth true")
        updateUsernameForm = UpdateUsernameForm()
        postItemForm = PostItemForm()
        updatePhotoForm = UpdateProfilePicForm()
        if request.method == "POST":
            print("hit post method")
            submitter = request.form['submit']
            if submitter == "Update Username":          #USERNAME UPDATE FORM
                if updateUsernameForm.submit.data:
                    if updateUsernameForm.validate_on_submit():
                        newUsername = updateUsernameForm.username.data
                        current_user.modify(username=newUsername)
                        current_user.save()
                        return redirect(url_for("bpUser  .logout"))
            if submitter == "Publish your listing":     #POSTING A PROPERTY FORM
                if postItemForm.submit.data:
                    if postItemForm.validate_on_submit():
                        item = Item(
                            poster=current_user._get_current_object(),
                            price=postItemForm.price.data,
                            rooms=postItemForm.rooms.data,
                            restrooms=postItemForm.restrooms.data,
                            propertyType=postItemForm.propertyType.data,
                            description=postItemForm.description.data,
                            date=current_time()
                        )
                        item.save()
                        return redirect(url_for("bpItem.index"))
            if submitter == 'Update profile picture':       # CHECKING FOR PRO-PIC UPDATE FORM
                print("submitter:", submitter)
                if updatePhotoForm.submit.data:
                    print("photo form data:", updatePhotoForm.submit.data)
                    if updatePhotoForm.validate_on_submit():
                        print("photo form validated")
                        img = updatePhotoForm.photo.data
                        print("img: ", img)
                        filename = secure_filename(img.filename)
                        print("filename:", filename)
                        contentType = f'images/{filename[-3:]}'
                        print("contentType: ", contentType, filename[-3:], img)
                        print(".get(): ", current_user.profilePic.get())
                        if current_user.profilePic.get() is None:
                            print("current_user.profilePic.get() is none")
                            current_user.profilePic.replace(img.stream, contentType=contentType)
                            print("after ")
                        else:
                            print("current_user.profilePic.get() was not None")
                            current_user.profilePic.replace(img.stream, contentType=contentType)
                        current_user.save()
        print("gonna hit final render")
        return render_template(
            "account.html",
            title="Account",
            updateUsernameForm=updateUsernameForm,
            updatePhotoForm=updatePhotoForm,
            image=get_b64_img(current_user.username),
            postItemForm=postItemForm
        )

  

def get_b64_img(username):
    user = User.objects(username=username).first()
    bytes_im = io.BytesIO(user.profilePic.read())
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return image