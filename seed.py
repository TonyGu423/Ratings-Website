"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from model import User, Rating, Movie, connect_to_db, db
from server import app
from datetime import datetime
from re import sub


def load_users():
    """Load users from u.user into database."""

    file_obj = open("seed_data/u.user")


    i = 0
    for line in file_obj:

        line = line.rstrip().split("|")
        user = User(user_id = line[0],
            age=line[1],
            zipcode=line[4])
        db.session.add(user)

        i += 1
        if i % 100 == 0:
            print "Inserted %d users" % i

    db.session.commit()


def load_movies():
    """Load movies from u.item into database."""

    file_obj = open("seed_data/u.item")

    i = 0

    for line in file_obj:
        line = line.rstrip().split("|")
        try:
            released_at_raw = line[2]
            movie_release_date = datetime.strptime(released_at_raw, "%d-%b-%Y")

            title = sub(" \(\d\d\d\d\)", "", line[1])

            movie = Movie(movie_id=line[0], title=title, released_at=movie_release_date, imdb_url=line[4])
            db.session.add(movie)
            
        except ValueError: # if there is no release date for a movie, skip it.
            pass # maybe put something else here if some other program wants this movie

        i += 1
        if i % 100 == 0:
            print "Inserted %d movies" % i

        
    db.session.commit()


def load_ratings():
    """Load ratings from u.data into database."""

    file_obj = open("seed_data/u.data")

    print "Ratings"

    i = 0
    for line in file_obj:
        line = line.rstrip().split()
        rating = Rating(user_id=int(line[0]), movie_id=int(line[1]), score=int(line[2]))

        db.session.add(rating)
        i += 1
        if i % 10000 == 0:
            print "Inserted %d ratings" % i
            db.session.commit()

if __name__ == "__main__":
    connect_to_db(app)

    load_users()
    load_movies()
    load_ratings()

# Don't run this without running python -i model.py and doing db.create_all() first