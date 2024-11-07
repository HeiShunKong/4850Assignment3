import React, { useEffect, useState } from 'react';
import '../App.css';

export default function AppStats({ lastUpdated }) {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null);

    // Function to fetch stats
    const getStats = () => {
        fetch(`https://mysql-3855.centralus.cloudapp.azure.com:8100/events/stats`)
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
    } else if (isLoaded === false) {
        return <div>Loading...</div>;
    } else if (isLoaded === true) {
        return (
            <div>
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
                    <tbody>
                        <tr>
                            <th>Blood Pressure</th>
                            <th>Heart Rate</th>
                        </tr>
                        <tr>
                            <td># BP: {stats['num_bp_readings']}</td>
                            <td># HR: {stats['num_hr_readings']}</td>
                        </tr>
                        <tr>
                            <td colSpan="2">Max BP Systolic: {stats['max_bp_sys_reading']}</td>
                        </tr>
                        <tr>
                            <td colSpan="2">Max BP Diastolic: {stats['max_bp_dia_reading']}</td>
                        </tr>
                        <tr>
                            <td colSpan="2">Max HR: {stats['max_hr_reading']}</td>
                        </tr>
                    </tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>
            </div>
        );
    }
}
