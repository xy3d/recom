// src/App.js
import React, { useState } from 'react';
import UserForm from './components/UserForm';
import Recommendations from './components/Recommendations';
import Container from '@mui/material/Container';

import './App.css'; // Import your custom CSS file

function App() {
  const [userId, setUserId] = useState('');

  const handleUserSubmit = (userId) => {
    setUserId(userId);
  };

  return (
    <Container disableGutters className="app-container">
      <h1 className="app-title">Product Recommendations</h1>
      <UserForm onSubmit={handleUserSubmit} />
      {userId && <Recommendations userId={userId} />}
    </Container>
  );
}

export default App;
