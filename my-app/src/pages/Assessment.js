import React, { useState } from "react";

const Assessment = () => {
  const [score, setScore] = useState(null);

  const takeTest = () => {
    const randomScore = Math.floor(Math.random() * 100);
    setScore(randomScore);
  };

  return (
    <div>
      <h1>Cognitive Assessment</h1>
      <button onClick={takeTest}>Start Test</button>
      {score !== null && <p>Your score: {score}/100</p>}
    </div>
  );
};

export default Assessment;