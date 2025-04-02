import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './LifestyleHistory.css';

function LifestyleHistory() {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedEntry, setSelectedEntry] = useState(null);

  useEffect(() => {
    // For testing without backend - use mock data
    const mockEntries = [
      {
        id: 1,
        date: '2023-05-15T00:00:00Z',
        sleep: 7.5,
        water: 8,
        mood: 'good',
        exercise: {
          type: 'Running',
          duration: 30,
          intensity: 'moderate'
        },
        nutrition: {
          fruits: 3,
          vegetables: 4,
          processedFoods: 1
        },
        notes: 'Felt energetic today after my morning run'
      },
      {
        id: 2,
        date: '2023-05-14T00:00:00Z',
        sleep: 6,
        water: 5,
        mood: 'tired',
        exercise: {
          type: 'Walking',
          duration: 20,
          intensity: 'light'
        },
        nutrition: {
          fruits: 2,
          vegetables: 3,
          processedFoods: 2
        },
        notes: 'Didnt sleep well last night'
      }
    ];

    // Uncomment this when you want to connect to real backend
    /*
    const fetchEntries = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/get-lifestyle-entries/');
        setEntries(response.data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };
    fetchEntries();
    */

    // For now, use mock data
    setEntries(mockEntries);
    setLoading(false);
  }, []);

  if (loading) return <div className="loading">Loading entries...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="lifestyle-history">
      <h2>Your Lifestyle History</h2>
      
      <div className="history-container">
        <div className="entries-list">
          {entries.map(entry => (
            <div 
              key={entry.id} 
              className={`entry-card ${selectedEntry?.id === entry.id ? 'selected' : ''}`}
              onClick={() => setSelectedEntry(entry)}
            >
              <h3>{new Date(entry.date).toLocaleDateString()}</h3>
              <div className="entry-summary">
                <span>😴 {entry.sleep} hrs</span>
                <span>💧 {entry.water} glasses</span>
                <span>🏃‍♂️ {entry.exercise.duration}min {entry.exercise.type}</span>
              </div>
            </div>
          ))}
        </div>
        
        {selectedEntry && (
          <div className="entry-detail">
            <h3>Details for {new Date(selectedEntry.date).toLocaleDateString()}</h3>
            <div className="detail-section">
              <h4>Basic Metrics</h4>
              <p><strong>Sleep:</strong> {selectedEntry.sleep} hours</p>
              <p><strong>Water:</strong> {selectedEntry.water} glasses</p>
              <p><strong>Mood:</strong> {selectedEntry.mood}</p>
            </div>
            
            <div className="detail-section">
              <h4>Exercise</h4>
              <p><strong>Type:</strong> {selectedEntry.exercise.type}</p>
              <p><strong>Duration:</strong> {selectedEntry.exercise.duration} minutes</p>
              <p><strong>Intensity:</strong> {selectedEntry.exercise.intensity}</p>
            </div>
            
            <div className="detail-section">
              <h4>Nutrition</h4>
              <p><strong>Fruits:</strong> {selectedEntry.nutrition.fruits} servings</p>
              <p><strong>Vegetables:</strong> {selectedEntry.nutrition.vegetables} servings</p>
              <p><strong>Processed Foods:</strong> {selectedEntry.nutrition.processedFoods} servings</p>
            </div>
            
            {selectedEntry.notes && (
              <div className="detail-section">
                <h4>Notes</h4>
                <p>{selectedEntry.notes}</p>
              </div>
            )}
          </div>
        )}

        {entries.length === 0 && !loading && (
          <div className="no-entries">
            <p>No lifestyle entries found.</p>
            <p>Start by adding your first entry!</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default LifestyleHistory;