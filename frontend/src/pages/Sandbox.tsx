
import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Sparkles, DollarSign, Calculator, ChevronDown, ChevronUp, Info, ArrowUp, ArrowDown, AlertCircle, Settings } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, ComposedChart, Bar, Cell } from 'recharts';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';
import { 
  extractPLData, 
  generateForecastData, 
  calculateSummaryMetrics,
  calculateLaborAutomationImpact,
  calculateProductionEfficiencyImpact,
  calculateInventoryTurnoverImpact,
  type PLData,
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
  // New slider states with specified ranges and defaults
  const [productionVolume, setProductionVolume] = useState(80); // 50-120% of capacity, default 80%
  const [defectRateReduction, setDefectRateReduction] = useState(0); // 0-100%, default 0%
  const [automationLevel, setAutomationLevel] = useState(30); // 0-100%, default 30%
  const [overtimeHours, setOvertimeHours] = useState(20); // 0-50% of regular hours, default 20%
  const [inventoryTurnover, setInventoryTurnover] = useState(8); // 4-24 times/year, default 8
  
  // Legacy states for compatibility during transition
  const [priceValue, setPriceValue] = useState(baselineData.averagePrice);
  const [marketingValue, setMarketingValue] = useState(baselineData.marketingSpend);
  const [laborAutomation, setLaborAutomation] = useState(10);
  const [productionEfficiency, setProductionEfficiency] = useState(100);
  
  // Slider ranges
  const priceRange = {
    min: Math.round(baselineData.averagePrice * 0.7),
    max: Math.round(baselineData.averagePrice * 1.3)
  };
  const marketingRange = {
    min: 0,
    max: Math.max(baselineData.marketingSpend * 3, 50000)
  };
  
  // UI state
  const [isInvestmentBreakdownExpanded, setIsInvestmentBreakdownExpanded] = useState(false);
  const [savedScenarios, setSavedScenarios] = useState<Array<{id: string, name: string, values: any}>>([]);
  const [selectedScenario, setSelectedScenario] = useState<string>('');
  const [showScenarioComparison, setShowScenarioComparison] = useState(false);
  const [showConstraints, setShowConstraints] = useState(false);
  const [budgetLimit, setBudgetLimit] = useState<number>(0);
  const [timelineLimit, setTimelineLimit] = useState<number>(12);
  const [constraintProductPrice, setConstraintProductPrice] = useState<number>(baselineData.averagePrice);

  // Update slider values when baseline data changes
  useEffect(() => {
    setPriceValue(baselineData.averagePrice);
    setMarketingValue(baselineData.marketingSpend);
    setConstraintProductPrice(baselineData.averagePrice);
  }, [baselineData]);
  
  // Load saved scenarios from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('savedScenarios');
    if (saved) {
      setSavedScenarios(JSON.parse(saved));
    }
  }, []);
  
  // Create operational factors object using new sliders
  const operationalFactors: OperationalFactors = useMemo(() => ({
    laborAutomationLevel: automationLevel,
    productionEfficiency: 100 + (productionVolume - 80) * 0.5, // Map production volume to efficiency
    inventoryTurnoverRate: inventoryTurnover
  }), [automationLevel, productionVolume, inventoryTurnover]);
  
  // Generate forecast data with seasonal variation (using constraint price if set)
  const effectivePrice = constraintProductPrice || priceValue;
  const forecastData = useMemo(() => 
    generateForecastData(baselineData, effectivePrice, marketingValue, operationalFactors), 
    [baselineData, effectivePrice, marketingValue, operationalFactors]
  );
  
  // Calculate individual investment components for breakdown using new sliders and constraints
  const investmentBreakdown = useMemo(() => {
    try {
      const automationImpact = calculateLaborAutomationImpact(baselineData, automationLevel);
      const efficiencyImpact = calculateProductionEfficiencyImpact(baselineData, operationalFactors?.productionEfficiency || 100);
      const inventoryImpact = calculateInventoryTurnoverImpact(baselineData, inventoryTurnover);
      const marketingCost = marketingValue - (baselineData?.marketingSpend || 0);
      
      // Additional costs for new sliders
      const qualityImprovementCost = defectRateReduction * 50; // $50/month per % improvement
      const overtimeReductionCost = Math.max(0, (50 - overtimeHours) * 100); // $100/month per % reduction
      
      const totalCost = (automationImpact?.automationInvestment || 0) + 
                       (efficiencyImpact?.implementationCost || 0) + 
                       (inventoryImpact?.implementationCost || 0) + 
                       Math.max(marketingCost, 0) + 
                       qualityImprovementCost + 
                       overtimeReductionCost;
      
      // Apply budget constraint if set
      const budgetConstrainedCost = budgetLimit > 0 ? Math.min(totalCost, budgetLimit) : totalCost;
      const budgetConstraintActive = budgetLimit > 0 && totalCost > budgetLimit;
      
      return {
        laborAutomationCost: automationImpact?.automationInvestment || 0,
        productionEfficiencyCost: efficiencyImpact?.implementationCost || 0,
        inventorySystemCost: inventoryImpact?.implementationCost || 0,
        marketingSpendCost: Math.max(marketingCost, 0),
        qualityImprovementCost,
        overtimeReductionCost,
        totalMonthlyCost: budgetConstrainedCost,
        budgetConstraintActive,
        originalCost: totalCost
      };
    } catch (error) {
      console.error('Error calculating investment breakdown:', error);
      return {
        laborAutomationCost: 0,
        productionEfficiencyCost: 0,
        inventorySystemCost: 0,
        marketingSpendCost: 0,
        qualityImprovementCost: 0,
        overtimeReductionCost: 0,
        totalMonthlyCost: 0,
        budgetConstraintActive: false,
        originalCost: 0
      };
    }
  }, [baselineData, automationLevel, operationalFactors, inventoryTurnover, marketingValue, defectRateReduction, overtimeHours, budgetLimit]);
  
  // Calculate summary metrics using constraint-aware investment breakdown
  const summaryMetrics = useMemo(() => {
    try {
      const baseMetrics = calculateSummaryMetrics(baselineData, forecastData, marketingValue, operationalFactors);
      
      // Override total investment with budget-constrained value if budget limit is active
      if (budgetLimit > 0 && investmentBreakdown?.budgetConstraintActive) {
        const constrainedInvestment = (investmentBreakdown?.totalMonthlyCost || 0) * 12;
        const roi = constrainedInvestment > 0 ? ((baseMetrics?.annualDifference || 0) / constrainedInvestment) * 100 : 0;
        
        return {
          ...baseMetrics,
          totalInvestment: Math.round(constrainedInvestment),
          roi: Math.round(roi * 10) / 10
        };
      }
      
      return baseMetrics;
    } catch (error) {
      console.error('Error calculating summary metrics:', error);
      return {
        currentProfit: 0,
        newProfit: 0,
        monthlyDifference: 0,
        annualDifference: 0,
        roi: 0,
        totalInvestment: 0
      };
    }
  }, [baselineData, forecastData, marketingValue, operationalFactors, budgetLimit, investmentBreakdown]);
  
  // New slider handlers
  const handleProductionVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setProductionVolume(parseInt(e.target.value));
  };
  
  const handleDefectRateReductionChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setDefectRateReduction(parseInt(e.target.value));
  };
  
  const handleAutomationLevelChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setAutomationLevel(parseInt(e.target.value));
  };
  
  const handleOvertimeHoursChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setOvertimeHours(parseInt(e.target.value));
  };
  
  const handleInventoryTurnoverChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInventoryTurnover(parseInt(e.target.value));
  };
  
  // Legacy handlers for backward compatibility
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
  
  // Save current scenario
  const saveCurrentScenario = () => {
    const scenarioName = prompt('Enter a name for this scenario:');
    if (scenarioName) {
      const newScenario = {
        id: Date.now().toString(),
        name: scenarioName,
        values: {
          productionVolume,
          defectRateReduction,
          automationLevel,
          overtimeHours,
          inventoryTurnover
        }
      };
      const updated = [...savedScenarios, newScenario];
      setSavedScenarios(updated);
      localStorage.setItem('savedScenarios', JSON.stringify(updated));
    }
  };
  
  // Load selected scenario
  const loadScenario = (scenarioId: string) => {
    const scenario = savedScenarios.find(s => s.id === scenarioId);
    if (scenario) {
      setProductionVolume(scenario.values.productionVolume);
      setDefectRateReduction(scenario.values.defectRateReduction);
      setAutomationLevel(scenario.values.automationLevel);
      setOvertimeHours(scenario.values.overtimeHours);
      setInventoryTurnover(scenario.values.inventoryTurnover);
      setSelectedScenario(scenarioId);
    }
  };
  
  // Calculate waterfall chart data
  const waterfallData = useMemo(() => {
    const baselineCost = baselineData.monthlyCOGS + baselineData.monthlyLabor + baselineData.monthlyOverhead;
    const automationSavings = Math.max(0, ((automationLevel - 30) / 100) * baselineData.monthlyLabor * 0.3);
    const qualitySavings = Math.max(0, (defectRateReduction / 100) * baselineData.monthlyCOGS * 0.15);
    const overtimeSavings = Math.max(0, ((50 - overtimeHours) / 50) * baselineData.monthlyLabor * 0.15);
    
    let cumulative = baselineCost;
    const data = [
      { name: 'Baseline Costs', value: baselineCost, cumulative: baselineCost, type: 'baseline', start: 0 }
    ];
    
    if (automationSavings > 0) {
      cumulative -= automationSavings;
      data.push({ 
        name: 'Labor Savings', 
        value: -automationSavings, 
        cumulative: cumulative, 
        type: 'savings',
        start: cumulative
      });
    }
    
    if (qualitySavings > 0) {
      cumulative -= qualitySavings;
      data.push({ 
        name: 'Quality Savings', 
        value: -qualitySavings, 
        cumulative: cumulative, 
        type: 'savings',
        start: cumulative
      });
    }
    
    if (overtimeSavings > 0) {
      cumulative -= overtimeSavings;
      data.push({ 
        name: 'Overtime Savings', 
        value: -overtimeSavings, 
        cumulative: cumulative, 
        type: 'savings',
        start: cumulative
      });
    }
    
    data.push({ 
      name: 'Final Costs', 
      value: cumulative, 
      cumulative: cumulative, 
      type: 'final',
      start: 0
    });
    
    return data;
  }, [baselineData, automationLevel, defectRateReduction, overtimeHours]);

  // Use the reactive questionnaire state
  const { hasQuestionnaireData, isQuestionnaireCompleted, questionnaireData } = questionnaireState;

  return (
    <div className="container mx-auto px-6 py-16 space-y-8">
      <div className="mb-12 text-center">
        <h1 className="text-5xl font-bold professional-heading mb-6">Business Analysis Sandbox</h1>
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

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8">
        {/* Left Column - Sandbox Controls */}
        <div className="lg:col-span-3 order-2 lg:order-1">
          <Card className="professional-card h-fit">
            <CardHeader>
              <CardTitle className="text-2xl professional-heading">Sandbox Simulator</CardTitle>
              <p className="professional-text">
                Use these controls to see how changing key variables can impact a sample business in real-time.
              </p>
            </CardHeader>
            <CardContent className="space-y-6 pb-8">
              {/* Preset Scenarios */}
              <div className="space-y-4 pb-6 border-b border-gray-100">
                <h3 className="text-sm font-semibold text-gray-900">Preset Scenarios</h3>
                <div className="grid grid-cols-1 gap-3">
                  <Button 
                    variant="outline"
                    size="sm"
                    className="w-full justify-start text-sm font-medium py-3 px-4 h-auto"
                    onClick={() => {
                      setProductionVolume(65);
                      setDefectRateReduction(25);
                      setAutomationLevel(25);
                      setOvertimeHours(35);
                      setInventoryTurnover(9);
                    }}
                  >
                    <span className="mr-3">🛡️</span>
                    <span className="flex-1 text-left">Conservative Approach</span>
                  </Button>
                  <Button 
                    variant="outline"
                    size="sm"
                    className="w-full justify-start text-sm font-medium py-3 px-4 h-auto"
                    onClick={() => {
                      setProductionVolume(85);
                      setDefectRateReduction(50);
                      setAutomationLevel(50);
                      setOvertimeHours(25);
                      setInventoryTurnover(14);
                    }}
                  >
                    <span className="mr-3">⚖️</span>
                    <span className="flex-1 text-left">Balanced Strategy</span>
                  </Button>
                  <Button 
                    variant="outline"
                    size="sm"
                    className="w-full justify-start text-sm font-medium py-3 px-4 h-auto"
                    onClick={() => {
                      setProductionVolume(103);
                      setDefectRateReduction(75);
                      setAutomationLevel(75);
                      setOvertimeHours(12);
                      setInventoryTurnover(19);
                    }}
                  >
                    <span className="mr-3">🚀</span>
                    <span className="flex-1 text-left">Aggressive Growth</span>
                  </Button>
                </div>
              </div>
              
              {/* Scenario Comparison */}
              <div className="space-y-4 pb-6 border-b border-gray-100">
                <h3 className="text-sm font-semibold text-gray-900">Scenario Management</h3>
                <div className="space-y-3">
                  <Button 
                    variant="outline"
                    size="default"
                    className="w-full text-sm font-medium py-2"
                    onClick={saveCurrentScenario}
                  >
                    💾 Save Current Configuration
                  </Button>
                  {savedScenarios.length > 0 && (
                    <select 
                      value={selectedScenario}
                      onChange={(e) => e.target.value && loadScenario(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm bg-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    >
                      <option value="">📋 Load Saved Scenario</option>
                      {savedScenarios.map(scenario => (
                        <option key={scenario.id} value={scenario.id}>
                          {scenario.name}
                        </option>
                      ))}
                    </select>
                  )}
                </div>
              </div>
              
              {/* Constraints Panel */}
              <div className="space-y-3">
                <div 
                  className="flex items-center gap-2 cursor-pointer"
                  onClick={() => setShowConstraints(!showConstraints)}
                >
                  <Settings className="w-4 h-4 text-gray-600" />
                  <h3 className="text-sm font-semibold text-gray-900">Constraints</h3>
                  {showConstraints ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </div>
                
                {showConstraints && (
                  <div className="space-y-4 pl-6 border-l-2 border-gray-200">
                    {(budgetLimit > 0 || timelineLimit !== 12 || (constraintProductPrice && baselineData?.averagePrice && constraintProductPrice !== baselineData.averagePrice)) && (
                      <div className="bg-blue-50 border border-blue-200 rounded-lg px-3 py-2 mb-4">
                        <div className="flex items-center gap-2 text-xs text-blue-800 font-medium mb-1">
                          <Info className="w-4 h-4" />
                          Active Constraints:
                        </div>
                        <div className="text-xs text-blue-700 space-y-1">
                          {budgetLimit > 0 && <div>• Budget limit: ${budgetLimit.toLocaleString()}/month</div>}
                          {timelineLimit !== 12 && <div>• Timeline limit: {timelineLimit} months</div>}
                          {constraintProductPrice && baselineData?.averagePrice && constraintProductPrice !== baselineData.averagePrice && <div>• Product price: ${constraintProductPrice}</div>}
                        </div>
                      </div>
                    )}
                    <div className="space-y-2">
                      <label className="text-xs font-medium text-gray-700">Product Price ($)</label>
                      <input
                        type="number"
                        value={constraintProductPrice || ''}
                        onChange={(e) => setConstraintProductPrice(parseInt(e.target.value) || (baselineData?.averagePrice || 50))}
                        placeholder={`Default: $${baselineData?.averagePrice || 50}`}
                        className="w-full px-3 py-2 border rounded-md text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-medium text-gray-700">Budget Limit ($)</label>
                      <input
                        type="number"
                        value={budgetLimit || ''}
                        onChange={(e) => setBudgetLimit(parseInt(e.target.value) || 0)}
                        placeholder="No limit"
                        className="w-full px-3 py-2 border rounded-md text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-medium text-gray-700">Timeline Limit</label>
                      <select
                        value={timelineLimit}
                        onChange={(e) => setTimelineLimit(parseInt(e.target.value))}
                        className="w-full px-3 py-2 border rounded-md text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white"
                      >
                        <option value={3}>3 months</option>
                        <option value={6}>6 months</option>
                        <option value={12}>12 months</option>
                        <option value={18}>18 months</option>
                        <option value={24}>24 months</option>
                      </select>
                    </div>
                  </div>
                )}
              </div>
              
              {/* Production Volume Control */}
              <div className="space-y-4 py-6 border-b border-gray-100 last:border-b-0">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <label htmlFor="production-volume-slider" className="text-sm font-semibold text-gray-900 block">
                      Production Capacity
                    </label>
                    <span className="text-xs text-gray-500">Utilization level</span>
                  </div>
                  <div className="text-sm professional-text ml-4">
                    <span className="text-black font-bold text-lg transition-all duration-300 ease-out">{productionVolume}%</span>
                  </div>
                </div>
                <div className="relative">
                  <input
                    type="range"
                    id="production-volume-slider"
                    min="50"
                    max="120"
                    value={productionVolume}
                    onChange={handleProductionVolumeChange}
                    className="w-full h-4 md:h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer hover:bg-gray-300 transition-colors duration-200 slider-thumb touch-manipulation"
                  />
                  {/* Baseline marker */}
                  <div 
                    className="absolute top-0 w-0.5 h-3 bg-gray-600 rounded-full pointer-events-none"
                    style={{ 
                      left: `${((80 - 50) / (120 - 50)) * 100}%`,
                      transform: 'translateX(-50%)'
                    }}
                  />
                </div>
                <div className="flex justify-between items-center text-xs text-gray-500 mt-2">
                  <span>50%</span>
                  <div className="flex gap-2">
                    <button 
                      onClick={() => setProductionVolume(75)}
                      className="px-2 py-1 bg-green-100 hover:bg-green-200 text-green-700 rounded text-xs font-medium transition-colors"
                    >
                      75% (Min Optimal)
                    </button>
                    <button 
                      onClick={() => setProductionVolume(82)}
                      className="px-2 py-1 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded text-xs font-medium transition-colors"
                    >
                      82% (Recommended)
                    </button>
                    <button 
                      onClick={() => setProductionVolume(90)}
                      className="px-2 py-1 bg-green-100 hover:bg-green-200 text-green-700 rounded text-xs font-medium transition-colors"
                    >
                      90% (Max Optimal)
                    </button>
                  </div>
                  <span>120%</span>
                </div>
              </div>
              
              {/* Defect Rate Reduction Control */}
              <div className="space-y-4 py-6 border-b border-gray-100 last:border-b-0">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <label htmlFor="defect-rate-slider" className="text-sm font-semibold text-gray-900 block">
                      Quality Improvement
                    </label>
                    <span className="text-xs text-gray-500">Defect reduction level</span>
                  </div>
                  <div className="text-sm professional-text ml-4">
                    <span className="text-black font-bold text-lg transition-all duration-300 ease-out">{defectRateReduction}%</span>
                  </div>
                </div>
                <div className="relative">
                  <input
                    type="range"
                    id="defect-rate-slider"
                    min="0"
                    max="100"
                    value={defectRateReduction}
                    onChange={handleDefectRateReductionChange}
                    className="w-full h-4 md:h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer hover:bg-gray-300 transition-colors duration-200 slider-thumb touch-manipulation"
                  />
                  {/* Baseline marker */}
                  <div 
                    className="absolute top-0 w-0.5 h-3 bg-gray-600 rounded-full pointer-events-none"
                    style={{ 
                      left: `${((0 - 0) / (100 - 0)) * 100}%`,
                      transform: 'translateX(-50%)'
                    }}
                  />
                </div>
                <div className="flex justify-between items-center text-xs text-gray-500 mt-2">
                  <span>0%</span>
                  <div className="flex gap-2">
                    <button 
                      onClick={() => setDefectRateReduction(60)}
                      className="px-2 py-1 bg-green-100 hover:bg-green-200 text-green-700 rounded text-xs font-medium transition-colors"
                    >
                      60% (Min Optimal)
                    </button>
                    <button 
                      onClick={() => setDefectRateReduction(72)}
                      className="px-2 py-1 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded text-xs font-medium transition-colors"
                    >
                      72% (Recommended)
                    </button>
                    <button 
                      onClick={() => setDefectRateReduction(85)}
                      className="px-2 py-1 bg-green-100 hover:bg-green-200 text-green-700 rounded text-xs font-medium transition-colors"
                    >
                      85% (Max Optimal)
                    </button>
                  </div>
                  <span>100%</span>
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Defect rate: {Math.round(5 * (1 - defectRateReduction / 100))}%
                </div>
              </div>
              
              {/* Automation Level Control */}
              <div className="space-y-4 py-6 border-b border-gray-100 last:border-b-0">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <label htmlFor="automation-level-slider" className="text-sm font-semibold text-gray-900 block">
                      Automation Level
                    </label>
                    <span className="text-xs text-gray-500">Overall implementation</span>
                  </div>
                  <div className="text-sm professional-text ml-4">
                    <span className="text-black font-bold text-lg transition-all duration-300 ease-out">{automationLevel}%</span>
                  </div>
                </div>
                <div className="relative">
                  <input
                    type="range"
                    id="automation-level-slider"
                    min="0"
                    max="100"
                    value={automationLevel}
                    onChange={handleAutomationLevelChange}
                    className="w-full h-4 md:h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer hover:bg-gray-300 transition-colors duration-200 slider-thumb touch-manipulation"
                  />
                  {/* Baseline marker */}
                  <div 
                    className="absolute top-0 w-0.5 h-3 bg-gray-600 rounded-full pointer-events-none"
                    style={{ 
                      left: `${((30 - 0) / (100 - 0)) * 100}%`,
                      transform: 'translateX(-50%)'
                    }}
                  />
                </div>
                <div className="flex justify-between items-center text-xs text-gray-500 mt-2">
                  <span>0%</span>
                  <div className="flex gap-2">
                    <button 
                      onClick={() => setAutomationLevel(40)}
                      className="px-2 py-1 bg-green-100 hover:bg-green-200 text-green-700 rounded text-xs font-medium transition-colors"
                    >
                      40% (Min Optimal)
                    </button>
                    <button 
                      onClick={() => setAutomationLevel(55)}
                      className="px-2 py-1 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded text-xs font-medium transition-colors"
                    >
                      55% (Recommended)
                    </button>
                    <button 
                      onClick={() => setAutomationLevel(70)}
                      className="px-2 py-1 bg-green-100 hover:bg-green-200 text-green-700 rounded text-xs font-medium transition-colors"
                    >
                      70% (Max Optimal)
                    </button>
                  </div>
                  <span>100%</span>
                </div>
              </div>
              
              {/* Overtime Reduction Control */}
              <div className="space-y-4 py-6 border-b border-gray-100 last:border-b-0">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <label htmlFor="overtime-slider" className="text-sm font-semibold text-gray-900 block">
                      Overtime Reduction
                    </label>
                    <span className="text-xs text-gray-500">Labor cost savings</span>
                  </div>
                  <div className="text-sm professional-text ml-4">
                    <span className="text-black font-bold text-lg transition-all duration-300 ease-out">{50 - overtimeHours}%</span>
                  </div>
                </div>
                <div className="relative">
                  <input
                    type="range"
                    id="overtime-slider"
                    min="0"
                    max="50"
                    value={overtimeHours}
                    onChange={handleOvertimeHoursChange}
                    className="w-full h-4 md:h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer hover:bg-gray-300 transition-colors duration-200 slider-thumb touch-manipulation"
                  />
                  {/* Baseline marker */}
                  <div 
                    className="absolute top-0 w-0.5 h-3 bg-gray-600 rounded-full pointer-events-none"
                    style={{ 
                      left: `${((20 - 0) / (50 - 0)) * 100}%`,
                      transform: 'translateX(-50%)'
                    }}
                  />
                </div>
                <div className="flex justify-between items-center text-xs text-gray-500 mt-2">
                  <span>0% OT</span>
                  <div className="flex gap-2">
                    <button 
                      onClick={() => setOvertimeHours(15)}
                      className="px-2 py-1 bg-green-100 hover:bg-green-200 text-green-700 rounded text-xs font-medium transition-colors"
                    >
                      15% (Max Optimal)
                    </button>
                    <button 
                      onClick={() => setOvertimeHours(10)}
                      className="px-2 py-1 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded text-xs font-medium transition-colors"
                    >
                      10% (Recommended)
                    </button>
                    <button 
                      onClick={() => setOvertimeHours(5)}
                      className="px-2 py-1 bg-green-100 hover:bg-green-200 text-green-700 rounded text-xs font-medium transition-colors"
                    >
                      5% (Min Optimal)
                    </button>
                  </div>
                  <span>50% OT</span>
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Current overtime: {overtimeHours}% of regular hours
                </div>
              </div>
              
              {/* Inventory Optimization Control */}
              <div className="space-y-4 py-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <label htmlFor="inventory-optimization-slider" className="text-sm font-semibold text-gray-900 block">
                      Inventory Optimization
                    </label>
                    <span className="text-xs text-gray-500">Turnover rate per year</span>
                  </div>
                  <div className="text-sm professional-text ml-4">
                    <span className="text-black font-bold text-lg transition-all duration-300 ease-out">{inventoryTurnover}x</span>
                  </div>
                </div>
                <div className="relative">
                  <input
                    type="range"
                    id="inventory-optimization-slider"
                    min="4"
                    max="24"
                    value={inventoryTurnover}
                    onChange={handleInventoryTurnoverChange}
                    className="w-full h-4 md:h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer hover:bg-gray-300 transition-colors duration-200 slider-thumb touch-manipulation"
                  />
                  {/* Baseline marker */}
                  <div 
                    className="absolute top-0 w-0.5 h-3 bg-gray-600 rounded-full pointer-events-none"
                    style={{ 
                      left: `${((8 - 4) / (24 - 4)) * 100}%`,
                      transform: 'translateX(-50%)'
                    }}
                  />
                </div>
                <div className="flex justify-between items-center text-xs text-gray-500 mt-2">
                  <span>4x</span>
                  <div className="flex gap-2">
                    <button 
                      onClick={() => setInventoryTurnover(8)}
                      className="px-2 py-1 bg-green-100 hover:bg-green-200 text-green-700 rounded text-xs font-medium transition-colors"
                    >
                      8x (Min Optimal)
                    </button>
                    <button 
                      onClick={() => setInventoryTurnover(10)}
                      className="px-2 py-1 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded text-xs font-medium transition-colors"
                    >
                      10x (Recommended)
                    </button>
                    <button 
                      onClick={() => setInventoryTurnover(12)}
                      className="px-2 py-1 bg-green-100 hover:bg-green-200 text-green-700 rounded text-xs font-medium transition-colors"
                    >
                      12x (Max Optimal)
                    </button>
                  </div>
                  <span>24x</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* Center Column - Profit Forecast (Widest) */}
        <div className="lg:col-span-6 order-1 lg:order-2">
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
                        formatter={(value, name) => {
                          if (name === 'adjustedLowerBound' || name === 'adjustedUpperBound') return null;
                          return [
                            `$${Number(value).toLocaleString()}`,
                            name === 'originalProfit' ? 'Original Forecast' : 'Adjusted Forecast'
                          ];
                        }}
                      />}
                    />
                    
                    {/* Confidence bands as light lines */}
                    <Line 
                      type="monotone" 
                      dataKey="adjustedLowerBound" 
                      stroke="hsl(220, 70%, 50%)"
                      strokeWidth={1}
                      strokeOpacity={0.3}
                      strokeDasharray="2 2"
                      dot={false}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="adjustedUpperBound" 
                      stroke="hsl(220, 70%, 50%)"
                      strokeWidth={1}
                      strokeOpacity={0.3}
                      strokeDasharray="2 2"
                      dot={false}
                    />
                    
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
                      <div className="w-4 h-0.5 bg-blue-300 border-dashed border-t-2"></div>
                      <span className="text-gray-600">Confidence Band (±15%)</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </Card>
          
          {/* Cost Breakdown Waterfall Chart */}
          <Card className="professional-card mt-8">
            <CardHeader>
              <CardTitle className="text-2xl professional-heading">Cost Breakdown Waterfall</CardTitle>
              <p className="text-sm text-gray-600">See how each optimization reduces your monthly costs</p>
            </CardHeader>
            <CardContent>
              <div className="w-full h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart 
                    data={waterfallData} 
                    margin={{ top: 20, right: 30, left: 40, bottom: 80 }}
                    barCategoryGap="20%"
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="name" 
                      angle={-45}
                      textAnchor="end"
                      height={80}
                      interval={0}
                      fontSize={12}
                    />
                    <YAxis 
                      tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
                      fontSize={12}
                    />
                    <Tooltip 
                      formatter={(value) => [`$${Number(value).toLocaleString()}`, 'Amount']}
                      labelStyle={{ color: '#374151' }}
                      contentStyle={{ 
                        backgroundColor: 'white', 
                        border: '1px solid #e5e7eb',
                        borderRadius: '8px'
                      }}
                    />
                    <Bar 
                      dataKey="cumulative" 
                      fill="transparent"
                    >
                      {waterfallData.map((entry, index) => (
                        <Cell 
                          key={`cell-${index}`} 
                          fill={
                            entry.type === 'baseline' ? '#6366f1' :
                            entry.type === 'savings' ? '#10b981' :
                            entry.type === 'final' ? '#3b82f6' : '#94a3b8'
                          }
                        />
                      ))}
                    </Bar>
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
              
              {/* Legend */}
              <div className="mt-4 flex flex-wrap justify-center gap-6 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-indigo-500 rounded"></div>
                  <span>Baseline Costs</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-green-500 rounded"></div>
                  <span>Cost Savings</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-blue-500 rounded"></div>
                  <span>Final Costs</span>
                </div>
              </div>
            </CardContent>
          </Card>
          
          {/* Implementation Timeline */}
          <Card className="professional-card mt-8">
            <CardHeader>
              <CardTitle className="text-2xl professional-heading">Implementation Timeline</CardTitle>
              <p className="text-sm text-gray-600">Key milestones for your optimization journey</p>
            </CardHeader>
            <CardContent className="px-8 py-6">
              <div className="relative">
                {/* Timeline line */}
                <div className="absolute left-8 top-8 bottom-8 w-1 bg-gradient-to-b from-red-300 via-yellow-300 to-green-300 rounded-full"></div>
                
                <div className="space-y-12">
                  {/* Phase 1: Investment */}
                  <div className="flex items-start gap-8">
                    <div className="w-16 h-16 rounded-full bg-red-100 border-4 border-red-200 flex items-center justify-center relative z-10 shadow-lg">
                      <span className="text-red-600 font-bold text-sm">1-3</span>
                    </div>
                    <div className="flex-1 pt-2">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">Investment Phase</h3>
                      <p className="text-sm text-gray-600 mb-3">Months 1-{timelineLimit >= 6 ? '3' : timelineLimit >= 3 ? '2' : '1'}: Initial setup, equipment procurement, and staff training</p>
                      <div className="bg-red-50 border border-red-200 px-4 py-2 rounded-lg text-sm text-red-700 font-medium">
                        💸 Monthly Cost: $${Math.round(investmentBreakdown.totalMonthlyCost * 1.5).toLocaleString()}
                        {investmentBreakdown.budgetConstraintActive && (
                          <div className="text-orange-600 text-xs mt-1">⚠️ Budget constrained from $${investmentBreakdown.originalCost.toLocaleString()}</div>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {/* Phase 2: Break-even */}
                  <div className="flex items-start gap-8">
                    <div className="w-16 h-16 rounded-full bg-yellow-100 border-4 border-yellow-200 flex items-center justify-center relative z-10 shadow-lg">
                      <span className="text-yellow-600 font-bold text-sm">4-6</span>
                    </div>
                    <div className="flex-1 pt-2">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">Break-even Phase</h3>
                      <p className="text-sm text-gray-600 mb-3">Months {timelineLimit >= 6 ? '4-6' : timelineLimit >= 3 ? '3-' + Math.min(timelineLimit, 6) : timelineLimit + '-' + timelineLimit}: Systems stabilizing, processes optimizing, early returns</p>
                      <div className="bg-yellow-50 border border-yellow-200 px-4 py-2 rounded-lg text-sm text-yellow-700 font-medium">
                        ⚖️ Break-even: ±$0 net impact
                        {timelineLimit < 6 && (
                          <div className="text-orange-600 text-xs mt-1">⚠️ Accelerated timeline may increase risk</div>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {/* Phase 3: Profit */}
                  <div className="flex items-start gap-8">
                    <div className="w-16 h-16 rounded-full bg-green-100 border-4 border-green-200 flex items-center justify-center relative z-10 shadow-lg">
                      <span className="text-green-600 font-bold text-sm">{Math.max(7, Math.ceil(timelineLimit * 0.6))}-{timelineLimit}</span>
                    </div>
                    <div className="flex-1 pt-2">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">Profit Phase</h3>
                      <p className="text-sm text-gray-600 mb-3">Months {Math.max(7, Math.ceil(timelineLimit * 0.6))}-{timelineLimit}: Full optimization benefits, sustained improvements</p>
                      <div className="bg-green-50 border border-green-200 px-4 py-2 rounded-lg text-sm text-green-700 font-medium">
                        💰 Monthly Profit: +$${Math.round(summaryMetrics.monthlyDifference).toLocaleString()}
                        {timelineLimit < 12 && (
                          <div className="text-blue-600 text-xs mt-1">📈 Results may be {Math.round(((12 - timelineLimit) / 12) * 100)}% lower due to shorter timeline</div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* Right Column - Simulation Summary */}
        <div className="lg:col-span-3 space-y-8 order-3">
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
                    <div className={`inline-flex flex-col items-center px-4 py-3 rounded-full transition-all duration-300 ease-out ${
                      summaryMetrics.roi >= 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      <div className="text-2xl lg:text-3xl font-bold">
                        {summaryMetrics.roi >= 0 ? '+' : ''}{summaryMetrics.roi}%
                      </div>
                      <div className="text-xs lg:text-sm opacity-75">
                        ({(summaryMetrics.roi / 100 + 1).toFixed(2)}x return)
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Projected Monthly Profit - Largest Metric */}
                <div className="bg-blue-50 rounded-lg p-4">
                  <div className="text-sm text-blue-600 mb-2">Projected Monthly Profit</div>
                  <div className="space-y-2">
                    <div className="text-2xl lg:text-3xl font-bold text-blue-700 transition-all duration-300 ease-out break-words">
                      ${summaryMetrics.newProfit > 99999 
                        ? `${(summaryMetrics.newProfit / 1000).toFixed(1)}K` 
                        : summaryMetrics.newProfit.toLocaleString()}
                    </div>
                    <div className={`flex items-center text-sm lg:text-base font-semibold transition-all duration-300 ease-out ${
                      summaryMetrics.monthlyDifference >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {summaryMetrics.monthlyDifference >= 0 ? <ArrowUp className="w-4 h-4 mr-1 transition-transform duration-300" /> : <ArrowDown className="w-4 h-4 mr-1 transition-transform duration-300" />}
                      {summaryMetrics.monthlyDifference >= 0 ? '+' : ''}
                      ${Math.abs(summaryMetrics.monthlyDifference) > 99999 
                        ? `${(Math.abs(summaryMetrics.monthlyDifference) / 1000).toFixed(1)}K` 
                        : Math.abs(summaryMetrics.monthlyDifference).toLocaleString()}
                    </div>
                  </div>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-600 mb-1">Current Monthly Profit</div>
                  <div className="text-xl lg:text-2xl font-bold text-gray-900 break-words">
                    ${summaryMetrics.currentProfit > 99999 
                      ? `${(summaryMetrics.currentProfit / 1000).toFixed(1)}K` 
                      : summaryMetrics.currentProfit.toLocaleString()}
                  </div>
                </div>
                
                <div className="bg-purple-50 rounded-lg p-4">
                  <div className="text-sm text-purple-600 mb-1">12-Month Impact</div>
                  <div className="text-lg lg:text-xl font-bold text-purple-700 break-words">
                    {summaryMetrics.annualDifference >= 0 ? '+' : ''}
                    ${Math.abs(summaryMetrics.annualDifference) > 99999 
                      ? `${(Math.abs(summaryMetrics.annualDifference) / 1000).toFixed(1)}K` 
                      : Math.abs(summaryMetrics.annualDifference).toLocaleString()}
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
                    {automationLevel > 60 
                      ? `Your biggest opportunity is in automation, with potential annual savings of $${Math.round(((automationLevel - 30) / 100) * baselineData.monthlyLabor * 12).toLocaleString()}.`
                      : defectRateReduction > 50
                      ? `Quality improvements show high ROI potential with projected $${Math.round(defectRateReduction * 0.01 * baselineData.monthlyCOGS * 12).toLocaleString()} annual impact.`
                      : productionVolume > 100
                      ? `Production capacity optimization could deliver $${Math.round(((productionVolume - 80) / 100) * baselineData.monthlyRevenue * 12 * 0.1).toLocaleString()}/year in additional revenue.`
                      : `Focus on gradual automation to achieve $${Math.round(baselineData.monthlyLabor * 12 * 0.2).toLocaleString()}/year in labor cost reductions.`}
                  </p>
                </div>

                {/* Divider */}
                <div className="border-t border-purple-200 my-4"></div>

                {/* Analysis Highlights */}
                <div className="space-y-6">
                  <div className="flex items-center gap-2 mb-4">
                    <span className="text-xl">📊</span>
                    <h4 className="text-base font-bold text-gray-900">Analysis Highlights</h4>
                  </div>
                  
                  <div className="grid gap-4">
                    {/* Automation Efficiency */}
                    <div className="bg-white rounded-lg p-4 border border-gray-100 shadow-sm">
                      <div className="flex items-start gap-3">
                        <span className="text-xl mt-1">💰</span>
                        <div className="flex-1">
                          <h5 className="text-sm font-semibold text-gray-900 mb-2">Automation Efficiency</h5>
                          <p className="text-sm text-gray-700 leading-relaxed">
                            {automationLevel > 50 
                              ? `${Math.round(((automationLevel - 30) / 70) * 100)}% improvement possible with potential annual savings of $${Math.round(((automationLevel - 30) / 100) * baselineData.monthlyLabor * 12).toLocaleString()}`
                              : `${Math.round(((20) / 70) * 100)}% improvement possible with basic automation, saving approximately $${Math.round((20 / 100) * baselineData.monthlyLabor * 12).toLocaleString()} annually`}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Quality Control */}
                    <div className="bg-white rounded-lg p-4 border border-gray-100 shadow-sm">
                      <div className="flex items-start gap-3">
                        <span className="text-xl mt-1">✅</span>
                        <div className="flex-1">
                          <h5 className="text-sm font-semibold text-gray-900 mb-2">Quality Control</h5>
                          <p className="text-sm text-gray-700 leading-relaxed">
                            {defectRateReduction > 50 
                              ? `${defectRateReduction}% defect reduction achievable, generating annual savings of $${Math.round(defectRateReduction * 0.01 * baselineData.monthlyCOGS * 12).toLocaleString()}`
                              : `30% defect reduction possible through process optimization, saving $${Math.round(baselineData.monthlyCOGS * 12 * 0.05).toLocaleString()} per year`}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Production Capacity */}
                    <div className="bg-white rounded-lg p-4 border border-gray-100 shadow-sm">
                      <div className="flex items-start gap-3">
                        <span className="text-xl mt-1">📊</span>
                        <div className="flex-1">
                          <h5 className="text-sm font-semibold text-gray-900 mb-2">Production Capacity</h5>
                          <p className="text-sm text-gray-700 leading-relaxed">
                            {productionVolume > 90 
                              ? `${Math.round(((productionVolume - 80) / 40) * 100)}% capacity optimization delivering $${Math.round(((productionVolume - 80) / 100) * baselineData.monthlyRevenue * 12 * 0.1).toLocaleString()} in additional annual revenue`
                              : `${Math.round((10 / 40) * 100)}% capacity increase potential worth $${Math.round((10 / 100) * baselineData.monthlyRevenue * 12 * 0.1).toLocaleString()} annually`}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Inventory Optimization */}
                    <div className="bg-white rounded-lg p-4 border border-gray-100 shadow-sm">
                      <div className="flex items-start gap-3">
                        <span className="text-xl mt-1">📈</span>
                        <div className="flex-1">
                          <h5 className="text-sm font-semibold text-gray-900 mb-2">Inventory Optimization</h5>
                          <p className="text-sm text-gray-700 leading-relaxed">
                            {inventoryTurnover > 12 
                              ? `${Math.round(((inventoryTurnover - 8) / 16) * 100)}% reduction in carrying costs, saving $${Math.round(((inventoryTurnover - 8) / 16) * baselineData.monthlyOverhead * 12 * 0.3).toLocaleString()} annually`
                              : `${Math.round((4 / 16) * 100)}% reduction potential through better turnover management, worth $${Math.round((4 / 16) * baselineData.monthlyOverhead * 12 * 0.3).toLocaleString()} per year`}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* ROI Timeline */}
                    <div className="bg-white rounded-lg p-4 border border-gray-100 shadow-sm">
                      <div className="flex items-start gap-3">
                        <span className="text-xl mt-1">⏱️</span>
                        <div className="flex-1">
                          <h5 className="text-sm font-semibold text-gray-900 mb-2">ROI Timeline</h5>
                          <p className="text-sm text-gray-700 leading-relaxed">
                            {summaryMetrics.roi > 50 
                              ? `${Math.round(12 / (summaryMetrics.roi / 100))}-month payback period for current optimizations`
                              : summaryMetrics.roi > 0
                              ? `${Math.round(24 / (summaryMetrics.roi / 100))}-month payback period with gradual implementation`
                              : `Focus on quick wins with 6-8 month payback potential`}
                          </p>
                        </div>
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
              
              {/* Risk/Reward Gauge */}
              <div className="mt-8 p-6 bg-gradient-to-br from-gray-50 to-blue-50 rounded-lg border border-gray-200">
                <div className="flex items-center gap-2 mb-6">
                  <span className="text-xl">⚖️</span>
                  <h4 className="text-base font-bold text-gray-900">Risk/Reward Assessment</h4>
                </div>
                
                <div className="space-y-4">
                  {/* Axis Labels */}
                  <div className="text-center">
                    <div className="text-sm font-medium text-gray-700 mb-4">Implementation Difficulty vs Potential Savings</div>
                  </div>
                  
                  {/* Matrix Grid */}
                  <div className="relative">
                    <div className="grid grid-cols-2 grid-rows-2 gap-2 h-48">
                      {/* Top Left - Low Impact, Low Risk */}
                      <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-4 flex flex-col justify-center">
                        <div className="text-center">
                          <div className="text-xs font-semibold text-yellow-800 mb-1">Low Risk</div>
                          <div className="text-xs text-yellow-700">Low Impact</div>
                        </div>
                      </div>
                      
                      {/* Top Right - High Impact, Low Risk */}
                      <div className="bg-green-50 border-2 border-green-200 rounded-lg p-4 flex flex-col justify-center">
                        <div className="text-center">
                          <div className="text-xs font-semibold text-green-800 mb-1">Low Risk</div>
                          <div className="text-xs text-green-700">High Impact</div>
                        </div>
                      </div>
                      
                      {/* Bottom Left - Low Impact, High Risk */}
                      <div className="bg-orange-50 border-2 border-orange-200 rounded-lg p-4 flex flex-col justify-center">
                        <div className="text-center">
                          <div className="text-xs font-semibold text-orange-800 mb-1">High Risk</div>
                          <div className="text-xs text-orange-700">Low Impact</div>
                        </div>
                      </div>
                      
                      {/* Bottom Right - High Impact, High Risk */}
                      <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4 flex flex-col justify-center">
                        <div className="text-center">
                          <div className="text-xs font-semibold text-red-800 mb-1">High Risk</div>
                          <div className="text-xs text-red-700">High Impact</div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Current configuration indicator */}
                    <div 
                      className="absolute w-6 h-6 bg-blue-600 rounded-full border-3 border-white shadow-lg transform -translate-x-1/2 -translate-y-1/2 z-10 flex items-center justify-center"
                      style={{
                        left: `${Math.min(85, Math.max(15, 25 + (summaryMetrics.roi / 200) * 50))}%`,
                        top: `${Math.min(85, Math.max(15, 75 - (automationLevel / 100) * 50))}%`
                      }}
                      title="Your Current Configuration"
                    >
                      <div className="w-2 h-2 bg-white rounded-full"></div>
                    </div>
                  </div>
                  
                  {/* Legend */}
                  <div className="flex items-center justify-center gap-2 text-sm">
                    <div className="w-4 h-4 bg-blue-600 rounded-full"></div>
                    <span className="text-gray-700">Your Current Configuration</span>
                  </div>
                </div>
              </div>
              
              <div className="pt-4 border-t border-gray-200">
                <div className="text-sm text-gray-600 mb-3">Ready to implement these insights?</div>
                <Button 
                  className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white py-3 px-4 font-semibold rounded-lg transform hover:scale-105 transition-all duration-200 flex items-center justify-center gap-2"
                  onClick={() => {
                    // Navigate to analysis page with current simulation parameters
                    window.location.href = `/simulation?from=sandbox&productionVolume=${productionVolume}&defectRate=${defectRateReduction}&automation=${automationLevel}&overtime=${overtimeHours}&inventory=${inventoryTurnover}`;
                  }}
                >
                  <DollarSign className="w-4 h-4" />
                  See Full Analysis →
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
      
      {/* Bottom right navigation button */}
      <div className="fixed bottom-4 right-4 lg:bottom-8 lg:right-8 z-50">
        <Button 
          size="lg"
          className="shadow-lg bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-semibold rounded-full px-4 py-2 lg:px-6 lg:py-3 transform hover:scale-105 transition-all duration-200 flex items-center gap-2 text-sm lg:text-base"
          onClick={() => {
            // Navigate to analysis page with current simulation parameters
            window.location.href = `/simulation?from=sandbox&productionVolume=${productionVolume}&defectRate=${defectRateReduction}&automation=${automationLevel}&overtime=${overtimeHours}&inventory=${inventoryTurnover}`;
          }}
        >
          <span className="hidden sm:inline">See Full Analysis →</span>
          <span className="sm:hidden">Analysis →</span>
        </Button>
      </div>
    </div>
  );
};

export default Sandbox;
