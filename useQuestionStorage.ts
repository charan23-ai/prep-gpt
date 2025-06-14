
import { useState, useEffect } from 'react';

interface StoredQuestion {
  id: string;
  question: string;
  answer: string;
  timestamp: string;
  category?: string;
}

export const useQuestionStorage = () => {
  const [storedQuestions, setStoredQuestions] = useState<StoredQuestion[]>([]);

  useEffect(() => {
    const saved = localStorage.getItem('prepgpt-questions');
    if (saved) {
      try {
        setStoredQuestions(JSON.parse(saved));
      } catch (error) {
        console.error('Error loading stored questions:', error);
      }
    }
  }, []);

  const saveQuestion = (question: string, answer: string, category?: string) => {
    const newQuestion: StoredQuestion = {
      id: Date.now().toString(),
      question,
      answer,
      timestamp: new Date().toISOString(),
      category
    };

    const updated = [newQuestion, ...storedQuestions];
    setStoredQuestions(updated);
    localStorage.setItem('prepgpt-questions', JSON.stringify(updated));
  };

  const deleteQuestion = (id: string) => {
    const updated = storedQuestions.filter(q => q.id !== id);
    setStoredQuestions(updated);
    localStorage.setItem('prepgpt-questions', JSON.stringify(updated));
  };

  const clearAllQuestions = () => {
    setStoredQuestions([]);
    localStorage.removeItem('prepgpt-questions');
  };

  return {
    storedQuestions,
    saveQuestion,
    deleteQuestion,
    clearAllQuestions
  };
};
