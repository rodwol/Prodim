import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import axios from 'axios';
import './LifestyleTracker.css';

function LifestyleTracker() {
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    sleep: '',
    water: '',
    steps: '',
    exercise: '',
    mood: '5',
    nutrition: ''
  });
  const [trackerData, setTrackerData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch existing data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/lifestyle-data/');
        setTrackerData(response.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(
        'http://localhost:8000/api/lifestyle-data/',
        formData,
        {
          headers: {
            'Authorization': `Token ${localStorage.getItem('token')}`, // If using token auth
            'Content-Type': 'application/json'
          }
        }
      );
      
      // Update the tracker data with the response
      setTrackerData(response.data);
      
      // Reset form
      setFormData({
        date: new Date().toISOString().split('T')[0],
        sleep: '',
        water: '',
        steps: '',
        exercise: '',
        mood: '5',
        nutrition: ''
      });
      
    } catch (error) {
      console.error("Error saving data:", error);
      alert("Failed to save entry. Please try again.");
    }
  };

  // Prepare chart data
  const chartData = trackerData.map(item => ({
    date: item.date,
    sleep: parseInt(item.sleep),
    water: parseInt(item.water),
    steps: parseInt(item.steps)/1000, // Convert to thousands
    mood: parseInt(item.mood)
  }));

  return (
    <div className="lifestyle-tracker">
      <h2>Lifestyle Tracker</h2>
      
      <div className="tracker-container">
        <form onSubmit={handleSubmit} className="tracker-form">
          <h3>Daily Input</h3>
          
          <div className="form-group">
            <label>Date:</label>
            <input 
              type="date" 
              name="date" 
              value={formData.date}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Sleep (hours):</label>
              <input
                type="number"
                name="sleep"
                min="0"
                max="24"
                value={formData.sleep}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label>Water (glasses):</label>
              <input
                type="number"
                name="water"
                min="0"
                value={formData.water}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Steps:</label>
              <input
                type="number"
                name="steps"
                min="0"
                value={formData.steps}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label>Exercise (minutes):</label>
              <input
                type="number"
                name="exercise"
                min="0"
                value={formData.exercise}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label>Mood (1-10):</label>
            <input
              type="range"
              name="mood"
              min="1"
              max="10"
              value={formData.mood}
              onChange={handleChange}
            />
            <span className="mood-value">{formData.mood}</span>
          </div>

          <div className="form-group">
            <label>Nutrition Notes:</label>
            <textarea
              name="nutrition"
              value={formData.nutrition}
              onChange={handleChange}
              placeholder="What did you eat today?"
            />
          </div>

          <button type="submit" className="submit-btn">Save Entry</button>
        </form>

        <div className="tracker-visualization">
          <h3>Progress Overview</h3>
          
          {isLoading ? (
            <p>Loading data...</p>
          ) : trackerData.length > 0 ? (
            <>
              <div className="chart-container">
                <LineChart width={500} height={300} data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="sleep" stroke="#8884d8" />
                  <Line type="monotone" dataKey="water" stroke="#82ca9d" />
                  <Line type="monotone" dataKey="steps" stroke="#ffc658" />
                  <Line type="monotone" dataKey="mood" stroke="#ff8042" />
                </LineChart>
              </div>

              <div className="stats-grid">
                <div className="stat-card">
                  <h4>Avg. Sleep</h4>
                  <p>{Math.round(trackerData.reduce((sum, item) => sum + parseInt(item.sleep), 0) / trackerData.length)} hrs</p>
                </div>
                <div className="stat-card">
                  <h4>Avg. Water</h4>
                  <p>{Math.round(trackerData.reduce((sum, item) => sum + parseInt(item.water), 0) / trackerData.length)} glasses</p>
                </div>
                <div className="stat-card">
                  <h4>Avg. Steps</h4>
                  <p>{Math.round(trackerData.reduce((sum, item) => sum + parseInt(item.steps), 0) / trackerData.length).toLocaleString()}</p>
                </div>
                <div className="stat-card">
                  <h4>Avg. Mood</h4>
                  <p>{Math.round(trackerData.reduce((sum, item) => sum + parseInt(item.mood), 0) / trackerData.length)}/10</p>
                </div>
              </div>
            </>
          ) : (
            <p>No data available. Add your first entry!</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default LifestyleTracker;