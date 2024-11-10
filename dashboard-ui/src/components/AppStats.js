import React, { useEffect, useState } from 'react';
import '../App.css';

export default function AppStats({ lastUpdated }) {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null);

    // Function to fetch stats
    const getStats = () => {
        fetch(`http://mysql-3855.centralus.cloudapp.azure.com:8100/events/stats`)
            .then((res) => res.json())
            .then(
                (result) => {
                    console.log("Received Stats");
                    setStats(result);
                    setIsLoaded(true);
                },
                (error) => {
                    setError(error);
                    setIsLoaded(true);
                }
            );
    };

    useEffect(() => {
        getStats();
        const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
        return () => clearInterval(interval);
    }, []);

    if (error) {
        return <div className={"error"}>Error found when fetching from API</div>;
    } else if (!isLoaded) {
        return <div>Loading...</div>;
    } else {
        return (
            <div>
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
                    <tbody>
                        <tr>
                            <th>Total Movies</th>
                            <th>Total Reviews</th>
                        </tr>
                        <tr>
                            <td># Movies: {stats['num_movies']}</td>
                            <td># Reviews: {stats['num_reviews']}</td>
                        </tr>
                        <tr>
                            <td colSpan="2">Average Movie Length: {stats['avg_movie_length']}</td>
                        </tr>
                        <tr>
                            <td colSpan="2">Highest Rating: {stats['max_review_rating']}</td>
                        </tr>
                    </tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>
            </div>
        );
    }
}
