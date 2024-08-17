import requests
from flask import current_app
from app.models import db, Movie, Genre, Actor

class TMDbService:

    _genre_mapping = None

    @staticmethod
    def _fetch_genre_mapping():
        """Fetches and caches the genre mapping from TMDb API."""
        api_key = current_app.config.get('TMDB_API_KEY')
        url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}&language=en-US"

        response = requests.get(url)
        if response.status_code == 200:
            genres = response.json().get('genres', [])
            TMDbService._genre_mapping = {genre['id']: genre['name'] for genre in genres}
            print("DEBUG: Genre mapping fetched successfully.")
        else:
            print(f"Failed to fetch genre mapping: {response.status_code}")
    
    @staticmethod
    def get_genre_mapping():
        """Returns the genre mapping, fetching it if necessary."""
        if TMDbService._genre_mapping is None:
            TMDbService._fetch_genre_mapping()
        return TMDbService._genre_mapping

    @staticmethod
    def fetch_movie_by_id(tmdb_id):
        api_key = current_app.config.get('TMDB_API_KEY')
        url = f'https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={api_key}&append_to_response=credits'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None

    @staticmethod
    def save_movie_to_db(movie_data):
        print("DEBUG: Movie data received:", movie_data)

        genre_mapping = TMDbService.get_genre_mapping()

        # Process genres
        genre_objects = []
        for genre_id in movie_data.get('genre_ids', []):
            genre_name = genre_mapping.get(genre_id, "Unknown")
            genre_obj = Genre.query.filter_by(name=genre_name).first()
            if not genre_obj:
                genre_obj = Genre(name=genre_name)
                db.session.add(genre_obj)
            genre_objects.append(genre_obj)

        print("DEBUG: Processed genres:", [genre.name for genre in genre_objects])

        existing_movie = Movie.query.filter_by(tmdb_id=movie_data['id']).first()
        if existing_movie:
            print("DEBUG: Updating existing movie:", existing_movie.title)
            existing_movie.title = movie_data.get('title', existing_movie.title)
            existing_movie.description = movie_data.get('overview', existing_movie.description)
            existing_movie.release_date = movie_data.get('release_date', existing_movie.release_date)
            existing_movie.rating = movie_data.get('vote_average', existing_movie.rating)
            existing_movie.poster_url = f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path', existing_movie.poster_url)}"
            existing_movie.genres = genre_objects
            existing_movie.original_language = movie_data.get('original_language', existing_movie.original_language)
            print("DEBUG: Updated movie details saved.")
        else:
            movie = Movie(
                tmdb_id=movie_data['id'],
                title=movie_data.get('title', 'Untitled'),
                description=movie_data.get('overview', ''),
                release_date=movie_data.get('release_date'),
                rating=movie_data.get('vote_average', 0),
                poster_url=f"https://image.tmdb.org/t/p/w500{movie_data.get('poster_path', '')}",
                genres=genre_objects,
                original_language=movie_data.get('original_language', 'Unknown'),
            )
            db.session.add(movie)
            print("DEBUG: New movie added:", movie.title)

        db.session.commit()
        print("DEBUG: Movie data committed to the database.")

    @staticmethod
    def fetch_and_save_movie(tmdb_id):
        movie_data = TMDbService.fetch_movie_by_id(tmdb_id)
        if movie_data:
            print(f"DEBUG: Fetched movie data from TMDb: {movie_data}")
            TMDbService.save_movie_to_db(movie_data)
            return movie_data
        print(f"ERROR: Could not fetch movie data from TMDb for ID {tmdb_id}")
        return None


    @staticmethod
    def fetch_trending_movies(time_window='day'):
        api_key = current_app.config.get('TMDB_API_KEY')
        url = f'https://api.themoviedb.org/3/trending/movie/{time_window}?api_key={api_key}'
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json().get('results', [])
            print(f'Trending Movies: {result}')
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
            results = response.json().get('results', [])
            genre_mapping = TMDbService.get_genre_mapping()

            # Convert genre_ids to genre names
            for result in results:
                result['genres'] = [genre_mapping.get(genre_id, "Unknown") for genre_id in result.get('genre_ids', [])]
                result['poster_url'] = f"https://image.tmdb.org/t/p/w500{result.get('poster_path', '')}"  # Ensure correct poster URL
            return results
        return None
