from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_bootstrap import Bootstrap5
import requests
from forms import EditForm, AddMovie
from found_movie import FoundMovie
import os


MOVIE_API_KEY = os.environ['MOVIE_API_KEY']

headers = {
            "accept": "application/json",
            "Authorization": f"{os.environ['AUTH_THEMOVIE_DB']}"
        }
app = Flask(__name__)
Bootstrap5(app)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///top_movies.db'


# CREATE DB
class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CREATE TABLE

class Movie(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    rating: Mapped[float] = mapped_column(Float)
    ranking: Mapped[float] = mapped_column(Float)
    review: Mapped[str] = mapped_column(String(500))
    img_url: Mapped[str] = mapped_column(String(150), nullable=False)


@app.route("/")
def home():
    result = db.session.execute(db.select(Movie).order_by(-Movie.rating))
    all_movies = result.scalars().all()
    for i, movie in enumerate(all_movies, 1):
        movie.ranking = i
    return render_template("index.html", movies=all_movies)


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    form = EditForm()

    result = db.session.execute(db.select(Movie).where(Movie.id == id))
    movie_to_change = result.scalar()
    if form.validate_on_submit():
        movie_to_change.rating = form.new_rating.data
        movie_to_change.review = form.new_review.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", form=form, movie=movie_to_change)


@app.route("/delete")
def delete():
    book_d = request.args.get("id")

    result = db.session.execute(db.select(Movie).where(Movie.id == book_d))
    book_to_delete = result.scalar()
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/add", methods=["GET", "POST"])
def select_movie():
    form = AddMovie()
    if form.validate_on_submit():
        title = form.title.data
        params = {
            "query": title
        }
        url = "https://api.themoviedb.org/3/search/movie"

        response = requests.get(url, params=params, headers=headers)
        all_movies = response.json().get("results")
        result_movies = [FoundMovie(movie["original_title"], movie["release_date"], movie["id"]) for movie in all_movies]
        return render_template('select.html', movies=result_movies)
    return render_template("add.html", form=form)


@app.route("/select")
def add_movie():
    movie_id = request.args.get("id")

    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    movie_to_add = requests.get(url, headers=headers).json()
    print(movie_to_add)
    title = movie_to_add["original_title"]
    img_url = movie_to_add["poster_path"]
    year = int(movie_to_add["release_date"][:4])
    description = movie_to_add["overview"]

    new_movie = Movie(title=title, year=year, description=description, img_url=img_url, rating=4, ranking=0, review="g")
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for("edit", id=new_movie.id))





if __name__ == '__main__':
    app.run(debug=True)
