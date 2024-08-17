import React, { useState, useEffect, useContext } from 'react';
import { UserContext } from '../UserContext';
import { fetchFavorites } from '../api';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';

const MyFavorites = () => {
    const { user } = useContext(UserContext);
    const [favorites, setFavorites] = useState([]);
  
    useEffect(() => {
      if (user) {
        const loadFavorites = async () => {
          try {
            const response = await fetchFavorites();
            setFavorites(response.data);
          } catch (error) {
            console.error('Error fetching favorites:', error);
          }
        };
        loadFavorites();
      }
    }, [user]);
  
    if (!user) return <div>Please log in to view your favorites.</div>;
  
    return (
      <Container>
        <h2 className="text-uppercase text-center my-4">My Favorites</h2>
        <Row>
          {favorites.length === 0 ? (
            <p className="text-center">You have no favorite movies.</p>
          ) : (
            favorites.map((item) => (
              <Col key={item.movie.id} md={4} className="mb-4">
                <Card>
                  <Card.Img variant="top" src={item.movie.poster_url} />
                  <Card.Body>
                    <Card.Title>{item.movie.title}</Card.Title>
                    <Link to={`/movies/${item.movie.id}`}>
                      <Button variant="primary">View Details</Button>
                    </Link>
                  </Card.Body>
                </Card>
              </Col>
            ))
          )}
        </Row>
      </Container>
    );
  };
  
  export default MyFavorites;