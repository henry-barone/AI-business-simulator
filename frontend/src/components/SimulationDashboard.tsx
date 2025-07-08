
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, DollarSign, Calendar, Target, CheckCircle, AlertCircle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar } from 'recharts';
import { API_BASE_URL } from '@/lib/api';
import PDFReportGenerator from '@/components/PDFReportGenerator';

interface SimulationData {
  baseline: {
    revenue: number;
    costs: {
      labor: number;
      cogs: number;
      overhead: number;
    };
  };
  optimized: {
    costs: {
      labor: number;
      cogs: number;
      overhead: number;
    };
  };
  timeline_projections: Array<{
    month: number;
    savings: number;
    cumulative: number;
  }>;
  recommendations: Array<{
    type: string;
    description: string;
    savings: number;
    cost: number;
    priority: number;
  }>;
  roi_metrics: {
    total_investment: number;
    payback_months: number;
    roi_percentage: number;
    annual_roi?: number;
    three_year_roi?: number;
    five_year_roi?: number;
    break_even_date?: string;
  };
}

interface DashboardProps {
  companyId: string;
  companyName?: string;
  onDataLoaded?: (data: SimulationData) => void;
}

const SimulationDashboard: React.FC<DashboardProps> = ({ companyId, companyName, onDataLoaded }) => {
  const [data, setData] = useState<SimulationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [confidenceScore] = useState(87); // Mock confidence score

  useEffect(() => {
    fetchSimulationData();
  }, [companyId]);

  const fetchSimulationData = async () => {
    try {
      // First try enhanced simulation endpoint
      let response = await fetch(`${API_BASE_URL}/companies/${companyId}/enhanced-simulation`);
      
      if (response.ok) {
        const result = await response.json();
        // Transform enhanced simulation data to match dashboard format
        const enhancedData = result.data;
        
        // Calculate current costs
        const currentLaborCosts = (enhancedData.baseline.cost_breakdown.direct_labor_cost || 0) + 
                                 (enhancedData.baseline.cost_breakdown.indirect_labor_cost || 0);
        const currentCogs = enhancedData.baseline.cogs || 0;
        const currentOverhead = enhancedData.baseline.overhead_costs || 0;
        
        // Calculate optimized costs (current costs minus savings)
        const laborSavings = enhancedData.optimizations?.labor?.total_annual_savings || 0;
        const qualitySavings = enhancedData.optimizations?.quality?.total_annual_savings || 0;
        const inventorySavings = enhancedData.optimizations?.inventory?.total_annual_savings || 0;
        const serviceSavings = enhancedData.optimizations?.service?.total_annual_savings || 0;
        
        const optimizedLaborCosts = Math.max(0, currentLaborCosts - laborSavings);
        const optimizedCogs = Math.max(0, currentCogs - qualitySavings);
        const optimizedOverhead = Math.max(0, currentOverhead - inventorySavings - serviceSavings);
        
        const transformedData = {
          baseline: {
            revenue: enhancedData.baseline.revenue || 0,
            costs: {
              labor: currentLaborCosts,
              cogs: currentCogs,
              overhead: currentOverhead
            }
          },
          optimized: {
            costs: {
              labor: optimizedLaborCosts,
              cogs: optimizedCogs,
              overhead: optimizedOverhead
            }
          },
          timeline_projections: (enhancedData.projections || []).map((p: any, index: number) => {
            // Calculate cumulative savings (positive values) instead of cash flow
            const monthlySavings = Math.max(0, p.total_savings || 0);
            const cumulativeSavings = index === 0 ? monthlySavings : 
              (enhancedData.projections.slice(0, index + 1).reduce((sum: number, proj: any) => 
                sum + Math.max(0, proj.total_savings || 0), 0));
            
            return {
              month: p.month || index + 1,
              savings: monthlySavings,
              cumulative: cumulativeSavings
            };
          }),
          recommendations: enhancedData.smart_recommendations || [
            {
              title: "Labor Automation",
              description: "Implement AI-powered labor optimization systems",
              annual_savings: laborSavings,
              implementation_cost: (enhancedData.optimizations?.labor?.implementation_cost || 0) + 
                    (enhancedData.optimizations?.labor?.training_cost || 0),
              priority: 1,
              type: 'standard',
              three_year_savings: laborSavings * 3,
              five_year_savings: laborSavings * 5,
              three_year_roi: 0,
              payback_months: 12
            },
            {
              title: "Quality Control",
              description: "Deploy automated quality assurance and inspection systems",
              annual_savings: qualitySavings,
              implementation_cost: (enhancedData.optimizations?.quality?.quality_system_cost || 0) + 
                    (enhancedData.optimizations?.quality?.training_cost || 0),
              priority: 2,
              type: 'standard',
              three_year_savings: qualitySavings * 3,
              five_year_savings: qualitySavings * 5,
              three_year_roi: 0,
              payback_months: 12
            },
            {
              title: "Inventory Management",
              description: "Optimize inventory with smart forecasting and automated tracking",
              annual_savings: inventorySavings,
              implementation_cost: (enhancedData.optimizations?.inventory?.system_cost || 0) + 
                    (enhancedData.optimizations?.inventory?.training_cost || 0),
              priority: 3,
              type: 'standard',
              three_year_savings: inventorySavings * 3,
              five_year_savings: inventorySavings * 5,
              three_year_roi: 0,
              payback_months: 12
            },
            {
              title: "Customer Service",
              description: "Automate customer service with AI-powered support systems",
              annual_savings: serviceSavings,
              implementation_cost: (enhancedData.optimizations?.service?.automation_platform_cost || 0) + 
                    (enhancedData.optimizations?.service?.setup_cost || 0),
              priority: 4,
              type: 'standard',
              three_year_savings: serviceSavings * 3,
              five_year_savings: serviceSavings * 5,
              three_year_roi: 0,
              payback_months: 12
            }
          ],
          roi_metrics: {
            total_investment: enhancedData.summary?.total_implementation_cost || 0,
            payback_months: enhancedData.break_even_analysis?.break_even_month || 
                           enhancedData.metrics?.payback_months || 12,
            roi_percentage: enhancedData.break_even_analysis?.final_roi_percentage || 
                           enhancedData.metrics?.roi_percentage || 0,
            annual_roi: enhancedData.roi_metrics?.annual_roi || enhancedData.break_even_analysis?.roi_metrics?.annual_roi || 0,
            three_year_roi: enhancedData.roi_metrics?.three_year_roi || enhancedData.break_even_analysis?.roi_metrics?.three_year_roi || 0,
            five_year_roi: enhancedData.roi_metrics?.five_year_roi || enhancedData.break_even_analysis?.roi_metrics?.five_year_roi || 0,
            break_even_date: enhancedData.roi_metrics?.break_even_date || enhancedData.break_even_analysis?.roi_metrics?.break_even_date
          },
          summary_metrics: {
            total_savings: enhancedData.summary?.total_annual_savings || 0,
            confidence_score: enhancedData.metrics?.confidence_score || 85
          }
        };
        
        console.log('Enhanced simulation data:', enhancedData);
        console.log('Transformed data:', transformedData);
        setData(transformedData);
        onDataLoaded?.(transformedData);
      } else {
        // Fallback to regular simulation endpoint
        response = await fetch(`${API_BASE_URL}/companies/${companyId}/simulation`);
        if (!response.ok) {
          throw new Error('Failed to fetch simulation data');
        }
        const result = await response.json();
        setData(result.data.simulation);
        onDataLoaded?.(result.data.simulation);
      }
    } catch (error) {
      console.error('Error fetching simulation data:', error);
      console.error('Company ID:', companyId);
      console.error('API Base URL:', API_BASE_URL);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i} className="professional-card">
            <CardContent className="p-6">
              <div className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                <div className="h-32 bg-gray-200 rounded"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (!data) {
    return (
      <Card className="professional-card">
        <CardContent className="p-8 text-center">
          <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="professional-text">Failed to load simulation data</p>
        </CardContent>
      </Card>
    );
  }

  const totalCurrentCosts = data.baseline.costs.labor + data.baseline.costs.cogs + data.baseline.costs.overhead;
  const totalOptimizedCosts = data.optimized.costs.labor + data.optimized.costs.cogs + data.optimized.costs.overhead;
  const totalSavings = data.summary_metrics?.total_savings || (totalCurrentCosts - totalOptimizedCosts);

  const costComparisonData = [
    {
      name: 'Current Costs',
      labor: data.baseline.costs.labor,
      cogs: data.baseline.costs.cogs,
      overhead: data.baseline.costs.overhead,
    },
    {
      name: 'Optimized Costs',
      labor: data.optimized.costs.labor,
      cogs: data.optimized.costs.cogs,
      overhead: data.optimized.costs.overhead,
    },
  ];

  const pieData = [
    { name: 'Labor', value: data.optimized.costs.labor, color: '#8B5CF6' },
    { name: 'COGS', value: data.optimized.costs.cogs, color: '#06B6D4' },
    { name: 'Overhead', value: data.optimized.costs.overhead, color: '#10B981' },
  ].filter(item => item.value > 0); // Only show non-zero values

  return (
    <div className="space-y-6">
      {/* Executive Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="professional-card">
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <DollarSign className="h-8 w-8 text-green-600" />
              <div>
                <p className="text-sm text-gray-600">Total Savings</p>
                <p className="text-2xl font-bold text-green-600">${totalSavings.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="professional-card">
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <TrendingUp className="h-8 w-8 text-purple-600" />
              <div>
                <p className="text-sm text-gray-600">3-Year ROI</p>
                <p className={`text-2xl font-bold ${
                  (data.roi_metrics.three_year_roi || data.roi_metrics.roi_percentage || 0) >= 0 ? 'text-purple-600' : 'text-red-600'
                }`}>
                  {(data.roi_metrics.three_year_roi || data.roi_metrics.roi_percentage || 0).toFixed(0)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="professional-card">
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <Calendar className="h-8 w-8 text-blue-600" />
              <div>
                <p className="text-sm text-gray-600">Payback Period</p>
                <p className="text-2xl font-bold text-blue-600">{data.roi_metrics.payback_months} months</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="professional-card">
          <CardContent className="p-6">
            <div className="flex items-center gap-3">
              <Target className="h-8 w-8 text-orange-600" />
              <div>
                <p className="text-sm text-gray-600">Confidence Score</p>
                <p className="text-2xl font-bold text-orange-600">{data.summary_metrics?.confidence_score || confidenceScore}%</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Comprehensive ROI Metrics */}
      <Card className="professional-card">
        <CardHeader>
          <CardTitle className="professional-heading">Return on Investment Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            <div className="text-center p-4 border border-gray-200 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Total Investment</p>
              <p className="text-xl font-bold text-gray-900">${data.roi_metrics.total_investment.toLocaleString()}</p>
            </div>
            <div className="text-center p-4 border border-gray-200 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Annual ROI</p>
              <p className={`text-xl font-bold ${
                (data.roi_metrics.annual_roi || 0) >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {(data.roi_metrics.annual_roi || 0).toFixed(0)}%
              </p>
            </div>
            <div className="text-center p-4 border border-gray-200 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">3-Year ROI</p>
              <p className={`text-xl font-bold ${
                (data.roi_metrics.three_year_roi || 0) >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {(data.roi_metrics.three_year_roi || 0).toFixed(0)}%
              </p>
            </div>
            <div className="text-center p-4 border border-gray-200 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">5-Year ROI</p>
              <p className={`text-xl font-bold ${
                (data.roi_metrics.five_year_roi || 0) >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {(data.roi_metrics.five_year_roi || 0).toFixed(0)}%
              </p>
            </div>
            <div className="text-center p-4 border border-gray-200 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Break-Even</p>
              <p className="text-xl font-bold text-blue-600">
                {data.roi_metrics.break_even_date ? 
                  new Date(data.roi_metrics.break_even_date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' }) :
                  `${data.roi_metrics.payback_months} mo`
                }
              </p>
            </div>
          </div>
          
          {/* ROI Status Indicator */}
          <div className={`mt-6 p-4 rounded-lg ${
            (data.roi_metrics.three_year_roi || 0) >= 100 ? 'bg-green-50 border border-green-200' :
            (data.roi_metrics.three_year_roi || 0) >= 50 ? 'bg-yellow-50 border border-yellow-200' :
            'bg-red-50 border border-red-200'
          }`}>
            <div className="flex items-center gap-3">
              <div className={`w-3 h-3 rounded-full ${
                (data.roi_metrics.three_year_roi || 0) >= 100 ? 'bg-green-500' :
                (data.roi_metrics.three_year_roi || 0) >= 50 ? 'bg-yellow-500' :
                'bg-red-500'
              }`}></div>
              <p className="text-sm font-medium">
                {(data.roi_metrics.three_year_roi || 0) >= 100 ? 
                  'Excellent ROI - Strong investment opportunity with high returns' :
                (data.roi_metrics.three_year_roi || 0) >= 50 ? 
                  'Good ROI - Positive investment with moderate returns' :
                (data.roi_metrics.three_year_roi || 0) >= 0 ? 
                  'Break-even - Investment recovers costs over time' :
                  'Negative ROI - Investment may not recover costs in projected timeframe'
                }
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Before/After Comparison */}
      <Card className="professional-card">
        <CardHeader>
          <CardTitle className="professional-heading">Cost Comparison</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={costComparisonData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(value) => `$${Number(value).toLocaleString()}`} />
                <Bar dataKey="labor" fill="#8B5CF6" name="Labor" />
                <Bar dataKey="cogs" fill="#06B6D4" name="COGS" />
                <Bar dataKey="overhead" fill="#10B981" name="Overhead" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Timeline Chart */}
        <Card className="professional-card">
          <CardHeader>
            <CardTitle className="professional-heading">Cumulative Savings Over Time</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data.timeline_projections}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="month" 
                    label={{ value: 'Month', position: 'insideBottom', offset: -5 }}
                  />
                  <YAxis 
                    label={{ value: 'Cumulative Savings ($)', angle: -90, position: 'insideLeft' }}
                    tickFormatter={(value) => `$${(value / 1000).toFixed(0)}K`}
                  />
                  <Tooltip 
                    formatter={(value) => [`$${Number(value).toLocaleString()}`, 'Cumulative Savings']}
                    labelFormatter={(label) => `Month ${label}`}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="cumulative" 
                    stroke="#8B5CF6" 
                    strokeWidth={3}
                    dot={{ fill: '#8B5CF6', strokeWidth: 2, r: 4 }}
                    name="Cumulative Savings"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Cost Breakdown */}
        <Card className="professional-card">
          <CardHeader>
            <CardTitle className="professional-heading">Optimized Cost Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => `$${Number(value).toLocaleString()}`} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recommendations */}
      <Card className="professional-card">
        <CardHeader>
          <CardTitle className="professional-heading">AI Recommendations</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {data.recommendations
              .sort((a, b) => a.priority - b.priority)
              .map((rec, index) => (
                <div key={index} className={`p-4 border rounded-lg ${
                  rec.type === 'quick_win' ? 'border-green-300 bg-green-50' : 'border-gray-200'
                }`}>
                  <div className="flex items-start gap-4">
                    <CheckCircle className="h-6 w-6 text-green-500 mt-1 flex-shrink-0" />
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h4 className="font-semibold text-gray-900">{rec.title || rec.description}</h4>
                        <Badge variant="outline">Priority {rec.priority}</Badge>
                        {rec.type === 'quick_win' && (
                          <Badge className="bg-green-100 text-green-800">Quick Win</Badge>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 mb-3">{rec.description}</p>
                      
                      {/* Financial Metrics Grid */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div className="text-center p-2 bg-white rounded border">
                          <p className="text-gray-600">Annual Savings</p>
                          <p className="font-medium text-green-600">${(rec.annual_savings || rec.savings || 0).toLocaleString()}</p>
                        </div>
                        <div className="text-center p-2 bg-white rounded border">
                          <p className="text-gray-600">3-Year ROI</p>
                          <p className={`font-medium ${
                            (rec.three_year_roi || 0) >= 50 ? 'text-green-600' : 'text-yellow-600'
                          }`}>
                            {(rec.three_year_roi || 0).toFixed(0)}%
                          </p>
                        </div>
                        <div className="text-center p-2 bg-white rounded border">
                          <p className="text-gray-600">Payback Period</p>
                          <p className="font-medium text-blue-600">{rec.payback_months || 12} months</p>
                        </div>
                        <div className="text-center p-2 bg-white rounded border">
                          <p className="text-gray-600">Investment</p>
                          <p className="font-medium text-gray-900">${(rec.implementation_cost || rec.cost || 0).toLocaleString()}</p>
                        </div>
                      </div>
                      
                      {/* 3-Year vs 5-Year Comparison */}
                      <div className="mt-3 pt-3 border-t">
                        <div className="grid grid-cols-2 gap-4 text-xs text-gray-600">
                          <div>3-Year Savings: <span className="font-medium text-green-700">${(rec.three_year_savings || (rec.annual_savings || rec.savings || 0) * 3).toLocaleString()}</span></div>
                          <div>5-Year Savings: <span className="font-medium text-green-700">${(rec.five_year_savings || (rec.annual_savings || rec.savings || 0) * 5).toLocaleString()}</span></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SimulationDashboard;
