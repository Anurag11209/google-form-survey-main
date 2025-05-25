import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000'; // FastAPI backend URL

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const createSurvey = (surveyData) => {
  return apiClient.post('/surveys/', surveyData);
};

export const getSurveys = () => {
  return apiClient.get('/surveys/');
};

export const getSurveyById = (surveyId) => {
  return apiClient.get(`/surveys/${surveyId}/`);
};

export const approveSurvey = (surveyId, recipientEmail) => {
  return apiClient.post(`/surveys/${surveyId}/approve`, { recipient_email: recipientEmail });
};

export const deleteSurvey = (surveyId) => {
  return apiClient.delete(`/surveys/${surveyId}/`);
};

export default apiClient;