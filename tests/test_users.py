from flask import session, request
import pytest

from types import SimpleNamespace

from flask_app.forms import RegistrationForm, UpdateUsernameForm
from flask_app.models import User

###########################################################################
###########################################################################
def test_register(client, auth):
    """ Test that registration page opens up """
    resp = client.get("/register")
    assert resp.status_code == 200
    response = auth.register()
    assert response.status_code == 200
    user = User.objects(username="test").first()
    assert user is not None

@pytest.mark.parametrize(
    ("username", "email", "password", "confirm", "message"),
    (
        ("test", "test@email.com", "test", "test", b"Username is taken"),
        ("p" * 41, "test@email.com", "test", "test", b"Field must be between 1 and 40"),
        ("username", "test", "test", "test", b"Invalid email address."),
        ("username", "test@email.com", "test", "test2", b"Field must be equal to"),
    ),
)
def test_register_validate_input(auth, username, email, password, confirm, message):
    if message == b"Username is taken":
        auth.register()
    response = auth.register(username, email, password, confirm)
    assert message in response.data
###########################################################################
###########################################################################
###########################################################################
###########################################################################
def test_login(client, auth):
    """ Test that login page opens up """
    resp = client.get("/login")
    assert resp.status_code == 200
    auth.register()
    response = auth.login()
    with client:
        client.get("/")
        assert session["_user_id"] == "test"

@pytest.mark.parametrize(("username", "password", "message"), 
    (
        ("", "", b"This field is required"),
        ("", "123", b"This field is required"),
        ("user1", "", b"This field is required"),
        ("user1", "password", b"Login failed. Check your username and/or password")
    )
)
def test_login_input_validation(auth, username, password, message):
    if username == "" or password == "":
        # LOGIN WITH AN EMPTY FOR EITHER OR BOTH OF THE INPUT FIELDS.
        login_resp = auth.login(username=username, password=password)
        assert message in login_resp.data
    else:
        # LOGIN WITH INCORRECT PASSWORD
        register_resp = auth.register(
            username=username, email="test@test.com", passwrd="test", confirm="test"
        )
        login_resp = auth.login(username=username, password=password)
        assert message in login_resp.data 
        # LOGIN WITH INCORRECT USERNAME
        register_resp = auth.register(
            username="test", email="test@test.com", passwrd=password, confirm="test"
        )
        login_resp = auth.login(username=username, password=password)
        assert message in login_resp.data
###########################################################################
###########################################################################
###########################################################################
###########################################################################
def test_logout(client, auth):
    '''
    Register, login, check that you successfully logged in, and then 
    logout, and check that you successfully logged out.
    '''
    resp = client.get("/login")
    assert resp.status_code == 200
    auth.register()
    response = auth.login()
    with client:
        client.get("/")
        assert session["_user_id"] == "test"
    logout_resp = auth.logout()
    assert logout_resp.status_code == 302
###########################################################################
###########################################################################
###########################################################################
###########################################################################
def test_change_username(client, auth):
    '''
    Test that the account page loads successfully and that you can 
    successfully change the username of the logged-in user.
    Test that the new username shows up on the account page
    Test that the new username change is reflected in the database
    '''
    resp = client.get("/login")
    assert resp.status_code == 200
    old_username, new_username = "test", "I CHANGED"
    # REGISTER A NEW USER
    register_resp = auth.register(
        username=old_username, email="test@test.com", passwrd="password", confirm="password"
    )
    # LOG IN BRAND NEW USER AND CHECK THAT LOGIN IS SUCCESSFUL.
    login_resp = auth.login(username=old_username, password="password")
    assert login_resp.status_code == 200
    resp = client.get("/account")
    assert resp.status_code == 200
    # CHECK THAT SESSION ID IS SET TO ORIGINAL USERNAME
    with client:
        client.get("/")
        assert session["_user_id"] == old_username
    # FILL IN FORM FOR USERNAME CHANGE
    change_name = SimpleNamespace(username=new_username, submit="Update Username")
    form = UpdateUsernameForm(formdata=None, obj=change_name)
    response = client.post("/account", data=form.data, follow_redirects=True)
    # FILLING OUT FOR REIDIRECTS BACK TO LOG IN PAGE, SO LOGIN W/ NEW CREDENTIALS.
    login_resp = auth.login(username=new_username, password="password")
    # CHECK THAT NEW LOGIN WORKED
    assert login_resp.status_code == 200
    # CHECK THAT SESSION ID CHANGES TO NEW USERNAME AFTER LOGING IN.
    with client:
        client.get("/")
        assert session["_user_id"] == new_username
    # CHECK THAT NEW USERNAME APPEARS IN ACCOUNT PAGE HTML.
    resp = client.get("/account")
    assert resp.status_code == 200
    assert str.encode(new_username) in resp.data
    # FINALLY, CHECK FOR NEW USERNAME IN DB.
    new_username_check = User.objects(username=new_username).first().username
    assert new_username == new_username_check
###########################################################################
###########################################################################
###########################################################################
###########################################################################
def test_change_username_taken(client, auth):
    '''
    Test that if we try to change the username to a different user's
    username, then we get the error message "That username is already taken"
    '''
    resp = client.get("/login")
    assert resp.status_code == 200
    # REGISTER 1ST USER.
    register_resp = auth.register(
        username="test", email="test@test.com", passwrd="password", confirm="password"
    )
    # REGISTER 2ND USER.
    register_resp = auth.register(
        username="test2", email="test2@test.com", passwrd="password", confirm="password"
    )
    # LOG IN 2ND USER AND CHECK THAT LOGIN IS SUCCESSFUL.
    login_resp = auth.login(username="test2", password="password")
    assert login_resp.status_code == 200
    resp = client.get("/account")
    assert resp.status_code == 200
    # CHECK THAT SESSION ID IS SET TO test2.
    with client:
        client.get("/")
        assert session["_user_id"] == "test2"
    # FILL IN FORM FOR USERNAME CHANGE ... IT SHOULD GIVE AN ERROR NOTIFICATION.
    change_name = SimpleNamespace(username="test", submit="Update Username")
    form = UpdateUsernameForm(formdata=None, obj=change_name)
    response = client.post("/account", data=form.data, follow_redirects=True)
    assert b"That username is already taken" in response.data


@pytest.mark.parametrize(
    ("new_username"), 
    (
        (""),
        ("a"*41)
    )
)
def test_change_username_input_validation(client, auth, new_username):
    '''
    Test that if we pass in an empty string, we get the error "This field is required."
    Test that if we pass in a string that's too long, we get the error "Field must be 
    between 1 and 40 characters long."
    '''
    # GET /login PAGE, REGISTER, LOGIN, SET SESSION 
    resp = client.get("/login")
    assert resp.status_code == 200
    auth.register()
    response = auth.login()
    with client:
        client.get("/")
        assert session["_user_id"] == "test"
    # FORM FOR CHANGING USERNAME
    change_name = SimpleNamespace(username=new_username, submit="Update Username")
    form = UpdateUsernameForm(formdata=None, obj=change_name)
    response = client.post("/account", data=form.data, follow_redirects=True)
    # USERNAME TOO SHORT.
    if new_username == "":
        assert b"This field is required" in response.data
    # USERNAME TOO LONG
    if len(new_username) > 40:
        assert b"Field must be between 1 and 40 characters long." in response.data
###########################################################################
###########################################################################