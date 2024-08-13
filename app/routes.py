from flask import Blueprint, request, jsonify, session, url_for
from flask_restful import Api, Resource, fields, marshal_with
from .models import db, Movie, Genre, Actor, User
from services.tmdb_services import TMDbService

# Define a blueprint
main = Blueprint('main', __name__)
api = Api(main)

# Define field mappings for marshalling
user_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'email': fields.String,
    'links': fields.Raw
}

def add_user_links(user):
    return {
        "logout": url_for('main.logoutresource', _external=True)
    }

# Registration Resource
class RegisterResource(Resource):
    @marshal_with(user_fields)
    def post(self):
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return {'message': 'All fields are required'}, 400

        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return {'message': 'User with this username or email already exists'}, 409

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        new_user.links = add_user_links(new_user)
        return new_user, 201

# Login Resource
class LoginResource(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return {'message': 'Both username and password are required'}, 400

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            return {'message': f'Welcome {username}'}, 200
        else:
            return {'message': 'Invalid username or password'}, 401

# Logout Resource
class LogoutResource(Resource):
    def post(self):
        session.pop('user_id', None)
        session.pop('username', None)
        return {'message': 'You have been logged out'}, 200

# Define field mappings for marshalling
movie_fields = {
    'id': fields.Integer,
    'tmdb_id': fields.Integer,
    'title': fields.String,
    'description': fields.String,
    'release_date': fields.String(attribute=lambda x: x.release_date.isoformat()),  # Convert date to ISO format string
    'rating': fields.Float,
    'poster_url': fields.String,
    'links': fields.Raw
}

def add_movie_links(movie):
    return {
        "self": url_for('main.movie_detail', movie_id=movie.id, _external=True),
        "all_movies": url_for('main.movies', _external=True)
    }

# Define API Resources
class MovieResource(Resource):
    @marshal_with(movie_fields)
    def get(self, movie_id):
        movie = Movie.query.get_or_404(movie_id)
        movie.links = add_movie_links(movie)
        return movie

    @marshal_with(movie_fields)
    def put(self, movie_id):
        movie = Movie.query.get_or_404(movie_id)
        data = request.get_json()

        movie.title = data.get('title', movie.title)
        movie.description = data.get('description', movie.description)
        movie.release_date = data.get('release_date', movie.release_date)
        movie.rating = data.get('rating', movie.rating)
        movie.poster_url = data.get('poster_url', movie.poster_url)

        db.session.commit()
        movie.links = add_movie_links(movie)
        return movie, 200

    def delete(self, movie_id):
        movie = Movie.query.get_or_404(movie_id)
        db.session.delete(movie)
        db.session.commit()
        return {'message': f'Movie with ID {movie_id} has been deleted'}, 200

class MovieCreateResource(Resource):
    @marshal_with(movie_fields)
    def post(self):
        data = request.get_json()
        new_movie = Movie(
            tmdb_id=data.get('tmdb_id', None),
            title=data['title'],
            description=data.get('description', ''),
            release_date=data.get('release_date'),
            rating=data.get('rating', 0),
            poster_url=data.get('poster_url', '')
        )
        db.session.add(new_movie)
        db.session.commit()
        new_movie.links = add_movie_links(new_movie)
        return new_movie, 201

class MovieListResource(Resource):
    @marshal_with(movie_fields)
    def get(self):
        movies = Movie.query.all()
        for movie in movies:
            movie.links = add_movie_links(movie)
        return movies

class TMDbFetchResource(Resource):
    def get(self, tmdb_id):
        movie_data = TMDbService.fetch_and_save_movie(tmdb_id)
        if movie_data:
            return jsonify({'message': 'Movie fetched and stored successfully!', 'movie': movie_data}), 200, {'Cache-Control': 'public, max-age=86400'}
        else:
            return jsonify({'message': 'Movie not found or failed to fetch!'}), 404

class TrendingMoviesResource(Resource):
    def get(self):
        trending_movies = TMDbService.fetch_trending_movies()
        if trending_movies:
            TMDbService.save_trending_movies_to_db(trending_movies)
            return {'message': 'Trending movies fetched and stored successfully!'}, 200, {'Cache-Control': 'public, max-age=3600'}
        else:
            return {'message': 'Failed to fetch trending movies!'}, 500

class TrendingMoviesListResource(Resource):
    @marshal_with(movie_fields)
    def get(self):
        trending_movies = Movie.query.order_by(Movie.release_date.desc()).limit(20).all()
        for movie in trending_movies:
            movie.links = add_movie_links(movie)
        return trending_movies

class MovieSearchResource(Resource):
    def get(self):
        query = request.args.get('query', '')
        if not query:
            return {'message': 'Please provide a search query'}, 400
        
        include_adult = request.args.get('include_adult', 'false').lower() == 'true'
        language = request.args.get('language', 'en-US')
        page = int(request.args.get('page', 1))
        primary_release_year = request.args.get('primary_release_year', None)
        region = request.args.get('region', None)
        year = request.args.get('year', None)

        results = TMDbService.search_movies(query, include_adult, language, page, primary_release_year, region, year)
        if results:
            return results, 200, {'Cache-Control': 'public, max-age=3600'}
        else:
            return {'message': 'No results found'}, 404

# Add resources to API
api.add_resource(MovieResource, '/movies/<int:movie_id>', endpoint='movie_detail')  # GET, PUT, DELETE for a movie
api.add_resource(MovieCreateResource, '/movies', endpoint='create_movie')  # POST for creating a movie
api.add_resource(MovieListResource, '/movies', endpoint='movies')
api.add_resource(TMDbFetchResource, '/tmdb/movies/<int:tmdb_id>')
api.add_resource(TrendingMoviesResource, '/tmdb/trending_movies')
api.add_resource(TrendingMoviesListResource, '/movies/trending')
api.add_resource(MovieSearchResource, '/movies/search')
api.add_resource(RegisterResource, '/users/register')
api.add_resource(LoginResource, '/users/login')
api.add_resource(LogoutResource, '/users/logout')
