from flask import Blueprint, request, jsonify, session, url_for
from flask_restful import Api, Resource, fields, marshal_with
from .models import db, Movie, Genre, Actor, User, Favorite, Rating, Watchlist
from services.tmdb_services import TMDbService
from flask_caching import Cache

# Define a blueprint
main = Blueprint('main', __name__)
api = Api(main)

# Initialize cache
cache = Cache()

# Define field mappings for marshalling
user_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'email': fields.String,
    'links': fields.Raw
}

movie_fields = {
    'id': fields.Integer,
    'tmdb_id': fields.Integer,
    'title': fields.String,
    'description': fields.String,
    'release_date': fields.String(attribute=lambda x: x['release_date'] if isinstance(x, dict) and 'release_date' in x else x.release_date.isoformat() if hasattr(x, 'release_date') and x.release_date else None),
    'rating': fields.Float,
    'poster_url': fields.String,
    'original_language': fields.String,
    'genres': fields.List(fields.String),
    'actors': fields.List(fields.Nested({
        'name': fields.String,
        'character': fields.String
    })),
    'links': fields.Raw
}

favorite_fields = {
    'id': fields.Integer,
    'movie': fields.Nested(movie_fields),
}

rating_fields = {
    'id': fields.Integer,
    'rating': fields.Float,
    'review': fields.String,
    'created_at': fields.String(attribute=lambda x: x.created_at.isoformat()),
    'movie': fields.Nested(movie_fields),
}

watchlist_fields = {
    'id': fields.Integer,
    'movie': fields.Nested(movie_fields),
}

# Additional helper methods for adding HATEOAS links
def add_user_links(user):
    return {
        "logout": url_for('main.logoutresource', _external=True)
    }

def add_movie_links(movie):
    return {
        "self": url_for('main.movie_detail', movie_id=movie.id, _external=True),
        "all_movies": url_for('main.movies', _external=True)
    }

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

class LoginResource(Resource):
    @marshal_with(user_fields)
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
            user.links = add_user_links(user)
            return user, 200
        else:
            return {'message': 'Invalid username or password'}, 401

class LogoutResource(Resource):
    def post(self):
        session.pop('user_id', None)
        session.pop('username', None)
        return {'message': 'You have been logged out'}, 200

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
        existing_movie = Movie.query.filter_by(tmdb_id=data.get('tmdb_id')).first()
        if existing_movie:
            return {'message': 'Movie with this TMDB ID already exists'}, 409

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
    @marshal_with(movie_fields)
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
            return results, 200
        else:
            return {'message': 'No results found'}, 404

class FavoriteResource(Resource):
    @marshal_with(favorite_fields)
    def post(self):
        user_id = session.get('user_id')
        data = request.get_json()
        movie_id = data.get('movie_id')

        favorite = Favorite.query.filter_by(user_id=user_id, movie_id=movie_id).first()
        if favorite:
            return {'message': 'This movie is already in your favorites'}, 409

        new_favorite = Favorite(user_id=user_id, movie_id=movie_id)
        db.session.add(new_favorite)
        db.session.commit()

        return new_favorite, 201

    @marshal_with(favorite_fields)
    def get(self):
        user_id = session.get('user_id')
        favorites = Favorite.query.filter_by(user_id=user_id).all()
        return favorites
    
    def delete(self, movie_id):
        user_id = session.get('user_id')
        favorite = Favorite.query.filter_by(user_id=user_id, movie_id=movie_id).first()
        if not favorite:
            return {'message': 'This movie is not in your favorites'}, 404

        db.session.delete(favorite)
        db.session.commit()

        return {'message': 'Movie removed from favorites'}, 200

class RatingResource(Resource):
    @marshal_with(rating_fields)
    def post(self):
        user_id = session.get('user_id')
        data = request.get_json()
        movie_id = data.get('movie_id')
        rating_value = data.get('rating')
        review = data.get('review', '')

        rating = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first()
        if rating:
            rating.rating = rating_value
            rating.review = review
        else:
            rating = Rating(user_id=user_id, movie_id=movie_id, rating=rating_value, review=review)
            db.session.add(rating)

        db.session.commit()

        return rating, 201

    @marshal_with(rating_fields)
    def get(self):
        user_id = session.get('user_id')
        ratings = Rating.query.filter_by(user_id=user_id).all()
        return ratings

class MovieReviewsResource(Resource):
    @marshal_with(rating_fields)
    def get(self, movie_id):
        reviews = Rating.query.filter_by(movie_id=movie_id).all()
        return reviews, 200

class WatchlistResource(Resource):
    @marshal_with(watchlist_fields)
    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'message': 'User not logged in'}, 401
        
        data = request.get_json()
        movie_id = data.get('movie_id')

        watchlist_item = Watchlist.query.filter_by(user_id=user_id, movie_id=movie_id).first()
        if watchlist_item:
            return {'message': 'This movie is already in your watchlist'}, 409

        new_watchlist_item = Watchlist(user_id=user_id, movie_id=movie_id)
        db.session.add(new_watchlist_item)
        db.session.commit()

        return new_watchlist_item, 201

    @marshal_with(watchlist_fields)
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'message': 'User not logged in'}, 401
        watchlist = Watchlist.query.filter_by(user_id=user_id).all()
        return watchlist
    
    def delete(self, movie_id):
        user_id = session.get('user_id')
        watchlist_item = Watchlist.query.filter_by(user_id=user_id, movie_id=movie_id).first()
        if not watchlist_item:
            return {'message': 'This movie is not in your watchlist'}, 404

        db.session.delete(watchlist_item)
        db.session.commit()

        return {'message': 'Movie removed from watchlist'}, 200

class EnsureMovieResource(Resource):
    @marshal_with(movie_fields)
    def post(self):
        data = request.get_json()
        tmdb_id = data.get('tmdb_id')

        if not tmdb_id:
            return {'message': 'TMDb ID is required'}, 400  # Ensure the ID is provided

        # Check if the movie already exists in the local database
        movie = Movie.query.filter_by(tmdb_id=tmdb_id).first()

        if not movie:
            # Fetch and save the movie from TMDb if it doesn't exist
            movie_data = TMDbService.fetch_and_save_movie(tmdb_id)
            
            if not movie_data:
                return {'message': 'Failed to fetch movie from TMDb'}, 404

            movie = Movie.query.filter_by(tmdb_id=tmdb_id).first()
            if not movie:
                return {'message': 'Failed to save movie to the database'}, 500

        return movie, 201




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
api.add_resource(FavoriteResource, '/users/favorites', endpoint='favorites')  # POST, GET for favorites
api.add_resource(FavoriteResource, '/users/favorites/<int:movie_id>', endpoint='favorite_delete')  # DELETE for a specific favorite
api.add_resource(RatingResource, '/users/ratings', endpoint='ratings')
api.add_resource(WatchlistResource, '/users/watchlist', endpoint='watchlist')  # POST, GET for watchlist
api.add_resource(WatchlistResource, '/users/watchlist/<int:movie_id>', endpoint='watchlist_delete')  # DELETE for a specific watchlist item
api.add_resource(MovieReviewsResource, '/movies/<int:movie_id>/reviews', endpoint='movie_reviews')
api.add_resource(EnsureMovieResource, '/movies/ensure')
