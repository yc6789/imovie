from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    favorites = db.relationship('Favorite', back_populates='user', cascade="all, delete-orphan")
    watchlist = db.relationship('Watchlist', back_populates='user', cascade="all, delete-orphan")
    ratings = db.relationship('Rating', back_populates='user', cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Genre(db.Model):
    __tablename__ = 'genres'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    movies = db.relationship('Movie', secondary='movie_genres', back_populates='genres')

class Actor(db.Model):
    __tablename__ = 'actors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    movies = db.relationship('Movie', secondary='movie_actors', back_populates='actors')

class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer, unique=True, nullable=False)  # Unique identifier from TMDb
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    release_date = db.Column(db.Date)
    rating = db.Column(db.Float)
    poster_url = db.Column(db.String)
    genres = db.relationship('Genre', secondary='movie_genres', back_populates='movies')
    actors = db.relationship('Actor', secondary='movie_actors', back_populates='movies')

class MovieGenre(db.Model):
    __tablename__ = 'movie_genres'
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id', ondelete='CASCADE'), primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id', ondelete='CASCADE'), primary_key=True)

class MovieActor(db.Model):
    __tablename__ = 'movie_actors'
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id', ondelete='CASCADE'), primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey('actors.id', ondelete='CASCADE'), primary_key=True)

class Watchlist(db.Model):
    __tablename__ = 'watchlist'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id', ondelete='CASCADE'), primary_key=True)
    user = db.relationship('User', back_populates='watchlist')
    movie = db.relationship('Movie')

class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id', ondelete='CASCADE'))
    user = db.relationship('User', back_populates='favorites')
    movie = db.relationship('Movie')

class Rating(db.Model):
    __tablename__ = 'ratings'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id', ondelete='CASCADE'), primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    user = db.relationship('User', back_populates='ratings')
    movie = db.relationship('Movie')
