import React, { useState } from 'react';

function LifestyleTracker() {
  const [diet, setDiet] = useState('');
  const [exercise, setExercise] = useState('');
  const [sleep, setSleep] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // Save lifestyle data (you can send it to the backend here)
    console.log({ diet, exercise, sleep });
    alert('Lifestyle data saved!');
  };

  return (
    <div className="lifestyle-tracker">
      <h3>Lifestyle Tracker</h3>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Diet:</label>
          <input
            type="text"
            value={diet}
            onChange={(e) => setDiet(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Exercise:</label>
          <input
            type="text"
            value={exercise}
            onChange={(e) => setExercise(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Sleep (hours):</label>
          <input
            type="number"
            value={sleep}
            onChange={(e) => setSleep(e.target.value)}
            required
          />
        </div>
        <button type="submit">Save</button>
      </form>
    </div>
  );
}

export default LifestyleTracker;