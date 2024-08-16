import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { UserContext } from '../UserContext';
import { FaStar, FaRegStar } from 'react-icons/fa';
import { Card, Button, Form, Container, Row, Col } from 'react-bootstrap';
import {
  fetchMovieDetails,
  fetchReviews,
  fetchWatchlist,
  fetchFavorites,
  addReview,
  addToWatchlist,
  removeFromWatchlist,
  addFavorite,
  removeFavorite
} from '../api';

const MovieDetails = () => {
  const { id } = useParams();
  const [movie, setMovie] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [newReview, setNewReview] = useState('');
  const [newRating, setNewRating] = useState(5);
  const [isInWatchlist, setIsInWatchlist] = useState(false);
  const [isFavorited, setIsFavorited] = useState(false);
  const { user } = useContext(UserContext);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const movieResponse = await fetchMovieDetails(id);
        setMovie(movieResponse.data);

        const reviewsResponse = await fetchReviews(id);
        setReviews(reviewsResponse.data);

        if (user) {
          const watchlistResponse = await fetchWatchlist();
          if (Array.isArray(watchlistResponse.data)) {
            const inWatchlist = watchlistResponse.data.some(
              (item) => item.movie.id === parseInt(id)
            );
            setIsInWatchlist(inWatchlist);
          } else {
            console.error('Watchlist response is not an array:', watchlistResponse.data);
          }

          const favoritesResponse = await fetchFavorites();
          if (Array.isArray(favoritesResponse.data)) {
            const favorited = favoritesResponse.data.some(
              (item) => item.movie.id === parseInt(id)
            );
            setIsFavorited(favorited);
          } else {
            console.error('Favorites response is not an array:', favoritesResponse.data);
          }
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, [id, user]);

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    if (!user) {
      navigate('/login');
      return;
    }

    const reviewData = {
      movie_id: id,
      rating: newRating,
      review: newReview,
    };

    try {
      const response = await addReview(reviewData);
      setReviews([...reviews, response.data]);
      setNewReview('');
      setNewRating(5);
    } catch (error) {
      console.error('Error adding review:', error);
    }
  };

  const toggleWatchlist = async () => {
    if (!user) {
      navigate('/login');
      return;
    }

    try {
      if (isInWatchlist) {
        await removeFromWatchlist(id);
      } else {
        await addToWatchlist(id);
      }
      setIsInWatchlist(!isInWatchlist);
    } catch (error) {
      if (error.response && error.response.status === 401) {
        navigate('/login');  // Redirect to login if not authenticated
      } else {
        console.error(`Error ${isInWatchlist ? 'removing from' : 'adding to'} watchlist:`, error);
      }
    }
  };

  const toggleFavorites = async () => {
    if (!user) {
      navigate('/login');
      return;
    }

    try {
      if (isFavorited) {
        await removeFavorite(id);
      } else {
        await addFavorite(id);
      }
      setIsFavorited(!isFavorited);
    } catch (error) {
      if (error.response && error.response.status === 401) {
        navigate('/login');  // Redirect to login if not authenticated
      } else {
        console.error(`Error ${isFavorited ? 'removing from' : 'adding to'} favorites:`, error);
      }
    }
  };

  if (!movie) return <div>Loading...</div>;

  return (
    <Container className="my-5">
      <Row>
        <Col md={4}>
          <Card>
            <Card.Img variant="top" src={movie.poster_url} alt={movie.title} />
          </Card>
        </Col>
        <Col md={8}>
          <h2>{movie.title}</h2>
          <p><strong>Release Date:</strong> {movie.release_date}</p>
          <p><strong>Rating:</strong> {movie.rating}</p>
          <p>{movie.description}</p>
          <Button variant={isInWatchlist ? "danger" : "primary"} onClick={toggleWatchlist}>
            {isInWatchlist ? 'Remove from Watchlist' : 'Add to Watchlist'}
          </Button>
          <Button variant={isFavorited ? "warning" : "secondary"} className="ml-2" onClick={toggleFavorites}>
            {isFavorited ? 'Remove from Favorites' : 'Add to Favorites'}
          </Button>
        </Col>
      </Row>

      <hr className="my-5" />

      <h3>Reviews</h3>
      {reviews.length === 0 ? (
        <p>No reviews yet. Be the first to review this movie!</p>
      ) : (
        reviews.map(review => (
          <Card key={review.id} className="mb-4">
            <Card.Body>
              <Card.Title>
                {Array.from({ length: Math.floor(review.rating) }, (_, i) => (
                  <FaStar key={i} color="gold" />
                ))}
                {review.rating % 1 !== 0 && <FaStar color="gold" />}
                {Array.from({ length: 10 - Math.ceil(review.rating) }, (_, i) => (
                  <FaRegStar key={i} color="gold" />
                ))}
                <span className="ml-2">{review.user?.username || 'Anonymous'}</span>
              </Card.Title>
              <Card.Subtitle className="mb-2 text-muted">{new Date(review.created_at).toLocaleDateString()}</Card.Subtitle>
              <Card.Text>{review.review}</Card.Text>
            </Card.Body>
          </Card>
        ))
      )}

      <Form onSubmit={handleReviewSubmit} className="mt-4">
        <Form.Group>
          <Form.Label>Your Rating (0.5 to 10)</Form.Label>
          <Form.Control
            type="range"
            min="0.5"
            max="10"
            step="0.5"
            value={newRating}
            onChange={(e) => setNewRating(e.target.value)}
            required
          />
          <Form.Text className="text-muted">Rating: {newRating}</Form.Text>
        </Form.Group>
        <Form.Group>
          <Form.Label>Your Review</Form.Label>
          <Form.Control
            as="textarea"
            value={newReview}
            onChange={(e) => setNewReview(e.target.value)}
            rows={3}
            required
          />
        </Form.Group>
        <Button type="submit" variant="success" className="mt-2">Submit Review</Button>
      </Form>
    </Container>
  );
};

export default MovieDetails;
