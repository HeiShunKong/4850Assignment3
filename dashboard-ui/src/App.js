import React, { useEffect, useState } from 'react';
import './App.css';
import logo from './logo.png';

import EndpointAnalyzer from './components/EndpointAnalyzer';
import AppStats from './components/AppStats';

function App() {
    // Your cloud base URL for the API
    const baseUrl = "https://mysql-3855.centralus.cloudapp.azure.com";

    // States for managing the movie and review data, as well as last updated time
    const [movies, setMovies] = useState([]);
    const [reviews, setReviews] = useState([]);
    const [lastUpdated, setLastUpdated] = useState(null);

    // Fetch movies and reviews from the MovieAPI
    const fetchMoviesAndReviews = async () => {
        try {
            // Fetch movie data from the movie endpoint
            const movieResponse = await fetch(`${baseUrl}/movie`);
            const movieData = await movieResponse.json();
            setMovies(movieData);

            // Fetch review data from the review endpoint
            const reviewResponse = await fetch(`${baseUrl}/review`);
            const reviewData = await reviewResponse.json();
            setReviews(reviewData);

            // Optionally, fetch stats from the stats endpoint for last updated time
            const statsResponse = await fetch(`${baseUrl}/stats`);
            const statsData = await statsResponse.json();
            setLastUpdated(statsData.timestamp);  // Assuming the timestamp is in the response

        } catch (error) {
            console.error("Error fetching data:", error);
        }
    };

    // Fetch stats and movie/review data on initial render and set up periodic updates
    useEffect(() => {
        fetchMoviesAndReviews();
        const interval = setInterval(() => {
            fetchMoviesAndReviews();
        }, 4000);  // Update stats and movie/review data every 4 seconds

        return () => clearInterval(interval);  // Clean up interval on component unmount
    }, []);

    return (
        <div className="App">
            <img src={logo} className="App-logo" alt="logo" height="150px" width="400px" />
            <div>
                {/* Display AppStats and Last Updated Timestamp */}
                <AppStats lastUpdated={lastUpdated} />
                <h1>Movie List</h1>
                <ul>
                    {movies.map((movie) => (
                        <li key={movie.id}>
                            <h2>{movie.title}</h2>
                            <p>Length: {movie.length} minutes</p>
                            {/* Assuming reviews contain a rating and are linked to a movie */}
                            <ul>
                                {reviews
                                    .filter((review) => review.movie_id === movie.id)
                                    .map((review) => (
                                        <li key={review.id}>
                                            <p>Review Rating: {review.rating}</p>
                                            <p>Comment: {review.comment}</p>
                                        </li>
                                    ))}
                            </ul>
                        </li>
                    ))}
                </ul>
                <h1>Analyzer Endpoints</h1>
                {/* Display EndpointAnalyzer for other endpoints */}
                <EndpointAnalyzer endpoint={`${baseUrl}/movie`} />
                <EndpointAnalyzer endpoint={`${baseUrl}/review`} />
            </div>
        </div>
    );
}

export default App;
