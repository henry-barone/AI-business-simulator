// Utility functions for business simulation calculations

export interface PLData {
  monthlyRevenue: number;
  monthlyCOGS: number;
  monthlyLabor: number;
  monthlyOverhead: number;
  monthlyProfit: number;
  averagePrice: number;
  unitsSold: number;
  marketingSpend: number;
}

export interface OperationalFactors {
  laborAutomationLevel: number; // 0-80%
  productionEfficiency: number; // 100-150%
  inventoryTurnoverRate: number; // 6-12x per year
}

export interface ForecastData {
  month: string;
  originalProfit: number;
  adjustedProfit: number;
  originalLowerBound: number;
  originalUpperBound: number;
  adjustedLowerBound: number;
  adjustedUpperBound: number;
}

// Extract P&L data from uploaded file or simulation data
export const extractPLData = (simulationData: any): PLData => {
  // Default fallback data
  const defaultData: PLData = {
    monthlyRevenue: 100000,
    monthlyCOGS: 60000,
    monthlyLabor: 20000,
    monthlyOverhead: 12000,
    monthlyProfit: 8000,
    averagePrice: 50,
    unitsSold: 2000,
    marketingSpend: 3000
  };

  if (!simulationData) {
    return defaultData;
  }

  // Extract from simulation data structure
  const baseline = simulationData.baseline || {};
  const revenue = baseline.revenue || defaultData.monthlyRevenue;
  const costs = baseline.costs || {};
  const cogs = costs.cogs || defaultData.monthlyCOGS;
  const labor = costs.labor || defaultData.monthlyLabor;
  const overhead = costs.overhead || defaultData.monthlyOverhead;
  const profit = revenue - cogs - labor - overhead;

  // Estimate average price and units (could be enhanced with actual data)
  const averagePrice = simulationData.averagePrice || defaultData.averagePrice;
  const unitsSold = revenue / averagePrice;
  const marketingSpend = simulationData.marketingSpend || defaultData.marketingSpend;

  return {
    monthlyRevenue: revenue,
    monthlyCOGS: cogs,
    monthlyLabor: labor,
    monthlyOverhead: overhead,
    monthlyProfit: profit,
    averagePrice,
    unitsSold,
    marketingSpend
  };
};

// Calculate price elasticity impact
export const calculatePriceImpact = (baselineData: PLData, newPrice: number) => {
  const priceChangePercent = (newPrice - baselineData.averagePrice) / baselineData.averagePrice;
  let demandChangePercent;
  
  if (priceChangePercent > 0) {
    // Price increase: 10% price increase = 15% demand decrease
    demandChangePercent = -priceChangePercent * 1.5;
  } else {
    // Price decrease: 10% price decrease = 8% demand increase
    demandChangePercent = -priceChangePercent * 0.8;
  }
  
  const newUnits = baselineData.unitsSold * (1 + demandChangePercent);
  const newRevenue = newPrice * newUnits;
  const newCOGS = (newRevenue / baselineData.monthlyRevenue) * baselineData.monthlyCOGS;
  
  return {
    revenue: newRevenue,
    cogs: newCOGS,
    units: newUnits,
    demandChange: demandChangePercent
  };
};

// Calculate marketing impact with diminishing returns
export const calculateMarketingImpact = (baselineData: PLData, marketingSpend: number) => {
  const additionalSpend = marketingSpend - baselineData.marketingSpend;
  let revenueBoostPercent = 0;
  
  if (additionalSpend > 0) {
    // First $10k = 20% boost
    const firstTier = Math.min(additionalSpend, 10000);
    revenueBoostPercent += (firstTier / 10000) * 0.20;
    
    // Next $10k = 10% additional boost
    if (additionalSpend > 10000) {
      const secondTier = Math.min(additionalSpend - 10000, 10000);
      revenueBoostPercent += (secondTier / 10000) * 0.10;
      
      // Beyond $20k = 5% per $10k (capped at 50% total)
      if (additionalSpend > 20000) {
        const thirdTier = additionalSpend - 20000;
        const thirdTierBoost = Math.min((thirdTier / 10000) * 0.05, 0.20); // Cap at 20% for third tier
        revenueBoostPercent += thirdTierBoost;
      }
    }
  }
  
  return Math.min(revenueBoostPercent, 0.50); // Cap total at 50%
};

// Calculate labor automation impact
export const calculateLaborAutomationImpact = (baselineData: PLData, automationLevel: number) => {
  try {
    // Baseline: 10% automation, labor is 35% of total operating expenses
    const baselineAutomation = 10; // 10%
    const totalOperatingExpenses = baselineData.monthlyCOGS + baselineData.monthlyLabor + baselineData.monthlyOverhead;
    const baselineLaborCost = totalOperatingExpenses * 0.35;
    
    // Calculate automation change
    const automationChange = automationLevel - baselineAutomation;
    const automationTiers = Math.floor(automationChange / 10);
    
    // Each 10% automation reduces labor costs by 8%
    const laborCostReduction = automationTiers * 0.08 * baselineLaborCost;
    
    // Automation investment: $2,000/month per 10% automation
    const automationInvestment = automationTiers * 2000;
    
    // Net impact = savings - investment
    const netImpact = laborCostReduction - automationInvestment;
    
    return {
      laborCostReduction: laborCostReduction || 0,
      automationInvestment: automationInvestment || 0,
      netImpact: netImpact || 0
    };
  } catch (error) {
    console.error('Error calculating labor automation impact:', error);
    return { laborCostReduction: 0, automationInvestment: 0, netImpact: 0 };
  }
};

// Calculate production efficiency impact
export const calculateProductionEfficiencyImpact = (baselineData: PLData, efficiencyLevel: number) => {
  try {
    // Baseline: 100% efficiency, COGS is 60% of revenue
    const baselineEfficiency = 100;
    const baselineCOGS = baselineData.monthlyRevenue * 0.60;
    
    // Calculate efficiency change
    const efficiencyChange = efficiencyLevel - baselineEfficiency;
    const efficiencyTiers = Math.floor(efficiencyChange / 10);
    
    // Each 10% efficiency increase reduces COGS by 6%
    const cogsReduction = efficiencyTiers * 0.06 * baselineCOGS;
    
    // Increases production capacity (allowing 5% more revenue potential)
    const revenueIncrease = efficiencyTiers * 0.05 * baselineData.monthlyRevenue;
    
    // Implementation cost: $1,500/month amortized per 10% improvement
    const implementationCost = efficiencyTiers * 1500;
    
    // Net impact = savings + revenue increase - implementation cost
    const netImpact = cogsReduction + revenueIncrease - implementationCost;
    
    return {
      cogsReduction: cogsReduction || 0,
      revenueIncrease: revenueIncrease || 0,
      implementationCost: implementationCost || 0,
      netImpact: netImpact || 0
    };
  } catch (error) {
    console.error('Error calculating production efficiency impact:', error);
    return { cogsReduction: 0, revenueIncrease: 0, implementationCost: 0, netImpact: 0 };
  }
};

// Calculate inventory turnover impact
export const calculateInventoryTurnoverImpact = (baselineData: PLData, turnoverRate: number) => {
  try {
    // Baseline: 6x per year turnover
    const baselineTurnover = 6;
    
    // Calculate turnover change
    const turnoverChange = turnoverRate - baselineTurnover;
    
    // Each 1x increase reduces carrying costs by $500/month
    const carryingCostReduction = turnoverChange * 500;
    
    // Reduces waste/obsolescence costs by $300/month per 1x increase
    const wasteReduction = turnoverChange * 300;
    
    // Implementation cost: $800/month for inventory management per 2x increase
    const implementationCost = Math.floor(turnoverChange / 2) * 800;
    
    // Cash flow improvement (3% working capital reduction per 1x increase)
    // This doesn't directly affect monthly profit but is noted for ROI
    const workingCapitalReduction = turnoverChange * 0.03;
    
    // Net impact = carrying cost savings + waste reduction - implementation cost
    const netImpact = carryingCostReduction + wasteReduction - implementationCost;
    
    return {
      carryingCostReduction: carryingCostReduction || 0,
      wasteReduction: wasteReduction || 0,
      implementationCost: implementationCost || 0,
      workingCapitalReduction: workingCapitalReduction || 0,
      netImpact: netImpact || 0
    };
  } catch (error) {
    console.error('Error calculating inventory turnover impact:', error);
    return { carryingCostReduction: 0, wasteReduction: 0, implementationCost: 0, workingCapitalReduction: 0, netImpact: 0 };
  }
};

// Generate 12-month forecast with seasonal variation
export const generateForecastData = (
  baselineData: PLData,
  priceValue: number,
  marketingValue: number,
  operationalFactors?: OperationalFactors
): ForecastData[] => {
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const seasonalFactors = [0.95, 0.92, 1.02, 1.05, 1.08, 1.12, 1.15, 1.10, 1.05, 1.00, 0.90, 0.85];
  
  const priceImpact = calculatePriceImpact(baselineData, priceValue);
  const marketingBoost = calculateMarketingImpact(baselineData, marketingValue);
  
  // Calculate operational impacts if provided
  const automationImpact = operationalFactors ? 
    calculateLaborAutomationImpact(baselineData, operationalFactors.laborAutomationLevel) : 
    { netImpact: 0 };
  
  const efficiencyImpact = operationalFactors ? 
    calculateProductionEfficiencyImpact(baselineData, operationalFactors.productionEfficiency) : 
    { netImpact: 0, revenueIncrease: 0, cogsReduction: 0 };
  
  const inventoryImpact = operationalFactors ? 
    calculateInventoryTurnoverImpact(baselineData, operationalFactors.inventoryTurnoverRate) : 
    { netImpact: 0 };
  
  return months.map((month, index) => {
    const growthFactor = 1 + (0.035 * (index / 12)); // 3.5% annual growth
    const seasonalFactor = seasonalFactors[index];
    
    // Original forecast
    const baseProfit = baselineData.monthlyProfit * growthFactor * seasonalFactor;
    const originalProfit = baseProfit;
    
    // Adjusted forecast with all impacts
    let adjustedRevenue = priceImpact.revenue * (1 + marketingBoost) * growthFactor * seasonalFactor;
    let adjustedCOGS = priceImpact.cogs * growthFactor * seasonalFactor;
    
    // Add operational impacts
    adjustedRevenue += (efficiencyImpact.revenueIncrease || 0) * growthFactor * seasonalFactor;
    adjustedCOGS -= (efficiencyImpact.cogsReduction || 0) * growthFactor * seasonalFactor;
    
    // Calculate adjusted profit with all operational impacts
    const adjustedProfit = adjustedRevenue - adjustedCOGS - baselineData.monthlyLabor - baselineData.monthlyOverhead - marketingValue + 
                          (automationImpact.netImpact || 0) + (inventoryImpact.netImpact || 0);
    
    // Confidence bands (±15%)
    const confidenceRange = 0.15;
    
    return {
      month,
      originalProfit: Math.round(originalProfit || 0),
      adjustedProfit: Math.round(adjustedProfit || 0),
      originalLowerBound: Math.round((originalProfit || 0) * (1 - confidenceRange)),
      originalUpperBound: Math.round((originalProfit || 0) * (1 + confidenceRange)),
      adjustedLowerBound: Math.round((adjustedProfit || 0) * (1 - confidenceRange)),
      adjustedUpperBound: Math.round((adjustedProfit || 0) * (1 + confidenceRange))
    };
  });
};

// Calculate summary metrics
export const calculateSummaryMetrics = (
  baselineData: PLData,
  forecastData: ForecastData[],
  marketingValue: number,
  operationalFactors?: OperationalFactors
) => {
  const currentProfit = baselineData.monthlyProfit;
  const newProfit = forecastData[0]?.adjustedProfit || 0;
  const monthlyDifference = newProfit - currentProfit;
  const annualDifference = monthlyDifference * 12;
  
  // Calculate total investment including operational factors
  let totalInvestment = (marketingValue - baselineData.marketingSpend) * 12;
  
  if (operationalFactors) {
    const automationImpact = calculateLaborAutomationImpact(baselineData, operationalFactors.laborAutomationLevel);
    const efficiencyImpact = calculateProductionEfficiencyImpact(baselineData, operationalFactors.productionEfficiency);
    const inventoryImpact = calculateInventoryTurnoverImpact(baselineData, operationalFactors.inventoryTurnoverRate);
    
    totalInvestment += (automationImpact.automationInvestment || 0) * 12;
    totalInvestment += (efficiencyImpact.implementationCost || 0) * 12;
    totalInvestment += (inventoryImpact.implementationCost || 0) * 12;
  }
  
  const roi = totalInvestment > 0 ? (annualDifference / totalInvestment) * 100 : 0;
  
  return {
    currentProfit,
    newProfit,
    monthlyDifference,
    annualDifference,
    roi: Math.round(roi * 10) / 10,
    totalInvestment: Math.round(totalInvestment)
  };
};