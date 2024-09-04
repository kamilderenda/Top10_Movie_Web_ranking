from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange
import requests

API_KEY = "a2e47788c725aaa8e050e260e2778073"
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
Bootstrap5(app)

# CREATE DB
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books-collection.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Movie(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    ranking: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    review: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

url = "https://api.themoviedb.org/3/search/movie?include_adult=false&language=en-US&page=1"
TMBD_URL="https://api.themoviedb.org/3/search/movie"
TMBD_BEARER="eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhMmU0Nzc4OGM3MjVhYWE4ZTA1MGUyNjBlMjc3ODA3MyIsIm5iZiI6MTcyNTQ2MzE5NS4yNDk2NTEsInN1YiI6IjY2ZDg3OTdiNDM1M2E1YzdiOTA5NmE1MCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.nGFeLUeOtR_nATX10YuVOuDY5zWmf_Dr_aRIMyqLVMU"
headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {TMBD_BEARER}"
}







# CREATE TABLE

class EditForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Done")

class AddForm(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")


@app.route("/")
def home():
    all_movies = db.session.query(Movie).all()
    return render_template("index.html", movies=all_movies)

@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = EditForm()
    movie_id = request.args.get('id')
    movie=db.get_or_404(Movie, movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=form)

@app.route("/delete")
def delete():
    movie_id = request.args.get('id')
    movie=db.get_or_404(Movie, movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddForm()
    if form.validate_on_submit():
        movie_title = form.title.data
        response = requests.get(TMBD_URL, headers=headers, params={"query": movie_title})
        data=response.json()["results"]
        return render_template("select.html", movies=data)
    return render_template("add.html", form=form)

@app.route("/select")
def select():
    movie_id = request.args.get('id')
    response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}", headers=headers)
    data = response.json()
    new_movie = Movie(
        title=data["title"],
        year=data["release_date"],
        description=data["overview"],
        rating=0,
        review="N/A",
        img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}"
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('edit', id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
