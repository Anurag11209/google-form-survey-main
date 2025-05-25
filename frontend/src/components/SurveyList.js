import React, { useState, useEffect, useCallback } from 'react';
import { getSurveys } from '../services/api';
import SurveyItem from './SurveyItem';

function SurveyList({ newSurvey, onSurveyUpdated, onSurveyDeleted }) {
  const [surveys, setSurveys] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchSurveys = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await getSurveys();
      setSurveys(response.data.sort((a,b) => b.id - a.id)); // Show newest first
    } catch (err) {
      setError('Failed to fetch surveys.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSurveys();
  }, [fetchSurveys]);

  useEffect(() => {
    if (newSurvey) {
      // Add new survey to the top of the list or refetch
      setSurveys(prevSurveys => [newSurvey, ...prevSurveys.filter(s => s.id !== newSurvey.id)].sort((a,b) => b.id - a.id));
    }
  }, [newSurvey]);

  const handleSurveyUpdate = (updatedSurvey) => {
    setSurveys(prevSurveys =>
      prevSurveys.map(s => (s.id === updatedSurvey.id ? updatedSurvey : s)).sort((a,b) => b.id - a.id)
    );
    onSurveyUpdated(updatedSurvey); // Propagate up if needed
  };

  const handleSurveyDelete = (deletedSurveyId) => {
     // Option 1: Refetch list
     // fetchSurveys(); 
     // Option 2: Update local state (if backend soft deletes and returns updated item)
     // For hard delete or simple removal from list:
     // setSurveys(prevSurveys => prevSurveys.filter(s => s.id !== deletedSurveyId));
     // For soft delete, we expect the backend to mark it as deleted, so we refetch or update.
     // Let's refetch to get the 'deleted' status properly.
     fetchSurveys();
     onSurveyDeleted(deletedSurveyId); // Propagate up if needed
  };


  if (isLoading) return <p>Loading surveys...</p>;
  if (error) return <p style={{ color: 'red' }}>{error}</p>;

  return (
    <div>
      <h2>Existing Surveys</h2>
      {surveys.length === 0 && <p>No surveys created yet.</p>}
      {surveys.map(survey => (
        <SurveyItem 
            key={survey.id} 
            survey={survey} 
            onSurveyUpdated={handleSurveyUpdate}
            onSurveyDeleted={handleSurveyDelete}
        />
      ))}
    </div>
  );
}

export default SurveyList;