import React, { useState, useEffect, useContext } from 'react';
import { UserContext } from '../UserContext';
import { fetchWatchlist } from '../api';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';

const MyWatchlist = () => {
    const { user } = useContext(UserContext);
    const [watchlist, setWatchlist] = useState([]);
  
    useEffect(() => {
      if (user) {
        const loadWatchlist = async () => {
          try {
            const response = await fetchWatchlist();
            setWatchlist(response.data);
          } catch (error) {
            console.error('Error fetching watchlist:', error);
          }
        };
        loadWatchlist();
      }
    }, [user]);
  
    if (!user) return <div>Please log in to view your watchlist.</div>;
  
    return (
      <Container>
        <h2 className="text-uppercase text-center my-4">My Watchlist</h2>
        <Row>
          {watchlist.length === 0 ? (
            <p className="text-center">Your watchlist is empty.</p>
          ) : (
            watchlist.map((item) => (
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
  
  export default MyWatchlist;