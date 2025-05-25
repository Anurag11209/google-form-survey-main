import React, { useState } from 'react';
import { createSurvey } from '../services/api';

function SurveyForm({ onSurveyCreated }) {
  const [questionsText, setQuestionsText] = useState('');
  const [title, setTitle] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!questionsText.trim()) {
      setError('Please enter some questions.');
      return;
    }
    setError('');
    setIsLoading(true);
    try {
      const surveyData = { questions_text: questionsText };
      if (title.trim()) {
        surveyData.title = title.trim();
      }
      const response = await createSurvey(surveyData);
      onSurveyCreated(response.data);
      setQuestionsText('');
      setTitle('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create survey. Ensure backend is running and Google Auth is complete.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Create New Survey</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <div>
        <label htmlFor="title">Survey Title (Optional):</label>
        <input
          type="text"
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          disabled={isLoading}
        />
      </div>
      <div>
        <label htmlFor="questions">Questions (one per line):</label>
        <textarea
          id="questions"
          value={questionsText}
          onChange={(e) => setQuestionsText(e.target.value)}
          rows="10"
          cols="50"
          required
          disabled={isLoading}
        />
      </div>
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Creating...' : 'Create Survey'}
      </button>
    </form>
  );
}

export default SurveyForm;