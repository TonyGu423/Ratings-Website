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

        session["login_info"] = (email, password)
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


@app.route("/signup", methods=["POST"])
def sign_up():
    """Inserts new user to DB"""

    email = request.form.get("email")
    age = int(request.form.get("age"))
    zipcode = request.form.get("zipcode")
    password = request.form.get("password")

    print email, age, zipcode, password

    return "%r, %r, %r, %r" % (email, age, zipcode, password)





@app.route("/users")
def user_list():
    """Show list of users"""

    users = User.query.all()
    return render_template("user_list.html", users=users)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()