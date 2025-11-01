import React from 'react';
import ReactDOM from 'react-dom/client';
// We deleted the import for './index.css'
import App from './App';
// We deleted the import for 'reportWebVitals'

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// We deleted the call to reportWebVitals()