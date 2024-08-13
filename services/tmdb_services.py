import requests
from flask import current_app
from app.models import db, Movie, Genre, Actor

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

        # Check if the movie already exists in the database by tmdb_id
        existing_movie = Movie.query.filter_by(tmdb_id=movie_data['id']).first()
        if existing_movie:
            # Update the existing movie's details if necessary
            existing_movie.title = movie_data['title']
            existing_movie.description = movie_data.get('overview', '')
            existing_movie.release_date = movie_data.get('release_date')
            existing_movie.rating = movie_data.get('vote_average', 0)
            existing_movie.poster_url = f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path', '')}"
            existing_movie.genres = genre_objects
            existing_movie.actors = actor_objects
        else:
            # Create a new movie object
            movie = Movie(
                tmdb_id=movie_data['id'],
                title=movie_data['title'],
                description=movie_data.get('overview', ''),
                release_date=movie_data.get('release_date'),
                rating=movie_data.get('vote_average', 0),
                poster_url=f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path', '')}",
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
            movie = Movie.query.filter_by(tmdb_id=movie_data['id']).first()
            if not movie:
                TMDbService.save_movie_to_db(movie_data)

    @staticmethod
    def search_movies(query, include_adult=False, language='en-US', page=1, primary_release_year=None, region=None, year=None):
        api_key = current_app.config.get('TMDB_API_KEY')
        params = {
            'api_key': api_key,
            'query': query,
            'include_adult': include_adult,
            'language': language,
            'page': page,
        }
        if primary_release_year:
            params['primary_release_year'] = primary_release_year
        if region:
            params['region'] = region
        if year:
            params['year'] = year
        
        url = 'https://api.themoviedb.org/3/search/movie'
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json().get('results', [])
        return None