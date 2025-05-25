import React, { useState } from 'react';
import SurveyForm from './components/SurveyForm';
import SurveyList from './components/SurveyList';
import './App.css'; // You can add some basic styling

function App() {
  const [latestSurvey, setLatestSurvey] = useState(null);

  const handleSurveyCreated = (survey) => {
    setLatestSurvey(survey); // Trigger SurveyList update
  };

  // These handlers can be used if App needs to know about updates/deletions
  const handleSurveyUpdated = (updatedSurvey) => {
    console.log('Survey updated in App:', updatedSurvey);
    setLatestSurvey(updatedSurvey); // This will re-render list with updated item
  };

  const handleSurveyDeleted = (deletedSurveyId) => {
    console.log('Survey deleted in App:', deletedSurveyId);
    // If SurveyList doesn't refetch on its own, you might need to trigger a refetch here
    // or filter out the deleted survey from a shared state if App manages the survey list.
    // For now, SurveyList handles its own refetch on delete.
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Google Forms Creator & Review</h1>
      </header>
      <main>
        <SurveyForm onSurveyCreated={handleSurveyCreated} />
        <hr />
        <SurveyList 
          newSurvey={latestSurvey} 
          onSurveyUpdated={handleSurveyUpdated}
          onSurveyDeleted={handleSurveyDeleted}
        />
      </main>
    </div>
  );
}

export default App;