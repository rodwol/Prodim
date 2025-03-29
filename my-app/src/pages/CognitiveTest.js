import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './CognitiveTest.css';

function CognitiveTest() {
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [score, setScore] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch questions
  useEffect(() => {
    axios.get('http://localhost:8000/api/cognitive-test-questions/')
      .then((response) => {
        setQuestions(response.data.questions);
        setLoading(false);
      })
      .catch((error) => {
        setError(error.message);
        setLoading(false);
      });
  }, []);

  const handleAnswerChange = (answer) => {
    setAnswers({
      ...answers,
      [questions[currentQuestionIndex].id]: answer
    });
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleSubmit = async () => {
    const userAnswers = Object.keys(answers).map((questionId) => ({
      question_id: questionId,
      answer: answers[questionId],
    }));

    try {
      const response = await axios.post('http://localhost:8000/api/evaluate-cognitive-test/', {
        answers: userAnswers,
      });
      setScore(response.data.score);
    } catch (error) {
      console.error('Error evaluating test:', error);
    }
  };

  if (loading) return <div className="loading">Loading questions...</div>;
  if (error) return <div className="error">Error loading questions: {error}</div>;
  if (questions.length === 0) return <div className="no-questions">No questions available</div>;

  const currentQuestion = questions[currentQuestionIndex];
  const isLastQuestion = currentQuestionIndex === questions.length - 1;
  const isAnswered = answers[currentQuestion.id] !== undefined;

  return (
    <div className="cognitive-test">
      <h3>Cognitive Ability Test</h3>
      
      {/* Progress indicator */}
      <div className="progress-indicator">
        Question {currentQuestionIndex + 1} of {questions.length}
      </div>
      
      {/* Current question */}
      <div className="question">
        <p>{currentQuestion.question}</p>
        {currentQuestion.options.map((option) => (
          <div key={option}>
            <label>
              <input
                type="radio"
                name={`question-${currentQuestion.id}`}
                value={option}
                checked={answers[currentQuestion.id] === option}
                onChange={() => handleAnswerChange(option)}
              />
              {option}
            </label>
          </div>
        ))}
      </div>
      
      {/* Navigation buttons */}
      <div className="navigation-buttons">
        {currentQuestionIndex > 0 && (
          <button 
            onClick={handlePreviousQuestion}
            className="nav-button prev-button"
          >
            Previous
          </button>
        )}
        
        {!isLastQuestion ? (
          <button
            onClick={handleNextQuestion}
            className="nav-button next-button"
            disabled={!isAnswered}
          >
            Next
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            className="submit-button"
            disabled={!isAnswered}
          >
            Submit Test
          </button>
        )}
      </div>
      
      {/* Score display */}
      {score !== null && (
        <div className="score-display">
          <h3>Your Results</h3>
          <div className="score-value">
            {score}<span className="score-total">/{questions.length}</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default CognitiveTest;