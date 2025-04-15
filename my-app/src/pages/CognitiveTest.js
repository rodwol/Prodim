import React, { useState, useEffect, useMemo, useCallback } from 'react';
import axios from 'axios';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import './CognitiveTest.css';

// Helper to get CSRF token from cookies
function getCSRFToken() {
  const name = 'csrftoken';
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    cookie = cookie.trim();
    if (cookie.startsWith(name + '=')) {
      return decodeURIComponent(cookie.substring(name.length + 1));
    }
  }
  return '';
}

function CognitiveTest() {
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [score, setScore] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [matchResult, setMatchResult] = useState({ valid: false, feedback: '' });
  const [submissionError, setSubmissionError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { transcript, listening, resetTranscript } = useSpeechRecognition();
  const currentQuestion = questions[currentQuestionIndex] || {};

  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        const response = await axios.get(
          'http://localhost:8000/api/cognitive-tests-questions/',
          {
            withCredentials: true,
            headers: {
              'X-CSRFToken': getCSRFToken(),
              'Content-Type': 'application/json'
            }
          }
        );
        setQuestions(response.data.questions || []);
      } catch (err) {
        setError(err.response?.data?.message || err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchQuestions();
  }, []);

  useEffect(() => {
    if (!currentQuestion.type) return;

    if (['reading', 'verbal_recall'].includes(currentQuestion.type)) {
      resetTranscript();
      SpeechRecognition.startListening({ continuous: true });
    }

    return () => {
      SpeechRecognition.stopListening();
    };
  }, [currentQuestionIndex, currentQuestion.type, resetTranscript]);

  useEffect(() => {
    if (transcript && currentQuestion.type) {
      const result = verifyResponse(transcript);
      setMatchResult(result);
      if (result.valid) {
        handleAnswerChange(transcript);
      }
    }
  }, [transcript, currentQuestion]);

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

    if (spoken.includes(expected)) {
      return { valid: true, feedback: '✅ Perfect recall!' };
    }

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
    setAnswers((prev) => ({
      ...prev,
      [currentQuestion.id]: {
        question_id: currentQuestion.id,
        answer: answer,
        type: currentQuestion.type
      }
    }));
  };

  const handleSubmit = async () => {
    setSubmissionError(null);
    setIsSubmitting(true);
  
    try {
      const formattedAnswers = Object.values(answers).map(answer => ({
        question_id: answer.question_id,
        answer: answer.answer,
        type: answer.type
      }));
  
      const response = await axios.post(
        'http://localhost:8000/api/submit_cognitive_test',
        { answers: formattedAnswers },
        {
          withCredentials: true,
          headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json'
          }
        }
      );
  
      if (response.data.error) {
        setSubmissionError(response.data.error);
      } else {
        setScore(response.data.score);
      }
    } catch (err) {
      setSubmissionError(
        err.response?.data?.message || 
        err.response?.data?.error || 
        'Failed to submit test. Please try again.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };
  
  const requiresVerbalResponse = ['reading', 'verbal_recall'].includes(currentQuestion.type);
  const canProceed = requiresVerbalResponse ?
    (matchResult.valid && answers[currentQuestion.id]) :
    answers[currentQuestion.id];
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
                checked={answers[currentQuestion.id]?.answer === option}
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
          <button
            onClick={handleSubmit}
            disabled={!canProceed || isSubmitting}
          >
            {isSubmitting ? 'Submitting...' : 'Submit Test'}
          </button>
        )}
      </div>

      {submissionError && (
        <div className="error-message">
          <p>Error: {submissionError}</p>
        </div>
      )}

      {score !== null && (
        <div className="results" data-score={
          score >= questions.length * 0.9 ? "excellent" :
            score >= questions.length * 0.7 ? "good" :
              score >= questions.length * 0.5 ? "average" : "poor"
        }>
          <h3>Your Score: {score}/{questions.length}</h3>
          <p>
            {score >= questions.length * 0.9 ? "Excellent! Your cognitive abilities are outstanding." :
              score >= questions.length * 0.7 ? "Good job! Your cognitive abilities are above average." :
                score >= questions.length * 0.5 ? "Average performance. There's room for improvement." :
                  "Below average. Consider practicing or consulting with a specialist."}
          </p>
          {score < questions.length * 0.7 && (
            <p className="suggestion">
              Tip: Regular mental exercises and a healthy lifestyle can help improve cognitive function.
            </p>
          )}
        </div>
      )}
    </div>
  );
}

export default CognitiveTest;
