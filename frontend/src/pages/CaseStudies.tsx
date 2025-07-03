
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const CaseStudies = () => {
  const [activeTab, setActiveTab] = useState(0);

  const caseStudies = [
    {
      title: "Manufacturing Company",
      company: "TechFlow Manufacturing",
      challenge: "TechFlow was experiencing significant bottlenecks in their production line, leading to delayed deliveries and increased operational costs. They lacked visibility into their end-to-end manufacturing process.",
      solution: "SPAIK created a comprehensive digital twin of their entire manufacturing process, integrating real-time data from sensors, ERP systems, and quality control checkpoints. Our AI models identified optimal production schedules and resource allocation strategies.",
      results: {
        roi: "280%",
        costSavings: "$1.2M annually",
        efficiency: "35% improvement in production efficiency",
        time: "50% reduction in order fulfillment time"
      },
      beforeAfter: "Production uptime increased from 72% to 94%",
      quote: "SPAIK's digital twin revolutionized our operations. We can now predict and prevent issues before they impact production."
    },
    {
      title: "Retail Business",
      company: "RetailMax Solutions",
      challenge: "RetailMax struggled with inventory management across 50+ locations, resulting in frequent stockouts, overstock situations, and poor customer satisfaction. Manual forecasting was proving inadequate.",
      solution: "We implemented an AI-powered inventory optimization system using digital twin technology to model customer behavior, seasonal trends, and supply chain dynamics. The system provides real-time recommendations for stock levels and reorder points.",
      results: {
        roi: "340%",
        costSavings: "$800K in reduced inventory costs",
        efficiency: "40% improvement in stock turnover",
        time: "60% reduction in stockout incidents"
      },
      beforeAfter: "Inventory accuracy improved from 78% to 96%",
      quote: "Our inventory management has been completely transformed. We now have the right products in the right places at the right time."
    },
    {
      title: "Tech Startup",
      company: "GrowthStart Inc.",
      challenge: "GrowthStart was burning through capital quickly without clear visibility into which initiatives were driving growth. They needed better resource allocation and ROI measurement across marketing channels and product development.",
      solution: "SPAIK built a financial digital twin that models cash flow, customer acquisition costs, lifetime value, and growth scenarios. Our platform provides predictive analytics for budget allocation and growth strategy optimization.",
      results: {
        roi: "420%",
        costSavings: "40% reduction in customer acquisition cost",
        efficiency: "60% improvement in marketing ROI",
        time: "3 months to break-even (from 8 months)"
      },
      beforeAfter: "Monthly recurring revenue growth increased from 12% to 35%",
      quote: "SPAIK helped us optimize our growth strategy and achieve profitability 5 months ahead of schedule."
    },
    {
      title: "Service Company",
      company: "ProServe Solutions",
      challenge: "ProServe was struggling with high customer acquisition costs and low conversion rates. Their sales process was inefficient, and they lacked insight into which marketing channels and customer segments were most profitable.",
      solution: "We created a customer journey digital twin that maps the entire sales funnel, integrating CRM data, marketing analytics, and customer behavior patterns. AI models identify high-value prospects and optimize touchpoint timing.",
      results: {
        roi: "380%",
        costSavings: "55% reduction in customer acquisition cost",
        efficiency: "45% increase in conversion rates",
        time: "30% shorter sales cycle"
      },
      beforeAfter: "Lead qualification accuracy improved from 45% to 87%",
      quote: "Our sales team is now 3x more effective, and we're closing higher-value deals with better customers."
    }
  ];

  return (
    <div className="container mx-auto px-6 py-16">
      {/* Header */}
      <Card className="professional-card mb-16">
        <CardContent className="p-16 text-center">
          <h1 className="text-6xl font-bold professional-heading mb-8">Success Stories</h1>
          <p className="text-xl professional-text max-w-4xl mx-auto">
            Discover how businesses across different industries have transformed their operations with SPAIK's digital twin technology
          </p>
        </CardContent>
      </Card>

      {/* Tabbed Interface */}
      <Card className="professional-card">
        <CardHeader>
          <div className="flex flex-wrap gap-3">
            {caseStudies.map((study, index) => (
              <button
                key={index}
                onClick={() => setActiveTab(index)}
                className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
                  activeTab === index
                    ? 'bg-purple-600 text-white shadow-md'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {study.title}
              </button>
            ))}
          </div>
        </CardHeader>
        
        <CardContent className="p-12">
          {caseStudies.map((study, index) => (
            <div
              key={index}
              className={`space-y-10 ${activeTab === index ? 'block' : 'hidden'}`}
            >
              {/* Company Challenge */}
              <div>
                <h3 className="text-3xl professional-heading mb-6">The Challenge</h3>
                <p className="professional-text text-lg leading-relaxed">{study.challenge}</p>
              </div>

              {/* SPAIK Solution */}
              <div>
                <h3 className="text-3xl professional-heading mb-6">Our Solution</h3>
                <p className="professional-text text-lg leading-relaxed">{study.solution}</p>
              </div>

              {/* Results */}
              <div>
                <h3 className="text-3xl professional-heading mb-6">Results Achieved</h3>
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                  <div className="bg-purple-50 p-8 rounded-lg border border-purple-100 text-center">
                    <div className="text-4xl font-bold text-purple-600 mb-3">{study.results.roi}</div>
                    <div className="text-sm font-medium text-gray-700">ROI</div>
                  </div>
                  <div className="bg-blue-50 p-8 rounded-lg border border-blue-100 text-center">
                    <div className="text-lg font-bold text-blue-600 mb-3">{study.results.costSavings}</div>
                    <div className="text-sm font-medium text-gray-700">Cost Savings</div>
                  </div>
                  <div className="bg-green-50 p-8 rounded-lg border border-green-100 text-center">
                    <div className="text-lg font-bold text-green-600 mb-3">{study.results.efficiency}</div>
                    <div className="text-sm font-medium text-gray-700">Efficiency Gain</div>
                  </div>
                  <div className="bg-orange-50 p-8 rounded-lg border border-orange-100 text-center">
                    <div className="text-lg font-bold text-orange-600 mb-3">{study.results.time}</div>
                    <div className="text-sm font-medium text-gray-700">Time Saved</div>
                  </div>
                </div>
              </div>

              {/* Before/After */}
              <div className="bg-gray-50 p-8 rounded-lg border border-gray-100">
                <h4 className="text-xl font-semibold professional-heading mb-4">Key Improvement</h4>
                <p className="professional-text text-lg">{study.beforeAfter}</p>
              </div>

              {/* Quote */}
              <div className="bg-gradient-to-r from-purple-600 to-blue-600 p-10 rounded-lg text-white">
                <blockquote className="text-xl italic mb-6">"{study.quote}"</blockquote>
                <cite className="text-purple-200 font-medium text-lg">— {study.company}</cite>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
};

export default CaseStudies;
