import React, { useState, useEffect, useMemo, useCallback } from 'react';
import axios from 'axios';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import './CognitiveTest.css';

function CognitiveTest() {
  // State management
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [score, setScore] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [matchResult, setMatchResult] = useState({ valid: false, feedback: '' });

  // Speech recognition
  const { transcript, listening, resetTranscript } = useSpeechRecognition();
  const currentQuestion = questions[currentQuestionIndex] || {};

  // Fetch questions - Ensure this runs only once
  useEffect(() => {
    console.log('Fetching questions...');
    const fetchQuestions = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/cognitive-tests-questions/');
        console.log('Questions fetched:', response.data);
        setQuestions(response.data.questions);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchQuestions();
  }, []); // Empty dependency array ensures effect runs only once when component mounts

  // Handle speech recognition based on question type
  useEffect(() => {
    if (!currentQuestion.type) return;

    if (currentQuestion.type === 'reading' || currentQuestion.type === 'verbal_recall') {
      resetTranscript();
      console.log('Starting Speech Recognition...');
      SpeechRecognition.startListening({ continuous: true });
    }

    return () => {
      console.log('Stopping Speech Recognition...');
      SpeechRecognition.stopListening();
    };
  }, [currentQuestionIndex, currentQuestion.type, resetTranscript]);

  // Verify response based on question type
  useEffect(() => {
    if (transcript && currentQuestion.type) {
      const result = verifyResponse(transcript);
      setMatchResult(result);
    }
  }, [transcript, currentQuestion]);

  // Memoize the verifyResponse function to avoid unnecessary recalculations
  const verifyResponse = useMemo(() => {
    return (spokenText) => {
      switch (currentQuestion.type) {
        case 'verbal_recall':
          return checkVerbalRecall(spokenText);
        case 'reading':
          return checkReading(spokenText);
        default:
          return { valid: true, feedback: '' };
      }
    };
  }, [currentQuestion]);

  const checkVerbalRecall = useCallback((spokenText) => {
    const normalize = (text) => text.toLowerCase().replace(/[^\w\s]/g, '');
    const spoken = normalize(spokenText);
    const expected = normalize(currentQuestion.expected_response);

    // Check for perfect match
    if (spoken.includes(expected)) {
      return { valid: true, feedback: '✅ Perfect recall!' };
    }

    // Check partial matches
    if (currentQuestion.partial_credit) {
      const bestMatch = currentQuestion.partial_credit.find((partial) =>
        spoken.includes(normalize(partial))
      );
      if (bestMatch) {
        return { valid: true, feedback: `⚠️ Partial: Got until ${bestMatch}` };
      }
    }

    return { valid: false, feedback: '❌ Try again' };
  }, [currentQuestion]);

  const checkReading = (spokenText) => {
    const questionWords = currentQuestion.question.toLowerCase().split(/\s+/);
    const spokenWords = spokenText.toLowerCase().split(/\s+/);
    const matchedWords = questionWords.filter((qWord) =>
      spokenWords.some((sWord) => sWord.includes(qWord))
    );
    const threshold = Math.max(2, questionWords.length * 0.6);
    const valid = matchedWords.length >= threshold;

    return {
      valid,
      feedback: valid ? '✅ Reading verified' : '❌ Please read the question carefully',
    };
  };

  // Navigation handlers
  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex((prev) => prev + 1);
      resetTranscript();
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex((prev) => prev - 1);
      resetTranscript();
    }
  };

  const handleAnswerChange = (answer) => {
    setAnswers((prev) => ({ ...prev, [currentQuestion.id]: answer }));
  };

  const handleSubmit = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/cognitive-tests-questions/', {
        answers: Object.entries(answers).map(([id, answer]) => ({ question_id: id, answer })),
      });
      setScore(response.data.score);
    } catch (err) {
      console.error('Evaluation error:', err);
    }
  };

  // Helper variables
  const requiresVerbalResponse = ['reading', 'verbal_recall'].includes(currentQuestion.type);
  const canProceed = requiresVerbalResponse ? matchResult.valid : answers[currentQuestion.id];
  const isLastQuestion = currentQuestionIndex === questions.length - 1;

  if (!SpeechRecognition.browserSupportsSpeechRecognition()) {
    return <div className="error">Browser doesn't support speech recognition</div>;
  }

  if (loading) return <div className="loading">Loading questions...</div>;
  if (error) return <div className="error">Error: {error}</div>;
  if (!currentQuestion.id) return <div>Loading question...</div>;

  return (
    <div className="cognitive-test">
      <h2>Cognitive Ability Test</h2>
      <div className="progress">Question {currentQuestionIndex + 1} of {questions.length}</div>

      <div className="question-container">
        <div className="question-text">
          <p>{currentQuestion.question}</p>
          {currentQuestion.options?.map((option) => (
            <label key={option}>
              <input
                type="radio"
                name={`q_${currentQuestion.id}`}
                checked={answers[currentQuestion.id] === option}
                onChange={() => handleAnswerChange(option)}
              />
              {option}
            </label>
          ))}
        </div>

        {requiresVerbalResponse && (
          <div className="verbal-section">
            <div className="verbal-controls">
              <button onClick={SpeechRecognition.startListening} disabled={listening}>
                {listening ? '🎤 Listening...' : '🎤 Start'}
              </button>
              <button onClick={SpeechRecognition.stopListening}>✋ Stop</button>
              <button onClick={resetTranscript}>🔄 Reset</button>
            </div>
            <div className="transcript">
              <p>You said: {transcript || '...'}</p>
              {matchResult.feedback && (
                <p className={`feedback ${matchResult.valid ? 'valid' : 'invalid'}`}>
                  {matchResult.feedback}
                </p>
              )}
            </div>
          </div>
        )}
      </div>

      <div className="navigation">
        {currentQuestionIndex > 0 && (
          <button onClick={handlePreviousQuestion}>← Previous</button>
        )}
        {!isLastQuestion ? (
          <button onClick={handleNextQuestion} disabled={!canProceed}>
            Next →
          </button>
        ) : (
          <button onClick={handleSubmit} disabled={!canProceed}>
            Submit Test
          </button>
        )}
      </div>

      {score !== null && (
        <div className="results">
          <h3>Your Score: {score}/{questions.length}</h3>
        </div>
      )}
    </div>
  );
}

export default CognitiveTest;