import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import DashboardStats from './DashboardStats'; // We still need our charts

const API_URL = 'http://localhost:8001/api/logs';

function App() {
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState(null);

  // --- NEW: State for the search bar ---
  // 'searchTerm' updates instantly as the user types
  const [searchTerm, setSearchTerm] = useState('');
  // 'debouncedSearchTerm' updates 300ms after the user stops typing
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');

  // --- NEW: Debounce Effect ---
  // This effect runs whenever 'searchTerm' changes
  useEffect(() => {
    // Set up a timer
    const timerId = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm);
    }, 300); // 300ms delay

    // This is the cleanup function: if the user types again,
    // clear the old timer and start a new one
    return () => {
      clearTimeout(timerId);
    };
  }, [searchTerm]); // Re-run this effect only if searchTerm changes

  // This function fetches the data from our backend
  const fetchLogs = async (currentSearchTerm) => { // <-- Now takes a parameter
    try {
      // NEW: Pass the search term as a query parameter
      const response = await axios.get(API_URL, {
        params: { search: currentSearchTerm }
      });
      
      setLogs(response.data.logs);
      setError(null);
    } catch (err) {
      console.error("Error fetching logs:", err);
      setError("Failed to fetch logs. Is the Query API running?");
    }
  };

  // This effect now fetches data AND auto-refreshes
  // It re-runs whenever the *debounced* search term changes
  useEffect(() => {
    fetchLogs(debouncedSearchTerm); // Fetch immediately with new search term

    const intervalId = setInterval(() => {
      fetchLogs(debouncedSearchTerm); // Refresh data every 3 seconds
    }, 3000);

    return () => clearInterval(intervalId);
  }, [debouncedSearchTerm]); // <-- UPDATED DEPENDENCY

  // Simple function to format the timestamp
  const formatTimestamp = (isoString) => {
    return new Date(isoString).toLocaleString();
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI-Powered Log Analytics Dashboard</h1>
        
        {/* --- NEW: Search Bar --- */}
        <div className="search-bar-container">
          <input
            type="text"
            className="search-bar"
            placeholder="Search logs (e.g., 'payment', 'ERROR')..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </header>
      <main>
        {error && <div className="error-message">{error}</div>}
        
        <DashboardStats logs={logs} />
        
        <div className="log-table-container">
          <table>
            {/* ... table head is the same ... */}
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Service</th>
                <th>Level</th>
                <th>Sentiment</th>
                <th>Message</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log, index) => (
                <tr key={index} className={`log-level-${log.level} sentiment-${log.ai_sentiment}`}>
                  <td>{formatTimestamp(log['@timestamp'])}</td>
                  <td>{log.service}</td>
                  <td className="log-level">{log.level}</td>
                  <td className="sentiment">{log.ai_sentiment} ({log.ai_sentiment_score.toFixed(2)})</td>
                  <td>{log.message}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}

export default App;