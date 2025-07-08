
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowRight, Download, Calendar } from 'lucide-react';
import { API_BASE_URL } from '@/lib/api';
import CompanySetup from '@/components/CompanySetup';
import FileUpload from '@/components/FileUpload';
import DynamicQuestionnaire from '@/components/DynamicQuestionnaire';
import SimulationDashboard from '@/components/SimulationDashboard';
import AdjustmentSliders from '@/components/AdjustmentSliders';
import PDFReportGenerator from '@/components/PDFReportGenerator';

type SimulationStep = 'landing' | 'setup' | 'upload' | 'questionnaire' | 'processing' | 'results';

interface CompanyData {
  id: string;
  name: string;
  industry: string;
}

interface SimulationData {
  simulation_id?: number;
  [key: string]: any;
}

const BusinessSimulation = () => {
  const [currentStep, setCurrentStep] = useState<SimulationStep>('landing');
  const [companyData, setCompanyData] = useState<CompanyData | null>(null);
  const [simulationData, setSimulationData] = useState<SimulationData | null>(null);
  const [fullReportData, setFullReportData] = useState<any>(null);

  const handleCompanySetup = (data: CompanyData) => {
    setCompanyData(data);
    setCurrentStep('upload');
  };

  const handleUploadSuccess = (data: any) => {
    setCurrentStep('questionnaire');
  };

  const handleQuestionnaireComplete = async () => {
    setCurrentStep('processing');
    
    try {
      // Create enhanced simulation after questionnaire completion
      const response = await fetch(`${API_BASE_URL}/companies/${companyData?.id}/enhanced-simulation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          automation_levels: {
            labor: 0.5,
            quality: 0.5,
            inventory: 0.5,
            service: 0.5
          },
          projection_months: 24,
          production_volume: "1000-10000 units/day",
          employee_count: "51-200",
          automation_level: "Some automated tools"
        }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Simulation created successfully:', data);
        setSimulationData({ 
          ...data.data, 
          simulation_id: data.simulation_id 
        });
        setTimeout(() => {
          setCurrentStep('results');
        }, 2000);
      } else {
        const errorText = await response.text();
        console.error('Failed to create simulation:', response.status, errorText);
        alert('Failed to create simulation. Please try again.');
        setCurrentStep('questionnaire');
        return;
      }
    } catch (error) {
      console.error('Error creating simulation:', error);
      alert('Network error creating simulation. Please check your connection and try again.');
      setCurrentStep('questionnaire');
      return;
    }
  };

  const handleSimulationUpdate = (data: any) => {
    setSimulationData(data);
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

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <SimulationDashboard 
                  companyId={companyData?.id || ''} 
                  companyName={companyData?.name}
                  onDataLoaded={setFullReportData}
                />
              </div>
              <div>
                <AdjustmentSliders
                  simulationId={simulationData?.simulation_id?.toString() || "1"}
                  onUpdate={handleSimulationUpdate}
                />
              </div>
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
