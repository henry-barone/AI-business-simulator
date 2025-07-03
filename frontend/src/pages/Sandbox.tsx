
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Sparkles } from 'lucide-react';

const Sandbox = () => {
  const [priceValue, setPriceValue] = useState(30);
  const [marketingValue, setMarketingValue] = useState(500);

  const handlePriceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value);
    setPriceValue(value);
    
    const priceSpan = document.getElementById('price-value');
    if (priceSpan) {
      priceSpan.textContent = value.toString();
    }
  };

  const handleMarketingChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value);
    setMarketingValue(value);
    
    const marketingSpan = document.getElementById('marketing-value');
    if (marketingSpan) {
      marketingSpan.textContent = value.toString();
    }
  };

  return (
    <div className="container mx-auto px-6 py-16">
      <div className="mb-12 text-center">
        <h1 className="text-5xl font-bold professional-heading mb-6">Business Simulation Sandbox</h1>
        <p className="text-xl professional-text max-w-3xl mx-auto">
          Experiment with key business variables and see their impact in real-time
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column - Sandbox Controls */}
        <div className="lg:col-span-3">
          <Card className="professional-card h-fit">
            <CardHeader>
              <CardTitle className="text-2xl professional-heading">Sandbox Simulator</CardTitle>
              <p className="professional-text">
                Use these controls to see how changing key variables can impact a sample business in real-time.
              </p>
            </CardHeader>
            <CardContent className="space-y-10">
              {/* Price Control */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <label htmlFor="price-slider" className="text-sm font-semibold text-gray-900">
                    Product Price ($)
                  </label>
                  <div className="text-sm professional-text">
                    Current Price: $<span id="price-value" className="text-gray-900 font-bold text-lg">{priceValue}</span>
                  </div>
                </div>
                <input
                  type="range"
                  id="price-slider"
                  min="10"
                  max="100"
                  value={priceValue}
                  onChange={handlePriceChange}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider-thumb"
                />
              </div>
              
              {/* Marketing Control */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <label htmlFor="marketing-slider" className="text-sm font-semibold text-gray-900">
                    Monthly Marketing Spend ($)
                  </label>
                  <div className="text-sm professional-text">
                    Current Spend: $<span id="marketing-value" className="text-gray-900 font-bold text-lg">{marketingValue}</span>
                  </div>
                </div>
                <input
                  type="range"
                  id="marketing-slider"
                  min="0"
                  max="2000"
                  value={marketingValue}
                  onChange={handleMarketingChange}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider-thumb"
                />
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* Center Column - Profit Forecast (Widest) */}
        <div className="lg:col-span-6">
          <Card className="professional-card">
            <CardHeader>
              <CardTitle className="text-2xl professional-heading">Projected 12-Month Profit Forecast</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="w-full h-96 flex items-center justify-center border border-gray-200 rounded-lg bg-gray-50">
                <canvas
                  id="profitChart"
                  width="600"
                  height="400"
                  className="max-w-full max-h-full"
                />
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* Right Column - AI Advisor */}
        <div className="lg:col-span-3">
          <Card className="professional-card h-fit">
            <CardHeader>
              <CardTitle className="text-2xl professional-heading">AI Business Advisor</CardTitle>
            </CardHeader>
            <CardContent className="space-y-8">
              <div className="bg-gray-50 rounded-lg p-6 border border-gray-100">
                <p className="professional-text">
                  Your personalized recommendations for automation and process improvements will appear here once you create your digital twin.
                </p>
              </div>
              
              <Button className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white py-4 px-6 font-semibold rounded-lg transform hover:scale-105 transition-all duration-200 flex items-center justify-center gap-2">
                <Sparkles className="w-4 h-4" />
                Create Your Company's Digital Twin
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Sandbox;
