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
    print dir(session)

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
    flash('You were successfully logged in')

    session["login_info"] = (email, password)
    return redirect("/")

@app.route("/logout")
def log_out():
    """Logs the user out"""

    session.clear()

    flash("You've been logged out.")
    return redirect("/")

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