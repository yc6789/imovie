from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource, fields, marshal_with
from .models import db, Movie, Genre, Actor, User
from .tmdb_service import TMDbService

# Define a blueprint
main = Blueprint('main', __name__)
api = Api(main)

# Define field mappings for marshalling
movie_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'description': fields.String,
    'release_date': fields.DateTime,
    'rating': fields.Float,
    'poster_url': fields.String,
}

# Define API Resources
class MovieResource(Resource):
    @marshal_with(movie_fields)
    def get(self, movie_id):
        movie = Movie.query.get_or_404(movie_id)
        return movie

    @marshal_with(movie_fields)
    def post(self):
        data = request.get_json()
        new_movie = Movie(
            title=data['title'],
            description=data['description'],
            release_date=data['release_date'],
            rating=data['rating'],
            poster_url=data['poster_url']
        )
        db.session.add(new_movie)
        db.session.commit()
        return new_movie, 201

class MovieListResource(Resource):
    @marshal_with(movie_fields)
    def get(self):
        movies = Movie.query.all()
        return movies

class TMDbFetchResource(Resource):
    def get(self, tmdb_id):
        movie_data = TMDbService.fetch_and_save_movie(tmdb_id)
        if movie_data:
            return jsonify({'message': 'Movie fetched and stored successfully!', 'movie': movie_data})
        else:
            return jsonify({'message': 'Movie not found or failed to fetch!'}), 404

class TrendingMoviesResource(Resource):
    def get(self):
        trending_movies = TMDbService.fetch_trending_movies()
        if trending_movies:
            TMDbService.save_trending_movies_to_db(trending_movies)
            return jsonify({'message': 'Trending movies fetched and stored successfully!'}), 200
        else:
            return jsonify({'message': 'Failed to fetch trending movies!'}), 500

class TrendingMoviesListResource(Resource):
    @marshal_with(movie_fields)
    def get(self):
        trending_movies = Movie.query.order_by(Movie.release_date.desc()).limit(20).all()
        return trending_movies

# Add resources to API
api.add_resource(MovieResource, '/movie/<int:movie_id>')
api.add_resource(MovieListResource, '/movies')
api.add_resource(TMDbFetchResource, '/fetch_movie/<int:tmdb_id>')
api.add_resource(TrendingMoviesResource, '/fetch_trending_movies')
api.add_resource(TrendingMoviesListResource, '/trending_movies')