"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

@app.route("/login")
def login_page():
    """Display login page"""

    return render_template("login.html")

@app.route("/login", methods=["POST"])
def logged_in():
    """Confirm that the user is logged in"""

    email = request.form.get("email")
    password = request.form.get("password")

    passcheck_query = User.query.filter_by(email=email, password=password).all()

    if (passcheck_query):
        flash('You were successfully logged in')

        user_id_tuple = db.session.query(User.user_id).filter_by(email=email).one()
        user_id = user_id_tuple[0]

        session["login_info"] = (email, password, user_id)
        print user_id
        return redirect("/")
    else:
        flash("Not in our database!")
        return render_template("signup.html")

@app.route("/logout")
def log_out():
    """Logs the user out"""

    session.clear()

    flash("You've been logged out.")
    return redirect("/")

@app.route("/signup", methods=["GET"])
def sign_up_page():
    """Display the signup page"""

    return render_template("signup.html")

@app.route("/signup", methods=["POST"])
def sign_up():
    """Inserts new user to DB"""

    email = request.form.get("email")
    age = int(request.form.get("age"))
    zipcode = request.form.get("zipcode")
    password = request.form.get("password")

    print email, age, zipcode, password
    new_user = User(email=email,
            age=age,
            zipcode=zipcode,
            password=password)
    db.session.add(new_user)
    db.session.commit()
    flash('New account created! Please log in.')

    return redirect("/login")


@app.route("/users")
def user_list():
    """Show list of users"""

    users = User.query.all()
    
    return render_template("user_list.html", users=users)


@app.route("/users/<int:id>")
def user_details(id):
    """Show specific details on a given user"""

    all_ratings = db.session.query(Movie.title, Rating.score).join(Rating)
    ratings = all_ratings.filter(Rating.user_id == id).all()

    user = User.query.get(id)

    return render_template("user_details.html", display_user=user, display_ratings=ratings)

@app.route("/movies")
def movie_list():
    """Show a list of all movies"""

    movies = Movie.query.order_by(Movie.title).all()

    movies_revised = []

    for movie in movies:
        movie_date_raw = movie.released_at
        movie_date = movie_date_raw.strftime("%b %d, %Y")

        movie_title_raw = movie.title

        if movie_title_raw[-5:] == ", The":
            movie_title = "The " + movie_title_raw[:-5]
        else:
            movie_title = movie.title


        movies_revised.append((movie.movie_id, movie_title, movie_date))

    return render_template("movie_list.html", movies=movies_revised)

@app.route("/movies/<int:movie_id>")
def movie_details(movie_id):
    """Show specific details on a given user"""

    all_ratings = db.session.query(User.user_id, Rating.score).join(Rating)
    ratings = all_ratings.filter(Rating.movie_id == movie_id).all()

    movie = Movie.query.get(movie_id)

    movie_title = movie.title
    movie_date_raw = movie.released_at
    movie_date = movie_date_raw.strftime("%b %d, %Y")

    if "login_info" in session.keys():
        user_id = session["login_info"][2]
    else:
        user_id = None

    if user_id:
        user_rating = Rating.query.filter_by(
            movie_id=movie_id, user_id=user_id).first()

    else:
        user_rating = None

    prediction = None
    if (not user_rating) and user_id:
        user = User.query.get(user_id)
        if user:
            prediction = user.predict_rating(movie)

    return render_template("movie_details.html",
                            movie_id=movie_id, 
                            movie_title=movie_title, 
                            movie_date=movie_date, 
                            ratings=ratings,
                            prediction=prediction)


@app.route("/rate/<int:id>", methods=["POST"])
def rate_movies(id):
    """Show page for rating films"""

    user_id = db.session.query(User.user_id).filter_by(email=session['login_info'][0]).one()[0]
    score = request.form.get("rating")
    movie_id = id

    rating = Rating(user_id=user_id, movie_id=movie_id, score=score)

    db.session.add(rating)
    db.session.commit()

    id_string = str(movie_id)

    return redirect("/movies/%s" %id_string)

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()



# THE USER IS: balloonicorn@unicorn.com
# THE PASSWORD: hackbright