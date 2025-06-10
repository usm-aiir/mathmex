import React, { useEffect, useState } from 'react';
import logo from './logo.svg';
import './App.css';

// Main App component
function App() {
  // State to hold the message from the backend
  const [backendMessage, setBackendMessage] = useState('');

  // useEffect runs once when the component mounts
  useEffect(() => {
    // Fetch data from the Flask backend
    // Uses environment variable if set, otherwise defaults to localhost:5000
    fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/`)
      .then(res => res.text()) // Parse response as text
      .then(data => setBackendMessage(data)) // Set the backend message in state
      .catch(() => setBackendMessage('Error connecting to backend')); // Handle errors
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        {/* React logo */}
        <img src={logo} className="App-logo" alt="logo" />
        {/* Display the backend message */}
        <p>
          Backend says: <strong>{backendMessage}</strong>
        </p>
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        {/* Link to React documentation */}
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}

export default App;
