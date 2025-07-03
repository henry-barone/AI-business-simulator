
import React from 'react';
import Header from '@/components/Header';
import SandboxControls from '@/components/SandboxControls';
import ProfitForecast from '@/components/ProfitForecast';
import AIAdvisor from '@/components/AIAdvisor';

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column - Sandbox Controls */}
          <div className="lg:col-span-3">
            <SandboxControls />
          </div>
          
          {/* Center Column - Profit Forecast */}
          <div className="lg:col-span-6">
            <ProfitForecast />
          </div>
          
          {/* Right Column - AI Advisor */}
          <div className="lg:col-span-3">
            <AIAdvisor />
          </div>
        </div>
      </main>
    </div>
  );
};

export default Index;
