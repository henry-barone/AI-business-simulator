
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const SandboxControls = () => {
  const [priceValue, setPriceValue] = useState(30);
  const [marketingValue, setMarketingValue] = useState(500);

  const handlePriceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value);
    setPriceValue(value);
    
    // Update the span element for external access
    const priceSpan = document.getElementById('price-value');
    if (priceSpan) {
      priceSpan.textContent = `$${value}`;
    }
  };

  const handleMarketingChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value);
    setMarketingValue(value);
    
    // Update the span element for external access
    const marketingSpan = document.getElementById('marketing-value');
    if (marketingSpan) {
      marketingSpan.textContent = `$${value}`;
    }
  };

  return (
    <Card className="h-fit bg-card/50 backdrop-blur-sm border-border/50">
      <CardHeader>
        <CardTitle className="text-xl font-semibold">Sandbox Simulator</CardTitle>
        <p className="text-sm text-muted-foreground leading-relaxed">
          Use these controls to see how changing key variables can impact a sample business in real-time.
        </p>
      </CardHeader>
      <CardContent className="space-y-8">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <label htmlFor="price-slider" className="text-sm font-medium">
              Product Price ($)
            </label>
            <div className="text-sm text-muted-foreground">
              Current Price: <span id="price-value" className="text-foreground font-medium">${priceValue}</span>
            </div>
          </div>
          <input
            type="range"
            id="price-slider"
            min="10"
            max="100"
            value={priceValue}
            onChange={handlePriceChange}
            className="custom-slider"
          />
        </div>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <label htmlFor="marketing-slider" className="text-sm font-medium">
              Monthly Marketing Spend ($)
            </label>
            <div className="text-sm text-muted-foreground">
              Current Spend: <span id="marketing-value" className="text-foreground font-medium">${marketingValue}</span>
            </div>
          </div>
          <input
            type="range"
            id="marketing-slider"
            min="0"
            max="2000"
            value={marketingValue}
            onChange={handleMarketingChange}
            className="custom-slider"
          />
        </div>
      </CardContent>
    </Card>
  );
};

export default SandboxControls;
