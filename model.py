"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy
import correlation

# This is the connection to the SQLite database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of the ratings website"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True, unique=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)

    def __repr__(self):
        """Provide helpful information representation when printed!"""

        return "<User user_id = %s email = %s>" %(self.user_id, self.email)

    def similarity(self, other):
        """Return Pearson rating for user compared to other user."""

        u_ratings = {}
        paired_ratings = []

        for r in self.ratings:
            u_ratings[r.movie_id] = r

        for r in other.ratings:
            u_r = u_ratings.get(r.movie_id)
            if u_r:
                paired_ratings.append( (u_r.score, r.score) )

        if paired_ratings:
            return correlation.pearson(paired_ratings)

        else:
            return 0.0

    def predict_rating(self, movie):
        """Predict user's rating of a movie."""

        other_ratings = movie.ratings

        similarities = [
            (self.similarity(r.user), r)
            for r in other_ratings
        ]

        similarities.sort(reverse=True)

        similarities = [(sim, r) for sim, r in similarities if sim > 0]

        if not similarities:
            return None

        numerator = sum([r.score * sim for sim, r in similarities])
        denominator = sum([sim for sim, r in similarities])

        return numerator/denominator


            #this is the one we wrote
    # def find_most_similar_user(self, movie):
    #     """Finds the most similar user.

    #     Returns a tuple: (similarity, user_id)
    #     """

    # # m = Movie.query.filter_by(title="Toy Story").one()
    # # balloon = User.query.get(944)

    #     other_users = [rating.user for rating in movie.ratings]

    #     user_similarities = []

    #     # i = 0
    #     for other_u in other_users:
    #         user_similarities.append((self.similarity(other_u), other_u.user_id))
    #         # i += 1
    #         # if i % 100 == 0:
    #         #     print "%d users checked" % i

    #     all_user_tuples = sorted(user_similarities, reverse=True)

    #     top_user_tuple = all_user_tuples[0]

    #     return top_user_tuple

    # def guess_rating(top_user_tuple, movie_id):
    #     """Given a similar user and a movie, predicts a rating for that movie."""

    #     similarity, top_user_id = top_user_tuple

    #     # print "similarity and top user id are: ", similarity, top_user_id

    #     rating_tuple = db.session.query(Rating.score).filter(Rating.user_id == top_user_id, Rating.movie_id == movie_id).first()

    #     # print "the rating tuple is: ", rating_tuple

    #     score = rating_tuple[0]

    #     guess = score * similarity

    #     # print "and our guess is", guess
    #     return guess


class Movie(db.Model):
    """Movie in the database"""

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    released_at = db.Column(db.DateTime, nullable=False)
    imdb_url = db.Column(db.String(500), nullable=True)

    def __repr__(self):
        """Provide helpful information representation when printed!"""

        return "<Movie = %s released_at = %s>" %(self.title, self.released_at)

class Rating(db.Model):
    """User ratings"""

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    score = db.Column(db.Integer, nullable=False) 

    # Define relationship to user
    user = db.relationship("User", backref=db.backref("ratings", order_by=rating_id))

    # Define relationship to movie
    movie = db.relationship("Movie", backref=db.backref("ratings", order_by=rating_id))



    def __repr__(self):
        """Provide helpful information representation when printed!"""

        return "<Rating user_id = %s movie_id = %s score = %s>" %(self.user_id, self.movie_id, self.score)

##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ratings.db'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."



