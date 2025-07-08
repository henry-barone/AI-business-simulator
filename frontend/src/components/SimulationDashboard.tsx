
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, DollarSign, Calendar, Target, CheckCircle, AlertCircle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar } from 'recharts';
import { API_BASE_URL } from '@/lib/api';

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
  };
}

interface DashboardProps {
  companyId: string;
}

const SimulationDashboard: React.FC<DashboardProps> = ({ companyId }) => {
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
          recommendations: [
            {
              type: "Labor Automation",
              description: "Implement AI-powered labor optimization systems",
              savings: laborSavings,
              cost: (enhancedData.optimizations?.labor?.implementation_cost || 0) + 
                    (enhancedData.optimizations?.labor?.training_cost || 0),
              priority: 1
            },
            {
              type: "Quality Control",
              description: "Deploy automated quality assurance and inspection systems",
              savings: qualitySavings,
              cost: (enhancedData.optimizations?.quality?.quality_system_cost || 0) + 
                    (enhancedData.optimizations?.quality?.training_cost || 0),
              priority: 2
            },
            {
              type: "Inventory Management",
              description: "Optimize inventory with smart forecasting and automated tracking",
              savings: inventorySavings,
              cost: (enhancedData.optimizations?.inventory?.system_cost || 0) + 
                    (enhancedData.optimizations?.inventory?.training_cost || 0),
              priority: 3
            },
            {
              type: "Customer Service",
              description: "Automate customer service with AI-powered support systems",
              savings: serviceSavings,
              cost: (enhancedData.optimizations?.service?.automation_platform_cost || 0) + 
                    (enhancedData.optimizations?.service?.setup_cost || 0),
              priority: 4
            }
          ],
          roi_metrics: {
            total_investment: enhancedData.summary?.total_implementation_cost || 0,
            payback_months: enhancedData.break_even_analysis?.break_even_month || 
                           enhancedData.metrics?.payback_months || 12,
            roi_percentage: enhancedData.break_even_analysis?.final_roi_percentage || 
                           enhancedData.metrics?.roi_percentage || 0
          },
          summary_metrics: {
            total_savings: enhancedData.summary?.total_annual_savings || 0,
            confidence_score: enhancedData.metrics?.confidence_score || 85
          }
        };
        
        console.log('Enhanced simulation data:', enhancedData);
        console.log('Transformed data:', transformedData);
        setData(transformedData);
      } else {
        // Fallback to regular simulation endpoint
        response = await fetch(`${API_BASE_URL}/companies/${companyId}/simulation`);
        if (!response.ok) {
          throw new Error('Failed to fetch simulation data');
        }
        const result = await response.json();
        setData(result.data.simulation);
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
                <p className="text-sm text-gray-600">ROI</p>
                <p className="text-2xl font-bold text-purple-600">{data.roi_metrics.roi_percentage}%</p>
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
                <div key={index} className="flex items-start gap-4 p-4 border border-gray-200 rounded-lg">
                  <CheckCircle className="h-6 w-6 text-green-500 mt-1 flex-shrink-0" />
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h4 className="font-semibold text-gray-900">{rec.description}</h4>
                      <Badge variant="outline">Priority {rec.priority}</Badge>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                      <div>Annual Savings: <span className="font-medium text-green-600">${rec.savings.toLocaleString()}</span></div>
                      <div>Implementation Cost: <span className="font-medium text-gray-900">${rec.cost.toLocaleString()}</span></div>
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
