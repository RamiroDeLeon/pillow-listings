import pytest

from types import SimpleNamespace
import random
import string

from flask_app.forms import SearchForm, MovieReviewForm
from flask_app.models import User, Review


def test_index(client):
    resp = client.get("/")
    assert resp.status_code == 200
    search = SimpleNamespace(search_query="guardians", submit="Search")
    form = SearchForm(formdata=None, obj=search)
    response = client.post("/", data=form.data, follow_redirects=True)
    assert b"Guardians of the Galaxy" in response.data


@pytest.mark.parametrize(("query", "message"), 
    (
        ("", b"This field is required"),
        ("ab", b"Too many results"), 
        ("1ciunech13cqwe", b"Movie not found"),
        ("a"*101, b"Field must be between 1 and 100 characters long.")
    )
) 
def test_search_input_validation(client, query, message):
    '''
    Test that with an empty query, you get the error "This field is required."
    Test that with a very short string, you get the error "Too many results"
    Test that with some gibberish (maybe a random string?) you get the error "Movie not found"
    Test that with a string that's too long, you get the error "Field must be between 1 and 100 characters long."
    '''
    search = SimpleNamespace(search_query=query, submit="Search")
    form = SearchForm(formdata=None, obj=search)
    response = client.post("/", data=form.data, follow_redirects=True)
    assert message in response.data


def test_movie_review(client, auth):
    '''
    - A beginning implementation is already provided to check 
    if the movie detail page for the 'Guardians of the Galaxy'
    page will show up. The choice of this id is arbitrary, and 
    you can change it to something else if you want.
    - Register and login. 
    - Submit a movie review with a randomly generated string 
    (to make sure that you're adding a truly unique review)
    - Test that the review shows up on the page
    - Test that the review is saved in the database
    '''
    guardians_id = "tt2015381"
    url = f"/movies/{guardians_id}"
    resp = client.get(url)
    assert resp.status_code == 200
    auth.register()
    auth.login()
    # CREATE FORM WITH OUR TEST REVIEW
    content = "!!!HERE-IS-MY-REVIEW-FOR-TESTING!!!"
    review = SimpleNamespace(text=content, submit="Enter Comment")
    form = MovieReviewForm(formdata=None, obj=review)
    resp = client.post(url, data=form.data, follow_redirects=True)
    # CHECK THAT content SHOWS UP IN HTML.
    assert str.encode(content) in resp.data
    # CHECK THAT REVIEW WITH content SHOWS UP IN DB.
    db_review = Review.objects(content=content).first()
    assert db_review is not None



@pytest.mark.parametrize(
    ("movie_id", "message"), 
    (
        ("", ""), 
        ("12345678", b"Incorrect IMDb ID"),
        ("123456789", b"Incorrect IMDb ID"), 
        ("1234567890", b"Incorrect IMDb ID")
    )
)
def test_movie_review_redirects(client, movie_id, message):
    '''
    - This test refers to navigating to movies at a certain /movies/<movie_id> url.
    - Test that with an empty movie_id, you get a status code of 404 and that you 
    see the custom 404 page.
    - Test that with (1) a movie_id shorter than 9 characters, (2) a movie_id exactly 
    9 characters (but an invalid id), and (3) a movie_id longer than 9 characters, the 
    request has a status code of 302 and the error message "Incorrect IMDb ID" is 
    displayed on the page you're redirected to.
    '''
    url = f"/movies/{movie_id}"
    url_resp = client.get(url)
    if movie_id == "":
        assert url_resp.status_code == 404
    else: 
        assert url_resp.status_code == 302
        resp = client.get("/")
        assert resp.status_code == 200
        assert message in resp.data


@pytest.mark.parametrize(
    ("comment", "message"), 
    (
        ("", b"This field is required"),
        ("abcd", b"Field must be between 5 and 500 characters long."),
        ("a"*501, b"Field must be between 5 and 500 characters long.")
    )
)
def test_movie_review_input_validation(client, auth, comment, message):
    '''
    - This test checks whether the proper validation errors from MovieReviewForm
    are raised when you provide incorrect input.
    - Test that with an empty string, you get the error "This field is required"
    - Test that with (1) a string shorter than 5 characters and (2) a string longer
    than 500 characters, you get the error "Field must be between 5 and 500 characters long."
    - Hint: 'a' * 10 == 'aaaaaaaaaa'
    - You can use any movie id here, just make sure it's valid or your test will fail.
    '''
    guardians_id = "tt2015381"
    url = f"/movies/{guardians_id}"
    resp = client.get(url)
    assert resp.status_code == 200
    auth.register()
    auth.login()
    review = SimpleNamespace(text=comment, submit="Enter Comment")
    form = MovieReviewForm(formdata=None, obj=review)
    resp = client.post(url, data=form.data, follow_redirects=True)
    # CHECK THAT content SHOWS UP IN HTML.
    assert message in resp.data
    # CHECK THAT REVIEW WITH content DOES NOT SHOW UP IN DB.
    db_review = Review.objects(content=comment).first()
    assert db_review is None

