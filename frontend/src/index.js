// src/index.js
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import axios from 'axios';

// Set the base URL for Axios requests
axios.defaults.baseURL = 'http://127.0.0.1:5000/'; // Replace with your Flask API address and port

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);
