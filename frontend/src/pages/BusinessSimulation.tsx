
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowRight, Download, Calendar, RotateCcw } from 'lucide-react';
import { API_BASE_URL } from '@/lib/api';
import CompanySetup from '@/components/CompanySetup';
import FileUpload from '@/components/FileUpload';
import DynamicQuestionnaire from '@/components/DynamicQuestionnaire';
import SimulationDashboard from '@/components/SimulationDashboard';
import PDFReportGenerator from '@/components/PDFReportGenerator';
import { businessSimulationState, type CompanyData } from '@/lib/businessSimulationState';

type SimulationStep = 'landing' | 'setup' | 'upload' | 'questionnaire' | 'processing' | 'results';

const BusinessSimulation = () => {
  const [currentStep, setCurrentStep] = useState<SimulationStep>('landing');
  const [companyData, setCompanyData] = useState<CompanyData | null>(null);
  const [fullReportData, setFullReportData] = useState<any>(null);

  // Initialize state from localStorage on component mount
  useEffect(() => {
    const savedState = businessSimulationState.getState();
    
    if (savedState.companyData) {
      setCompanyData(savedState.companyData);
    }
    
    if (savedState.fullReportData) {
      setFullReportData(savedState.fullReportData);
    }
    
    // Set the appropriate step based on saved state
    const appropriateStep = businessSimulationState.getCurrentStep();
    setCurrentStep(appropriateStep);
  }, []);

  const handleCompanySetup = (data: CompanyData) => {
    setCompanyData(data);
    businessSimulationState.updateCompanyData(data);
    setCurrentStep('upload');
  };

  const handleUploadSuccess = () => {
    setCurrentStep('questionnaire');
  };

  // Handle each questionnaire answer and update simulation
  const handleQuestionAnswered = async (answers: Record<string, string>, questionCount: number) => {
    // Save questionnaire progress
    businessSimulationState.updateQuestionnaireData(answers, questionCount);
    
    // Trigger simulation update every few questions or when significant answers are provided
    if (questionCount >= 3 && questionCount % 3 === 0) { // Update every 3 questions
      await updateSimulationWithCurrentAnswers(answers, questionCount);
    }
  };

  // Function to update simulation based on current questionnaire answers
  const updateSimulationWithCurrentAnswers = async (answers: Record<string, string>, questionCount: number) => {
    if (!companyData?.id) return;

    try {
      // Extract key answers for simulation parameters
      const employeeCount = answers['q3'] || '1-10';
      const productionVolume = answers['q5'] || 'Under 100 units';
      const automationLevel = answers['q8'] || 'Paper/Manual';

      // Create enhanced simulation with questionnaire data
      const response = await fetch(`${API_BASE_URL}/companies/${companyData.id}/enhanced-simulation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          automation_levels: {
            labor: questionCount >= 8 ? 0.3 : 0.1, // Increase automation suggestion as more questions answered
            quality: questionCount >= 4 ? 0.4 : 0.2,
            inventory: questionCount >= 9 ? 0.3 : 0.1,
            service: 0.2
          },
          projection_months: 24,
          production_volume: productionVolume,
          employee_count: employeeCount,
          automation_level: automationLevel,
          questionnaire_progress: {
            answers,
            completion_percentage: (questionCount / 12) * 100
          }
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const newSimulationData = { 
          ...data.data, 
          simulation_id: data.simulation_id,
          questionnaire_progress: questionCount 
        };
        
        businessSimulationState.updateSimulationData(newSimulationData);
      }
    } catch (error) {
      console.warn('Failed to update simulation with questionnaire answers:', error);
    }
  };

  const handleQuestionnaireComplete = async () => {
    setCurrentStep('processing');
    
    try {
      // Get final questionnaire answers
      const savedState = businessSimulationState.getState();
      const answers = savedState.questionnaireData?.answers || {};
      
      // Trigger final simulation update with complete questionnaire data
      await updateSimulationWithCurrentAnswers(answers, 12);
      
      // Mark questionnaire as completed with timestamp
      businessSimulationState.updateQuestionnaireData(answers, 12);
      
      setTimeout(() => {
        setCurrentStep('results');
      }, 2000);
    } catch (error) {
      console.error('Error creating final simulation:', error);
      alert('Network error creating simulation. Please check your connection and try again.');
      setCurrentStep('questionnaire');
      return;
    }
  };

  // Function to restart the questionnaire
  const handleRestartQuestionnaire = () => {
    businessSimulationState.clearQuestionnaireData();
    setFullReportData(null);
    setCurrentStep('questionnaire');
  };


  const renderStep = () => {
    switch (currentStep) {
      case 'landing':
        return (
          <div className="text-center space-y-8">
            <Card className="professional-card">
              <CardContent className="p-12">
                <h1 className="text-5xl font-bold professional-heading mb-6">
                  AI-Powered Business Optimization
                </h1>
                <p className="text-xl professional-text mb-8 max-w-3xl mx-auto">
                  Discover how artificial intelligence can transform your business operations, reduce costs, and increase efficiency. Get personalized recommendations based on your actual financial data.
                </p>
                <div className="grid md:grid-cols-3 gap-6 mb-8">
                  <div className="bg-gray-50 p-6 rounded-lg">
                    <h3 className="font-semibold text-gray-900 mb-2">Upload Your Data</h3>
                    <p className="text-sm text-gray-600">Share your P&L statement for AI analysis</p>
                  </div>
                  <div className="bg-gray-50 p-6 rounded-lg">
                    <h3 className="font-semibold text-gray-900 mb-2">Answer Questions</h3>
                    <p className="text-sm text-gray-600">Tell us about your business operations</p>
                  </div>
                  <div className="bg-gray-50 p-6 rounded-lg">
                    <h3 className="font-semibold text-gray-900 mb-2">Get Results</h3>
                    <p className="text-sm text-gray-600">Receive AI-powered optimization recommendations</p>
                  </div>
                </div>
                <Button
                  onClick={() => setCurrentStep('setup')}
                  className="professional-button text-lg px-8 py-4"
                >
                  Get Started
                  <ArrowRight className="ml-2 w-5 h-5" />
                </Button>
              </CardContent>
            </Card>
          </div>
        );

      case 'setup':
        return <CompanySetup onComplete={handleCompanySetup} />;

      case 'upload':
        return (
          <div className="max-w-2xl mx-auto space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold professional-heading mb-4">
                Upload Your P&L Statement
              </h2>
              <p className="professional-text">
                Upload your profit and loss statement so our AI can analyze your business finances and identify optimization opportunities.
              </p>
            </div>
            <FileUpload
              companyId={companyData?.id || ''}
              onUploadSuccess={handleUploadSuccess}
            />
          </div>
        );

      case 'questionnaire':
        return (
          <div className="max-w-2xl mx-auto space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold professional-heading mb-4">
                Business Assessment
              </h2>
              <p className="professional-text">
                Help us understand your business better by answering a few questions about your operations.
              </p>
            </div>
            <DynamicQuestionnaire
              companyId={companyData?.id || ''}
              onComplete={handleQuestionnaireComplete}
              onQuestionAnswered={handleQuestionAnswered}
            />
          </div>
        );

      case 'processing':
        return (
          <Card className="professional-card max-w-2xl mx-auto">
            <CardContent className="p-12 text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-600 mx-auto mb-6"></div>
              <h2 className="text-2xl font-bold professional-heading mb-4">
                AI Analysis in Progress
              </h2>
              <p className="professional-text mb-6">
                Our AI is analyzing your business data to identify optimization opportunities and calculate potential savings.
              </p>
              <div className="space-y-2 text-sm professional-text">
                <p>✓ Processing financial data</p>
                <p>✓ Analyzing operational patterns</p>
                <p>✓ Generating recommendations</p>
                <p className="text-purple-600">• Creating simulation results...</p>
              </div>
            </CardContent>
          </Card>
        );

      case 'results':
        return (
          <div className="space-y-8">
            <div className="text-center mb-8">
              <h2 className="text-4xl font-bold professional-heading mb-4">
                Your Business Optimization Results
              </h2>
              <p className="professional-text">
                Based on your data, here's how AI can transform your business operations.
              </p>
            </div>

            <div className="w-full">
              <SimulationDashboard 
                companyId={companyData?.id || ''} 
                companyName={companyData?.name}
                onDataLoaded={setFullReportData}
              />
            </div>

            <Card className="professional-card">
              <CardHeader>
                <CardTitle className="professional-heading">Next Steps</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col sm:flex-row gap-4">
                  <Button 
                    className="professional-button flex items-center gap-2"
                    onClick={() => {
                      console.log('Book Consultation clicked');
                      window.open('https://cal.com/jochem-spaik/discovery', '_blank');
                    }}
                  >
                    <Calendar className="w-4 h-4" />
                    Book Consultation
                  </Button>
                  {fullReportData && (
                    <PDFReportGenerator
                      data={fullReportData}
                      companyName={companyData?.name || 'Unknown Company'}
                      onGenerate={() => console.log('Generating full report PDF...')}
                      buttonText="Download Report"
                      buttonVariant="outline"
                      buttonClassName="border-purple-600 text-purple-600 hover:bg-purple-50"
                    />
                  )}
                  <Button 
                    variant="outline"
                    className="flex items-center gap-2 border-orange-600 text-orange-600 hover:bg-orange-50"
                    onClick={handleRestartQuestionnaire}
                  >
                    <RotateCcw className="w-4 h-4" />
                    Retake Assessment
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="container mx-auto px-6 py-16">
      {renderStep()}
    </div>
  );
};

export default BusinessSimulation;
