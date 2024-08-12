import requests
from flask import current_app
from .models import db, Movie, Genre, Actor

class TMDbService:

    @staticmethod
    def fetch_movie_by_id(tmdb_id):
        api_key = current_app.config.get('TMDB_API_KEY')
        url = f'https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={api_key}'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None

    @staticmethod
    def save_movie_to_db(movie_data):
        # Process genres
        genre_objects = []
        for genre in movie_data.get('genres', []):
            genre_obj = Genre.query.filter_by(name=genre['name']).first()
            if not genre_obj:
                genre_obj = Genre(name=genre['name'])
                db.session.add(genre_obj)
            genre_objects.append(genre_obj)

        # Process actors (fetching from credits endpoint)
        actor_objects = []
        credits_url = f'https://api.themoviedb.org/3/movie/{movie_data["id"]}/credits?api_key={current_app.config.get("TMDB_API_KEY")}'
        credits_response = requests.get(credits_url)
        if credits_response.status_code == 200:
            credits_data = credits_response.json()
            for actor in credits_data.get('cast', []):
                actor_obj = Actor.query.filter_by(name=actor['name']).first()
                if not actor_obj:
                    actor_obj = Actor(name=actor['name'])
                    db.session.add(actor_obj)
                actor_objects.append(actor_obj)

        # Create and store movie object
        movie = Movie(
            tmdb_id=movie_data['id'],
            title=movie_data['title'],
            description=movie_data.get('overview', ''),
            release_date=movie_data.get('release_date'),
            rating=movie_data.get('vote_average', 0),
            poster_url=movie_data.get('poster_path', ''),
            genres=genre_objects,
            actors=actor_objects
        )
        db.session.add(movie)
        db.session.commit()

    @staticmethod
    def fetch_and_save_movie(tmdb_id):
        movie_data = TMDbService.fetch_movie_by_id(tmdb_id)
        if movie_data:
            TMDbService.save_movie_to_db(movie_data)
            return movie_data
        return None

    @staticmethod
    def fetch_trending_movies(time_window='day'):
        api_key = current_app.config.get('TMDB_API_KEY')
        url = f'https://api.themoviedb.org/3/trending/movie/{time_window}?api_key={api_key}'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('results', [])
        return None

    @staticmethod
    def save_trending_movies_to_db(movies):
        for movie_data in movies:
            # Check if movie already exists
            movie = Movie.query.filter_by(tmdb_id=movie_data['id']).first()
            if not movie:
                TMDbService.save_movie_to_db(movie_data)
