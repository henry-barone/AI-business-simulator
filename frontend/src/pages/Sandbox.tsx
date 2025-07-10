
import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Sparkles, TrendingUp, DollarSign, Calculator, ChevronDown, ChevronUp, Info, ArrowUp, ArrowDown, AlertCircle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';
import { 
  extractPLData, 
  generateForecastData, 
  calculateSummaryMetrics,
  calculateLaborAutomationImpact,
  calculateProductionEfficiencyImpact,
  calculateInventoryTurnoverImpact,
  type PLData,
  type ForecastData,
  type OperationalFactors
} from '@/utils/simulationUtils';
import { businessSimulationState } from '@/lib/businessSimulationState';

interface SandboxProps {
  simulationData?: any;
}

const Sandbox: React.FC<SandboxProps> = ({ simulationData }) => {
  // State to hold current simulation data and questionnaire data
  const [currentSimulationData, setCurrentSimulationData] = useState(() => {
    const storedState = businessSimulationState.getState();
    return simulationData || storedState.simulationData;
  });
  
  const [questionnaireState, setQuestionnaireState] = useState(() => {
    const storedState = businessSimulationState.getState();
    return {
      hasQuestionnaireData: storedState.questionnaireData && Object.keys(storedState.questionnaireData.answers).length > 0,
      isQuestionnaireCompleted: businessSimulationState.isQuestionnaireCompleted(),
      questionnaireData: storedState.questionnaireData
    };
  });

  // Listen for state changes
  useEffect(() => {
    const cleanup = businessSimulationState.addListener(() => {
      const newState = businessSimulationState.getState();
      
      // Update simulation data if it changed
      const newSimulationData = simulationData || newState.simulationData;
      if (newSimulationData !== currentSimulationData) {
        setCurrentSimulationData(newSimulationData);
      }
      
      // Update questionnaire state
      const newQuestionnaireState = {
        hasQuestionnaireData: newState.questionnaireData && Object.keys(newState.questionnaireData.answers).length > 0,
        isQuestionnaireCompleted: businessSimulationState.isQuestionnaireCompleted(),
        questionnaireData: newState.questionnaireData
      };
      
      setQuestionnaireState(newQuestionnaireState);
    });

    return cleanup;
  }, [simulationData, currentSimulationData]);

  // Use the reactive simulation data
  const activeSimulationData = currentSimulationData;
  
  // Extract P&L data from simulation or use defaults
  const baselineData: PLData = useMemo(() => extractPLData(activeSimulationData), [activeSimulationData]);
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
  
  // UI state
  const [isInvestmentBreakdownExpanded, setIsInvestmentBreakdownExpanded] = useState(false);

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
  
  // Calculate individual investment components for breakdown
  const investmentBreakdown = useMemo(() => {
    const automationImpact = calculateLaborAutomationImpact(baselineData, laborAutomation);
    const efficiencyImpact = calculateProductionEfficiencyImpact(baselineData, productionEfficiency);
    const inventoryImpact = calculateInventoryTurnoverImpact(baselineData, inventoryTurnover);
    const marketingCost = marketingValue - baselineData.marketingSpend;
    
    return {
      laborAutomationCost: automationImpact.automationInvestment || 0,
      productionEfficiencyCost: efficiencyImpact.implementationCost || 0,
      inventorySystemCost: inventoryImpact.implementationCost || 0,
      marketingSpendCost: Math.max(marketingCost, 0),
      totalMonthlyCost: (automationImpact.automationInvestment || 0) + 
                       (efficiencyImpact.implementationCost || 0) + 
                       (inventoryImpact.implementationCost || 0) + 
                       Math.max(marketingCost, 0)
    };
  }, [baselineData, laborAutomation, productionEfficiency, inventoryTurnover, marketingValue]);

  // Use the reactive questionnaire state
  const { hasQuestionnaireData, isQuestionnaireCompleted, questionnaireData } = questionnaireState;

  return (
    <div className="container mx-auto px-6 py-16">
      <div className="mb-12 text-center">
        <h1 className="text-5xl font-bold professional-heading mb-6">Business Simulation Sandbox</h1>
        <p className="text-xl professional-text max-w-3xl mx-auto">
          Experiment with key business variables and see their impact in real-time
        </p>
        
        {/* Show status of questionnaire data */}
        {hasQuestionnaireData && (
          <div className="mt-4 max-w-2xl mx-auto">
            <Card className={`${isQuestionnaireCompleted ? 'border-green-200 bg-green-50' : 'border-blue-200 bg-blue-50'}`}>
              <CardContent className="p-4">
                <div className="flex items-center justify-center gap-2 text-sm">
                  {isQuestionnaireCompleted ? (
                    <>
                      <Sparkles className="w-4 h-4 text-green-600" />
                      <span className="text-green-700 font-medium">
                        Using your completed business assessment data
                      </span>
                    </>
                  ) : (
                    <>
                      <AlertCircle className="w-4 h-4 text-blue-600" />
                      <span className="text-blue-700 font-medium">
                        Using partial assessment data ({Object.keys(questionnaireData?.answers || {}).length}/12 questions answered)
                      </span>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
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
                    Current: $<span className="text-black font-bold text-lg transition-all duration-300 ease-out">{priceValue}</span>
                  </div>
                </div>
                <div className="relative">
                  <input
                    type="range"
                    id="price-slider"
                    min={priceRange.min}
                    max={priceRange.max}
                    value={priceValue}
                    onChange={handlePriceChange}
                    className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer hover:bg-gray-300 transition-colors duration-200 slider-thumb"
                  />
                  {/* Baseline marker */}
                  <div 
                    className="absolute top-0 w-0.5 h-3 bg-gray-600 rounded-full pointer-events-none"
                    style={{ 
                      left: `${((baselineData.averagePrice - priceRange.min) / (priceRange.max - priceRange.min)) * 100}%`,
                      transform: 'translateX(-50%)'
                    }}
                  />
                </div>
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
                    Current: $<span className="text-black font-bold text-lg transition-all duration-300 ease-out">{marketingValue.toLocaleString()}</span>
                  </div>
                </div>
                <div className="relative">
                  <input
                    type="range"
                    id="marketing-slider"
                    min={marketingRange.min}
                    max={marketingRange.max}
                    value={marketingValue}
                    onChange={handleMarketingChange}
                    className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer hover:bg-gray-300 transition-colors duration-200 slider-thumb"
                  />
                  {/* Baseline marker */}
                  <div 
                    className="absolute top-0 w-0.5 h-3 bg-gray-600 rounded-full pointer-events-none"
                    style={{ 
                      left: `${((baselineData.marketingSpend - marketingRange.min) / (marketingRange.max - marketingRange.min)) * 100}%`,
                      transform: 'translateX(-50%)'
                    }}
                  />
                </div>
                <div className="flex justify-between text-xs text-gray-500">
                  <span>$0</span>
                  <span className="text-gray-700 font-medium">Baseline: ${baselineData.marketingSpend.toLocaleString()}</span>
                  <span>${(marketingRange.max / 1000).toFixed(0)}k</span>
                </div>
              </div>
              
              {/* Labor Automation Level Control */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <label htmlFor="automation-slider" className="text-sm font-semibold text-gray-900">
                    Labor Automation Level (%)
                  </label>
                  <div className="text-sm professional-text">
                    Current: <span className="text-black font-bold text-lg transition-all duration-300 ease-out">{laborAutomation}%</span>
                  </div>
                </div>
                <div className="relative">
                  <input
                    type="range"
                    id="automation-slider"
                    min="0"
                    max="80"
                    value={laborAutomation}
                    onChange={handleLaborAutomationChange}
                    className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer hover:bg-gray-300 transition-colors duration-200 slider-thumb"
                  />
                  {/* Baseline marker */}
                  <div 
                    className="absolute top-0 w-0.5 h-3 bg-gray-600 rounded-full pointer-events-none"
                    style={{ 
                      left: `${(10 / 80) * 100}%`,
                      transform: 'translateX(-50%)'
                    }}
                  />
                </div>
                <div className="flex justify-between text-xs text-gray-500">
                  <span>0%</span>
                  <span className="text-gray-700 font-medium">Baseline: 10%</span>
                  <span>80%</span>
                </div>
              </div>
              
              {/* Production Efficiency Control */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <label htmlFor="efficiency-slider" className="text-sm font-semibold text-gray-900">
                    Production Efficiency (%)
                  </label>
                  <div className="text-sm professional-text">
                    Current: <span className="text-black font-bold text-lg transition-all duration-300 ease-out">{productionEfficiency}%</span>
                  </div>
                </div>
                <div className="relative">
                  <input
                    type="range"
                    id="efficiency-slider"
                    min="100"
                    max="150"
                    value={productionEfficiency}
                    onChange={handleProductionEfficiencyChange}
                    className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer hover:bg-gray-300 transition-colors duration-200 slider-thumb"
                  />
                  {/* Baseline marker */}
                  <div 
                    className="absolute top-0 w-0.5 h-3 bg-gray-600 rounded-full pointer-events-none"
                    style={{ 
                      left: `${((100 - 100) / (150 - 100)) * 100}%`,
                      transform: 'translateX(-50%)'
                    }}
                  />
                </div>
                <div className="flex justify-between text-xs text-gray-500">
                  <span>100%</span>
                  <span className="text-gray-700 font-medium">Baseline: 100%</span>
                  <span>150%</span>
                </div>
              </div>
              
              {/* Inventory Turnover Rate Control */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <label htmlFor="turnover-slider" className="text-sm font-semibold text-gray-900">
                    Inventory Turnover Rate (x/year)
                  </label>
                  <div className="text-sm professional-text">
                    Current: <span className="text-black font-bold text-lg transition-all duration-300 ease-out">{inventoryTurnover}x</span>
                  </div>
                </div>
                <div className="relative">
                  <input
                    type="range"
                    id="turnover-slider"
                    min="6"
                    max="12"
                    value={inventoryTurnover}
                    onChange={handleInventoryTurnoverChange}
                    className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer hover:bg-gray-300 transition-colors duration-200 slider-thumb"
                  />
                  {/* Baseline marker */}
                  <div 
                    className="absolute top-0 w-0.5 h-3 bg-gray-600 rounded-full pointer-events-none"
                    style={{ 
                      left: `${((6 - 6) / (12 - 6)) * 100}%`,
                      transform: 'translateX(-50%)'
                    }}
                  />
                </div>
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
                {/* ROI Hero Section */}
                {summaryMetrics.totalInvestment > 0 && (
                  <div className="text-center p-6 rounded-xl border-2 border-dashed border-gray-200">
                    <div className="text-sm text-gray-600 mb-2">Overall ROI</div>
                    <div className={`inline-flex items-center px-6 py-3 rounded-full text-3xl font-bold transition-all duration-300 ease-out ${
                      summaryMetrics.roi >= 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {summaryMetrics.roi >= 0 ? '+' : ''}{summaryMetrics.roi}%
                    </div>
                  </div>
                )}
                
                {/* Projected Monthly Profit - Largest Metric */}
                <div className="bg-blue-50 rounded-lg p-4">
                  <div className="text-sm text-blue-600 mb-1">Projected Monthly Profit</div>
                  <div className="flex items-center justify-between">
                    <div className="text-4xl font-bold text-blue-700 transition-all duration-300 ease-out">${summaryMetrics.newProfit.toLocaleString()}</div>
                    <div className={`flex items-center text-lg font-semibold transition-all duration-300 ease-out ${
                      summaryMetrics.monthlyDifference >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {summaryMetrics.monthlyDifference >= 0 ? <ArrowUp className="w-5 h-5 mr-1 transition-transform duration-300" /> : <ArrowDown className="w-5 h-5 mr-1 transition-transform duration-300" />}
                      {summaryMetrics.monthlyDifference >= 0 ? '+' : ''}${Math.abs(summaryMetrics.monthlyDifference).toLocaleString()}
                    </div>
                  </div>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-600 mb-1">Current Monthly Profit</div>
                  <div className="text-2xl font-bold text-gray-900">${summaryMetrics.currentProfit.toLocaleString()}</div>
                </div>
                
                <div className="bg-purple-50 rounded-lg p-4">
                  <div className="text-sm text-purple-600 mb-1">12-Month Impact</div>
                  <div className="text-xl font-bold text-purple-700">
                    {summaryMetrics.annualDifference >= 0 ? '+' : ''}${summaryMetrics.annualDifference.toLocaleString()}
                  </div>
                </div>
                
                {/* Investment Breakdown Section */}
                {investmentBreakdown.totalMonthlyCost > 0 && (
                  <div className="bg-orange-50 rounded-lg p-4">
                    <div 
                      className="flex items-center justify-between cursor-pointer"
                      onClick={() => setIsInvestmentBreakdownExpanded(!isInvestmentBreakdownExpanded)}
                    >
                      <div>
                        <div className="text-sm text-orange-600 mb-1">Investment Breakdown</div>
                        <div className="text-lg font-bold text-orange-700">
                          Total Monthly Investment: ${investmentBreakdown.totalMonthlyCost.toLocaleString()}
                        </div>
                      </div>
                      <div className="ml-2">
                        {isInvestmentBreakdownExpanded ? (
                          <ChevronUp className="w-5 h-5 text-orange-600 transition-transform duration-300" />
                        ) : (
                          <ChevronDown className="w-5 h-5 text-orange-600 transition-transform duration-300" />
                        )}
                      </div>
                    </div>
                    
                    {isInvestmentBreakdownExpanded && (
                      <div className="mt-4 space-y-2 border-t border-orange-200 pt-4 transition-all duration-300 ease-in-out">
                        {investmentBreakdown.laborAutomationCost > 0 && (
                          <div className="flex justify-between text-sm">
                            <span className="text-orange-700">Labor Automation Cost:</span>
                            <span className="font-semibold text-orange-800">${investmentBreakdown.laborAutomationCost.toLocaleString()}/month</span>
                          </div>
                        )}
                        {investmentBreakdown.productionEfficiencyCost > 0 && (
                          <div className="flex justify-between text-sm">
                            <span className="text-orange-700">Production Efficiency Cost:</span>
                            <span className="font-semibold text-orange-800">${investmentBreakdown.productionEfficiencyCost.toLocaleString()}/month</span>
                          </div>
                        )}
                        {investmentBreakdown.inventorySystemCost > 0 && (
                          <div className="flex justify-between text-sm">
                            <span className="text-orange-700">Inventory System Cost:</span>
                            <span className="font-semibold text-orange-800">${investmentBreakdown.inventorySystemCost.toLocaleString()}/month</span>
                          </div>
                        )}
                        {investmentBreakdown.marketingSpendCost > 0 && (
                          <div className="flex justify-between text-sm">
                            <span className="text-orange-700">Additional Marketing Spend:</span>
                            <span className="font-semibold text-orange-800">${investmentBreakdown.marketingSpendCost.toLocaleString()}/month</span>
                          </div>
                        )}
                        <div className="flex justify-between text-sm font-bold border-t border-orange-200 pt-2">
                          <span className="text-orange-700">Total Monthly Investment:</span>
                          <span className="text-orange-800">${investmentBreakdown.totalMonthlyCost.toLocaleString()}</span>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
          
          {/* AI Insights */}
          <Card className="professional-card">
            <CardHeader>
              <CardTitle className="text-xl professional-heading flex items-center gap-2">
                <Sparkles className="w-5 h-5" />
                AI Insights
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-5 border border-purple-100">
                {/* Key Insight Headline */}
                <div className="mb-4">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-2xl">🎯</span>
                    <h3 className="text-lg font-bold text-gray-900">Key Insight</h3>
                  </div>
                  <p className="text-gray-800 font-medium leading-relaxed">
                    {laborAutomation > 40 
                      ? `Your biggest opportunity is in labor automation, with potential annual savings of $${Math.round(((laborAutomation - 10) / 100) * baselineData.monthlyLabor * 12).toLocaleString()}.`
                      : marketingValue > baselineData.marketingSpend * 1.5
                      ? `Marketing optimization shows the highest ROI potential with projected $${Math.round(summaryMetrics.annualDifference * 0.4).toLocaleString()} annual impact.`
                      : productionEfficiency > 120
                      ? `Production efficiency improvements could deliver $${Math.round(((productionEfficiency - 100) / 100) * baselineData.monthlyCOGS * 12 * 0.15).toLocaleString()}/year in cost savings.`
                      : `Focus on gradual automation to achieve $${Math.round(baselineData.monthlyLabor * 12 * 0.2).toLocaleString()}/year in labor cost reductions.`}
                  </p>
                </div>

                {/* Divider */}
                <div className="border-t border-purple-200 my-4"></div>

                {/* Analysis Highlights */}
                <div className="space-y-3">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-xl">📊</span>
                    <h4 className="text-base font-bold text-gray-900">Analysis Highlights</h4>
                  </div>
                  
                  <div className="space-y-2 ml-1">
                    {/* Labor Efficiency */}
                    <div className="flex items-start gap-2">
                      <span className="text-lg">💰</span>
                      <div className="flex-1">
                        <span className="text-sm font-semibold text-gray-900">Labor Efficiency:</span>
                        <span className="text-sm text-gray-700 ml-1">
                          {laborAutomation > 30 
                            ? `${Math.round(((laborAutomation - 10) / 70) * 100)}% improvement possible ($${Math.round(((laborAutomation - 10) / 100) * baselineData.monthlyLabor * 12).toLocaleString()}/year)`
                            : `${Math.round(((20) / 70) * 100)}% improvement with basic automation ($${Math.round((20 / 100) * baselineData.monthlyLabor * 12).toLocaleString()}/year)`}
                        </span>
                      </div>
                    </div>

                    {/* Production Quality */}
                    <div className="flex items-start gap-2">
                      <span className="text-lg">✅</span>
                      <div className="flex-1">
                        <span className="text-sm font-semibold text-gray-900">Quality Control:</span>
                        <span className="text-sm text-gray-700 ml-1">
                          {productionEfficiency > 120 
                            ? `${Math.round(((productionEfficiency - 100) / 50) * 45)}% defect reduction achievable ($${Math.round(((productionEfficiency - 100) / 100) * baselineData.monthlyCOGS * 12 * 0.1).toLocaleString()}/year)`
                            : `${Math.round((20 / 50) * 45)}% defect reduction with process optimization ($${Math.round((baselineData.monthlyCOGS * 12 * 0.05)).toLocaleString()}/year)`}
                        </span>
                      </div>
                    </div>

                    {/* Inventory Optimization */}
                    <div className="flex items-start gap-2">
                      <span className="text-lg">📈</span>
                      <div className="flex-1">
                        <span className="text-sm font-semibold text-gray-900">Inventory Optimization:</span>
                        <span className="text-sm text-gray-700 ml-1">
                          {inventoryTurnover > 8 
                            ? `${Math.round(((inventoryTurnover - 6) / 6) * 100)}% reduction in carrying costs ($${Math.round(((inventoryTurnover - 6) / 6) * baselineData.monthlyOverhead * 12 * 0.3).toLocaleString()}/year)`
                            : `${Math.round((2 / 6) * 100)}% reduction potential with better turnover ($${Math.round((2 / 6) * baselineData.monthlyOverhead * 12 * 0.3).toLocaleString()}/year)`}
                        </span>
                      </div>
                    </div>

                    {/* ROI Timeline */}
                    <div className="flex items-start gap-2">
                      <span className="text-lg">⏱️</span>
                      <div className="flex-1">
                        <span className="text-sm font-semibold text-gray-900">ROI Timeline:</span>
                        <span className="text-sm text-gray-700 ml-1">
                          {summaryMetrics.roi > 50 
                            ? `${Math.round(12 / (summaryMetrics.roi / 100))}-month payback period for current optimizations`
                            : summaryMetrics.roi > 0
                            ? `${Math.round(24 / (summaryMetrics.roi / 100))}-month payback period with gradual implementation`
                            : `Focus on quick wins with 6-8 month payback potential`}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Additional context based on questionnaire */}
                {hasQuestionnaireData && questionnaireData?.answers['q1'] && (
                  <>
                    <div className="border-t border-purple-200 my-4"></div>
                    <div className="bg-white/50 rounded-lg p-3 border border-purple-100">
                      <p className="text-sm text-purple-800 font-medium">
                        <span className="font-semibold">Industry Context:</span> {questionnaireData.answers['q1']} manufacturing typically benefits from {
                          questionnaireData.answers['q1'].includes('Metal') 
                            ? 'precision automation and quality control systems'
                            : questionnaireData.answers['q1'].includes('Electronics')
                            ? 'component tracking and automated testing systems'
                            : questionnaireData.answers['q1'].includes('Food')
                            ? 'hygiene automation and inventory freshness tracking'
                            : 'industry-specific automation solutions'
                        } as priority improvements.
                      </p>
                    </div>
                  </>
                )}
              </div>
              
              <div className="pt-4 border-t border-gray-200">
                <div className="text-sm text-gray-600 mb-3">Ready to implement these insights?</div>
                <Button className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white py-3 px-4 font-semibold rounded-lg transform hover:scale-105 transition-all duration-200 flex items-center justify-center gap-2">
                  <DollarSign className="w-4 h-4" />
                  Get Full Analysis →
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Sandbox;
