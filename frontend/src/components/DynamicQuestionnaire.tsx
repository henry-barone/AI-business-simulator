
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { API_BASE_URL } from '@/lib/api';

interface Question {
  id: string;
  text: string;
  type: 'select' | 'radio' | 'textarea' | 'text' | 'cost_breakdown';
  options?: string[];
  required: boolean;
  placeholder?: string;
  fields?: { name: string; label: string }[];
}

interface QuestionnaireProps {
  companyId: string;
  onComplete: () => void;
  onQuestionAnswered?: (answers: Record<string, string>, questionCount: number) => void;
}

const DynamicQuestionnaire: React.FC<QuestionnaireProps> = ({ companyId, onComplete, onQuestionAnswered }) => {
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [questionIndex, setQuestionIndex] = useState(0);
  const [totalQuestions] = useState(12);
  const [loading, setLoading] = useState(false);
  const [canGoBack, setCanGoBack] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    fetchNextQuestion();
  }, []);

  const fetchNextQuestion = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/questionnaire/next`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          companyId,
          previousAnswers: answers 
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch question');
      }

      const data = await response.json();
      
      if (data.data.completed) {
        // Questionnaire complete
        onComplete();
      } else if (data.data.question) {
        setCurrentQuestion(data.data.question);
        setQuestionIndex(prev => prev + 1);
        setCanGoBack(questionIndex > 0);
      } else {
        // No more questions, questionnaire complete
        onComplete();
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load next question. Please try again.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async (answer: string) => {
    if (!currentQuestion) return;

    const newAnswers = { ...answers, [currentQuestion.id]: answer };
    setAnswers(newAnswers);

    try {
      const response = await fetch(`${API_BASE_URL}/companies/${companyId}/questionnaire`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          questionId: currentQuestion.id,
          answer: answer
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit answer');
      }

      // Notify parent component about the new answer
      if (onQuestionAnswered) {
        onQuestionAnswered(newAnswers, Object.keys(newAnswers).length);
      }

      // Fetch next question
      await fetchNextQuestion();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to submit answer. Please try again.",
        variant: "destructive"
      });
    }
  };

  const handleNext = () => {
    const answer = answers[currentQuestion?.id || ''];
    if (currentQuestion?.required && !answer) {
      toast({
        title: "Required field",
        description: "Please answer this question before continuing.",
        variant: "destructive"
      });
      return;
    }

    // Special validation for cost breakdown question
    if (currentQuestion?.type === 'cost_breakdown' && currentQuestion?.id === 'q11') {
      try {
        const costData = JSON.parse(answer);
        const total = costData.labor + costData.materials + costData.overhead;
        if (Math.abs(total - 100) > 0.1) {
          toast({
            title: "Invalid percentage",
            description: "The three percentages must sum to 100%.",
            variant: "destructive"
          });
          return;
        }
      } catch (e) {
        toast({
          title: "Invalid data",
          description: "Please fill in all percentage fields.",
          variant: "destructive"
        });
        return;
      }
    }

    submitAnswer(answer);
  };

  const handlePrevious = () => {
    if (questionIndex > 1) {
      setQuestionIndex(prev => prev - 1);
      // In a real implementation, you'd fetch the previous question
      // For now, we'll just show a message
      toast({
        title: "Navigation",
        description: "Previous question navigation would be implemented here.",
      });
    }
  };

  const renderQuestionInput = () => {
    if (!currentQuestion) return null;

    const currentAnswer = answers[currentQuestion.id] || '';

    switch (currentQuestion.type) {
      case 'select':
        return (
          <div className="space-y-2">
            <Label htmlFor="answer">{currentQuestion.text}</Label>
            <select
              id="answer"
              value={currentAnswer}
              onChange={(e) => setAnswers(prev => ({ ...prev, [currentQuestion.id]: e.target.value }))}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="">Select an option...</option>
              {currentQuestion.options?.map((option, index) => (
                <option key={index} value={option}>{option}</option>
              ))}
            </select>
          </div>
        );

      case 'radio':
        return (
          <div className="space-y-4">
            <Label>{currentQuestion.text}</Label>
            <div className="space-y-2">
              {currentQuestion.options?.map((option, index) => (
                <label key={index} className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    name="answer"
                    value={option}
                    checked={currentAnswer === option}
                    onChange={(e) => setAnswers(prev => ({ ...prev, [currentQuestion.id]: e.target.value }))}
                    className="w-4 h-4 text-purple-600 focus:ring-purple-500"
                  />
                  <span className="text-gray-700">{option}</span>
                </label>
              ))}
            </div>
          </div>
        );

      case 'textarea':
        return (
          <div className="space-y-2">
            <Label htmlFor="answer">{currentQuestion.text}</Label>
            <Textarea
              id="answer"
              value={currentAnswer}
              onChange={(e) => setAnswers(prev => ({ ...prev, [currentQuestion.id]: e.target.value }))}
              placeholder={currentQuestion.placeholder || "Enter your answer..."}
              rows={4}
            />
          </div>
        );

      case 'text':
        return (
          <div className="space-y-2">
            <Label htmlFor="answer">{currentQuestion.text}</Label>
            <Input
              id="answer"
              value={currentAnswer}
              onChange={(e) => setAnswers(prev => ({ ...prev, [currentQuestion.id]: e.target.value }))}
              placeholder={currentQuestion.placeholder || "Enter your answer..."}
            />
          </div>
        );

      case 'cost_breakdown':
        const costData = (() => {
          try {
            return currentAnswer ? JSON.parse(currentAnswer) : { labor: '', materials: '', overhead: '' };
          } catch {
            return { labor: '', materials: '', overhead: '' };
          }
        })();
        
        const updateCostData = (field: string, value: string) => {
          const numValue = value === '' ? 0 : parseFloat(value) || 0;
          const newData = { ...costData, [field]: numValue };
          setAnswers(prev => ({ ...prev, [currentQuestion.id]: JSON.stringify(newData) }));
        };

        const total = (costData.labor || 0) + (costData.materials || 0) + (costData.overhead || 0);

        return (
          <div className="space-y-4">
            <Label>{currentQuestion.text}</Label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {currentQuestion.fields?.map((field) => (
                <div key={field.name} className="space-y-2">
                  <Label htmlFor={field.name}>{field.label} %</Label>
                  <Input
                    id={field.name}
                    type="number"
                    min="0"
                    max="100"
                    value={costData[field.name] || ''}
                    onChange={(e) => updateCostData(field.name, e.target.value)}
                    placeholder="0"
                  />
                </div>
              ))}
            </div>
            <div className={`text-sm font-medium ${Math.abs(total - 100) < 0.1 ? 'text-green-600' : 'text-red-600'}`}>
              Total: {total.toFixed(1)}% {Math.abs(total - 100) < 0.1 ? '✓' : '(must equal 100%)'}
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  if (loading && !currentQuestion) {
    return (
      <Card className="professional-card">
        <CardContent className="p-8 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="professional-text">Loading questions...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="professional-card">
      <CardHeader>
        <CardTitle className="professional-heading">Business Assessment</CardTitle>
        <div className="space-y-2">
          <div className="flex justify-between text-sm professional-text">
            <span>Question {questionIndex} of {totalQuestions}</span>
            <span>{Math.round((questionIndex / totalQuestions) * 100)}% complete</span>
          </div>
          <Progress value={(questionIndex / totalQuestions) * 100} className="w-full" />
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {currentQuestion && (
          <>
            <div className="space-y-4">
              {renderQuestionInput()}
            </div>
            
            <div className="flex justify-between pt-4">
              <Button
                variant="outline"
                onClick={handlePrevious}
                disabled={!canGoBack}
                className="flex items-center gap-2"
              >
                <ChevronLeft className="w-4 h-4" />
                Previous
              </Button>
              
              <Button
                onClick={handleNext}
                disabled={loading}
                className="professional-button flex items-center gap-2"
              >
                {loading ? 'Submitting...' : 'Next'}
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default DynamicQuestionnaire;
