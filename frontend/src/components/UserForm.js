// src/components/UserForm.js
import React, { useState } from 'react';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import './UserForm.css'; // Import the CSS file

const UserForm = ({ onSubmit }) => {
  const [userId, setUserId] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit(userId);
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <h2>Enter User ID</h2>
      <form onSubmit={handleSubmit}>
        <TextField
          label="User ID"
          variant="outlined"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
        />
        <Button type="submit" variant="contained" color="primary" sx={{ marginTop: 2 }}>
          Get Recommendations
        </Button>
      </form>
    </Box>
  );
};

export default UserForm;
