import io
import base64
from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user

# from .. import movie_client
from ..forms import MovieReviewForm, SearchForm
from ..models import User, Review, Item
from ..utils import current_time

bpItem = Blueprint("bpItem", __name__)


""" ************ View functions ************ """


@bpItem.route("/", methods=["GET", "POST"])
def index():
    print("in bpItem.index() request was:", request.method)
    # searchForm = SearchForm()
    userLst = User.objects()
    reviewLst = Review.objects()
    itemLst = Item.objects()
    # if searchForm.validate_on_submit():
    #     return redirect(
    #         url_for("movies.query_results", query=searchForm.search_query.data)
    #     )

    return render_template(
        "index.html",
        userLst=userLst,
        reviewLst=reviewLst,
        itemLst=itemLst
    )


# @movies.route("/search-results/<query>", methods=["GET"])
# def query_results(query):
#     try:
#         results = movie_client.search(query)
#     except ValueError as e:
#         flash(str(e))
#         return redirect(url_for("movies.index"))    #maybe diff ?

#     return render_template("query.html", results=results)

 
# @movies.route("/movies/<movie_id>", methods=["GET", "POST"])
# def movie_detail(movie_id):
#     try:
#         result = movie_client.retrieve_movie_by_id(movie_id)
#     except ValueError as e:
#         flash(str(e))
#         return redirect(url_for("users.login"))
#     form = MovieReviewForm()
#     if form.validate_on_submit() and current_user.is_authenticated:
#         review = Review(
#             commenter=current_user._get_current_object(),
#             content=form.text.data,
#             date=current_time(),
#             imdb_id=movie_id,
#             movie_title=result.title,
#         )
#         review.save()
#         return redirect(request.path)
#     reviews = Review.objects(imdb_id=movie_id)
#     return render_template(
#         "movie_detail.html", form=form, movie=result, reviews=reviews
#     )


@bpItem.route("/user/<username>")
def user_detail(username):
    poster = User.objects(username=username).first()
    itemLst = Item.objects(poster=poster)
    img= User.objects(username=username).first()
    return render_template(
        "user_detail.html",
        username=username,
        image=get_b64_img(username),
        itemLst=itemLst
    )


def get_b64_img(username):
    user = User.objects(username=username).first()
    bytes_im = io.BytesIO(user.profilePic.read())
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return image