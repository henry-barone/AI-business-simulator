
import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Sparkles, TrendingUp, DollarSign, Calculator } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';
import { 
  extractPLData, 
  generateForecastData, 
  calculateSummaryMetrics,
  type PLData,
  type ForecastData,
  type OperationalFactors
} from '@/utils/simulationUtils';

interface SandboxProps {
  simulationData?: any;
}

const Sandbox: React.FC<SandboxProps> = ({ simulationData }) => {
  // Extract P&L data from simulation or use defaults
  const baselineData: PLData = useMemo(() => extractPLData(simulationData), [simulationData]);
  // Slider state - calculate ranges based on baseline data
  const priceRange = {
    min: Math.round(baselineData.averagePrice * 0.7),
    max: Math.round(baselineData.averagePrice * 1.3)
  };
  const marketingRange = {
    min: 0,
    max: Math.max(baselineData.marketingSpend * 3, 50000)
  };
  
  const [priceValue, setPriceValue] = useState(baselineData.averagePrice);
  const [marketingValue, setMarketingValue] = useState(baselineData.marketingSpend);
  
  // New operational factor states
  const [laborAutomation, setLaborAutomation] = useState(10); // 10% baseline
  const [productionEfficiency, setProductionEfficiency] = useState(100); // 100% baseline
  const [inventoryTurnover, setInventoryTurnover] = useState(6); // 6x baseline

  // Update slider values when baseline data changes
  useEffect(() => {
    setPriceValue(baselineData.averagePrice);
    setMarketingValue(baselineData.marketingSpend);
  }, [baselineData]);
  
  // Create operational factors object
  const operationalFactors: OperationalFactors = useMemo(() => ({
    laborAutomationLevel: laborAutomation,
    productionEfficiency: productionEfficiency,
    inventoryTurnoverRate: inventoryTurnover
  }), [laborAutomation, productionEfficiency, inventoryTurnover]);
  
  // Generate forecast data with seasonal variation
  const forecastData = useMemo(() => 
    generateForecastData(baselineData, priceValue, marketingValue, operationalFactors), 
    [baselineData, priceValue, marketingValue, operationalFactors]
  );
  
  // Calculate summary metrics
  const summaryMetrics = useMemo(() => 
    calculateSummaryMetrics(baselineData, forecastData, marketingValue, operationalFactors),
    [baselineData, forecastData, marketingValue, operationalFactors]
  );
  
  const handlePriceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPriceValue(parseInt(e.target.value));
  };

  const handleMarketingChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setMarketingValue(parseInt(e.target.value));
  };
  
  const handleLaborAutomationChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLaborAutomation(parseInt(e.target.value));
  };
  
  const handleProductionEfficiencyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setProductionEfficiency(parseInt(e.target.value));
  };
  
  const handleInventoryTurnoverChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInventoryTurnover(parseInt(e.target.value));
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
                    Current: $<span className="text-gray-900 font-bold text-lg">{priceValue}</span>
                  </div>
                </div>
                <input
                  type="range"
                  id="price-slider"
                  min={priceRange.min}
                  max={priceRange.max}
                  value={priceValue}
                  onChange={handlePriceChange}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider-thumb"
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>${priceRange.min}</span>
                  <span className="text-gray-700 font-medium">Baseline: ${baselineData.averagePrice}</span>
                  <span>${priceRange.max}</span>
                </div>
              </div>
              
              {/* Marketing Control */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <label htmlFor="marketing-slider" className="text-sm font-semibold text-gray-900">
                    Monthly Marketing Spend ($)
                  </label>
                  <div className="text-sm professional-text">
                    Current: $<span className="text-gray-900 font-bold text-lg">{marketingValue.toLocaleString()}</span>
                  </div>
                </div>
                <input
                  type="range"
                  id="marketing-slider"
                  min={marketingRange.min}
                  max={marketingRange.max}
                  value={marketingValue}
                  onChange={handleMarketingChange}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider-thumb"
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>$0</span>
                  <span className="text-gray-700 font-medium">Baseline: ${baselineData.marketingSpend.toLocaleString()}</span>
                  <span>${(marketingRange.max / 1000).toFixed(0)}k</span>
                </div>
              </div>
              
              {/* Labor Automation Level Control */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <label htmlFor="automation-slider" className="text-sm font-semibold text-gray-900" title="Percentage of manual labor processes automated">
                    Labor Automation Level (%)
                  </label>
                  <div className="text-sm professional-text">
                    Current: <span className="text-gray-900 font-bold text-lg">{laborAutomation}%</span>
                  </div>
                </div>
                <input
                  type="range"
                  id="automation-slider"
                  min="0"
                  max="80"
                  value={laborAutomation}
                  onChange={handleLaborAutomationChange}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider-thumb"
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>0%</span>
                  <span className="text-gray-700 font-medium">Baseline: 10%</span>
                  <span>80%</span>
                </div>
              </div>
              
              {/* Production Efficiency Control */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <label htmlFor="efficiency-slider" className="text-sm font-semibold text-gray-900" title="Overall production process efficiency relative to baseline">
                    Production Efficiency (%)
                  </label>
                  <div className="text-sm professional-text">
                    Current: <span className="text-gray-900 font-bold text-lg">{productionEfficiency}%</span>
                  </div>
                </div>
                <input
                  type="range"
                  id="efficiency-slider"
                  min="100"
                  max="150"
                  value={productionEfficiency}
                  onChange={handleProductionEfficiencyChange}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider-thumb"
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>100%</span>
                  <span className="text-gray-700 font-medium">Baseline: 100%</span>
                  <span>150%</span>
                </div>
              </div>
              
              {/* Inventory Turnover Rate Control */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <label htmlFor="turnover-slider" className="text-sm font-semibold text-gray-900" title="How many times inventory is sold and replaced annually">
                    Inventory Turnover Rate (x/year)
                  </label>
                  <div className="text-sm professional-text">
                    Current: <span className="text-gray-900 font-bold text-lg">{inventoryTurnover}x per year</span>
                  </div>
                </div>
                <input
                  type="range"
                  id="turnover-slider"
                  min="6"
                  max="12"
                  value={inventoryTurnover}
                  onChange={handleInventoryTurnoverChange}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider-thumb"
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>6x</span>
                  <span className="text-gray-700 font-medium">Baseline: 6x</span>
                  <span>12x</span>
                </div>
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
              <div className="w-full h-96">
                <ChartContainer
                  config={{
                    originalProfit: {
                      label: "Original Forecast",
                      color: "hsl(var(--muted-foreground))"
                    },
                    adjustedProfit: {
                      label: "Adjusted Forecast",
                      color: "hsl(220, 70%, 50%)"
                    },
                    confidence: {
                      label: "Confidence Band",
                      color: "hsl(220, 70%, 50%)"
                    }
                  }}
                >
                  <LineChart data={forecastData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis 
                      tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
                    />
                    <ChartTooltip 
                      content={<ChartTooltipContent 
                        formatter={(value, name) => [
                          `$${Number(value).toLocaleString()}`,
                          name === 'originalProfit' ? 'Original Forecast' : 'Adjusted Forecast'
                        ]}
                      />}
                    />
                    
                    {/* Confidence bands */}
                    <defs>
                      <linearGradient id="originalConfidence" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="hsl(var(--muted-foreground))" stopOpacity={0.2}/>
                        <stop offset="95%" stopColor="hsl(var(--muted-foreground))" stopOpacity={0.1}/>
                      </linearGradient>
                      <linearGradient id="adjustedConfidence" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="hsl(220, 70%, 50%)" stopOpacity={0.2}/>
                        <stop offset="95%" stopColor="hsl(220, 70%, 50%)" stopOpacity={0.1}/>
                      </linearGradient>
                    </defs>
                    
                    {/* Original forecast line (grayed out) */}
                    <Line 
                      type="monotone" 
                      dataKey="originalProfit" 
                      stroke="hsl(var(--muted-foreground))"
                      strokeWidth={2}
                      strokeDasharray="5 5"
                      dot={false}
                    />
                    
                    {/* Adjusted forecast line (primary) */}
                    <Line 
                      type="monotone" 
                      dataKey="adjustedProfit" 
                      stroke="hsl(220, 70%, 50%)"
                      strokeWidth={3}
                      dot={{ fill: "hsl(220, 70%, 50%)", strokeWidth: 2, r: 4 }}
                    />
                    
                    {/* Zero line reference */}
                    <ReferenceLine y={0} stroke="hsl(var(--muted-foreground))" strokeDasharray="2 2" />
                  </LineChart>
                </ChartContainer>
              </div>
            </CardContent>
            
            {/* Legend */}
            <div className="mt-4 flex justify-center">
              <Card className="professional-card">
                <CardContent className="p-4">
                  <div className="flex items-center gap-8 text-sm">
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-0.5 bg-gray-400 border-dashed border-t-2"></div>
                      <span className="text-gray-600">Original Forecast</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-0.5 bg-blue-500"></div>
                      <span className="text-blue-600">Adjusted Forecast</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-2 bg-blue-100 rounded-sm"></div>
                      <span className="text-gray-600">Confidence Band (±15%)</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </Card>
        </div>
        
        {/* Right Column - Simulation Summary */}
        <div className="lg:col-span-3 space-y-6">
          {/* Summary Metrics */}
          <Card className="professional-card">
            <CardHeader>
              <CardTitle className="text-xl professional-heading flex items-center gap-2">
                <Calculator className="w-5 h-5" />
                Impact Summary
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 gap-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-600 mb-1">Current Monthly Profit</div>
                  <div className="text-2xl font-bold text-gray-900">${summaryMetrics.currentProfit.toLocaleString()}</div>
                </div>
                
                <div className="bg-blue-50 rounded-lg p-4">
                  <div className="text-sm text-blue-600 mb-1">Projected Monthly Profit</div>
                  <div className="text-2xl font-bold text-blue-700">${summaryMetrics.newProfit.toLocaleString()}</div>
                </div>
                
                <div className={`rounded-lg p-4 ${summaryMetrics.monthlyDifference >= 0 ? 'bg-green-50' : 'bg-red-50'}`}>
                  <div className={`text-sm mb-1 ${summaryMetrics.monthlyDifference >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    Monthly Impact
                  </div>
                  <div className={`text-2xl font-bold flex items-center gap-2 ${summaryMetrics.monthlyDifference >= 0 ? 'text-green-700' : 'text-red-700'}`}>
                    {summaryMetrics.monthlyDifference >= 0 ? '+' : ''}${summaryMetrics.monthlyDifference.toLocaleString()}
                    <TrendingUp className="w-5 h-5" />
                  </div>
                </div>
                
                <div className="bg-purple-50 rounded-lg p-4">
                  <div className="text-sm text-purple-600 mb-1">12-Month Impact</div>
                  <div className="text-xl font-bold text-purple-700">
                    {summaryMetrics.annualDifference >= 0 ? '+' : ''}${summaryMetrics.annualDifference.toLocaleString()}
                  </div>
                </div>
                
                {summaryMetrics.totalInvestment > 0 && (
                  <div className="bg-orange-50 rounded-lg p-4">
                    <div className="text-sm text-orange-600 mb-1">Total Investment</div>
                    <div className="text-xl font-bold text-orange-700">${summaryMetrics.totalInvestment.toLocaleString()}</div>
                  </div>
                )}
                
                {summaryMetrics.totalInvestment > 0 && (
                  <div className="bg-yellow-50 rounded-lg p-4">
                    <div className="text-sm text-yellow-600 mb-1">Overall ROI</div>
                    <div className="text-xl font-bold text-yellow-700">{summaryMetrics.roi}%</div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
          
          {/* AI Advisor */}
          <Card className="professional-card">
            <CardHeader>
              <CardTitle className="text-xl professional-heading flex items-center gap-2">
                <Sparkles className="w-5 h-5" />
                AI Insights
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-gray-50 rounded-lg p-4 border border-gray-100">
                <div className="text-sm text-gray-600 mb-2">AI Recommendations</div>
                <div className="space-y-2">
                  <p className="text-sm professional-text">
                    {priceValue > baselineData.averagePrice 
                      ? `Higher pricing (+${(((priceValue - baselineData.averagePrice) / baselineData.averagePrice) * 100).toFixed(1)}%) may reduce demand but increase margins.`
                      : priceValue < baselineData.averagePrice 
                      ? `Lower pricing (-${(((baselineData.averagePrice - priceValue) / baselineData.averagePrice) * 100).toFixed(1)}%) should increase demand volume.`
                      : 'Current pricing at baseline level.'}
                  </p>
                  <p className="text-sm professional-text">
                    {marketingValue > baselineData.marketingSpend 
                      ? `Marketing investment shows diminishing returns beyond $${(baselineData.marketingSpend / 1000).toFixed(0)}k/month.`
                      : 'Consider increasing marketing spend for potential revenue growth.'}
                  </p>
                  <p className="text-sm professional-text">
                    {laborAutomation > 40 && productionEfficiency < 120 
                      ? 'High automation with low efficiency gains suggests focusing on process optimization first.'
                      : laborAutomation > 60 
                      ? 'High automation levels may require significant change management investment.'
                      : laborAutomation < 30 
                      ? 'Consider gradual automation to reduce labor costs while maintaining quality.'
                      : 'Current automation level is well-balanced.'}
                  </p>
                  <p className="text-sm professional-text">
                    {inventoryTurnover > 10 
                      ? 'High inventory turnover requires robust supply chain management.'
                      : inventoryTurnover < 8 
                      ? 'Consider improving inventory management to reduce carrying costs.'
                      : 'Inventory turnover rate is within optimal range.'}
                  </p>
                </div>
              </div>
              
              <Button className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white py-3 px-4 font-semibold rounded-lg transform hover:scale-105 transition-all duration-200 flex items-center justify-center gap-2">
                <DollarSign className="w-4 h-4" />
                Get Full Analysis
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Sandbox;
