import React, { useState } from 'react';
import { approveSurvey, deleteSurvey as apiDeleteSurvey } from '../services/api';

function SurveyItem({ survey, onSurveyUpdated, onSurveyDeleted }) {
  const [recipientEmail, setRecipientEmail] = useState('');
  const [isApproving, setIsApproving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState('');
  const [showEmailInput, setShowEmailInput] = useState(false);

  const handleApprove = async () => {
    if (!recipientEmail.trim()) {
      setError('Please enter a recipient email.');
      return;
    }
    setError('');
    setIsApproving(true);
    try {
      const response = await approveSurvey(survey.id, recipientEmail);
      onSurveyUpdated(response.data);
      setShowEmailInput(false); // Hide input after success
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to approve survey.');
      console.error(err);
    } finally {
      setIsApproving(false);
    }
  };

  const handleDelete = async () => {
    if (window.confirm(`Are you sure you want to delete survey "${survey.title || 'Untitled'}"?`)) {
      setIsDeleting(true);
      setError('');
      try {
        await apiDeleteSurvey(survey.id);
        onSurveyDeleted(survey.id);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to delete survey.');
        console.error(err);
      } finally {
        setIsDeleting(false);
      }
    }
  };
  
  const cardStyle = {
    border: '1px solid #ccc',
    padding: '15px',
    margin: '10px',
    borderRadius: '5px',
    backgroundColor: survey.status === 'approved' ? '#e6ffe6' : survey.status === 'deleted' ? '#ffe6e6' : '#fff',
  };

  return (
    <div style={cardStyle}>
      <h3>{survey.title || 'Untitled Survey'} (ID: {survey.id})</h3>
      <p>Status: <strong>{survey.status}</strong></p>
      {survey.form_url && (
        <p>
          Form URL: <a href={survey.form_url} target="_blank" rel="noopener noreferrer">{survey.form_url}</a>
        </p>
      )}
      {survey.recipient_email && <p>Sent to: {survey.recipient_email}</p>}
      <details>
        <summary>View Questions</summary>
        <pre style={{whiteSpace: 'pre-wrap', wordBreak: 'break-all'}}>{survey.questions_text}</pre>
      </details>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {survey.status === 'draft' && (
        <div>
          {!showEmailInput && (
            <button onClick={() => setShowEmailInput(true)} disabled={isApproving}>
              Approve
            </button>
          )}
          {showEmailInput && (
            <div>
              <input
                type="email"
                value={recipientEmail}
                onChange={(e) => setRecipientEmail(e.target.value)}
                placeholder="Recipient Email"
                disabled={isApproving}
              />
              <button onClick={handleApprove} disabled={isApproving || !recipientEmail.trim()}>
                {isApproving ? 'Approving...' : 'Send Approval Email'}
              </button>
              <button onClick={() => setShowEmailInput(false)} disabled={isApproving} style={{marginLeft: '5px'}}>
                Cancel
              </button>
            </div>
          )}
        </div>
      )}

      {survey.status !== 'deleted' && (
        <button onClick={handleDelete} disabled={isDeleting} style={{backgroundColor: '#ffdddd', marginLeft: survey.status === 'draft' ? '10px' : '0px'}}>
          {isDeleting ? 'Deleting...' : 'Delete Survey'}
        </button>
      )}
    </div>
  );
}

export default SurveyItem;