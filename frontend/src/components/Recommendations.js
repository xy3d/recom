// src/components/Recommendations.js
import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import Box from '@mui/material/Box';
import './Recommendations.css'; // Import the CSS file

const Recommendations = ({ userId }) => {
  const [recommendations, setRecommendations] = useState([]);

  const fetchRecommendations = useCallback(async () => {
    try {
      const response = await axios.get(`/recommendations?user_id=${userId}`);
      setRecommendations(response.data.recommendations);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      setRecommendations([]);
    }
  }, [userId]);

  useEffect(() => {
    // Fetch recommendations when the component mounts or when userId changes
    fetchRecommendations();
  }, [fetchRecommendations]);

  return (
    <Box className="RecommendationList">
      <h2>Recommendations</h2>
      <ul>
        {recommendations.map((recommendation) => (
          <li key={recommendation.product_id}>
            {recommendation.product_name}
          </li>
        ))}
      </ul>
    </Box>
  );
};

export default Recommendations;
