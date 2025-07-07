
import React from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowRight } from 'lucide-react';

const Overview = () => {
  const testimonials = [
    {
      name: "Sarah Johnson",
      company: "TechFlow Manufacturing",
      quote: "SPAIK's digital twin helped us reduce operational costs by 35% and identify bottlenecks we never knew existed."
    },
    {
      name: "Michael Chen",
      company: "RetailMax Solutions",
      quote: "The AI recommendations transformed our inventory management. We've seen a 40% improvement in stock turnover."
    },
    {
      name: "Emma Rodriguez",
      company: "GrowthStart Inc.",
      quote: "SPAIK's platform gave us data-driven insights that led to a 25% increase in our marketing ROI within 3 months."
    }
  ];

  const benefits = [
    "Digital twin creation for your entire business",
    "AI-powered recommendations for optimization",
    "ROI simulation capabilities",
    "Process automation insights"
  ];

  return (
    <div className="container mx-auto px-6 py-16 space-y-16">
      {/* Hero Section */}
      <Card className="professional-card">
        <CardContent className="p-16 text-center">
          <h1 className="text-6xl font-bold professional-heading mb-8">
            Create Your Business's Digital Twin Today
          </h1>
          <p className="text-xl professional-text mb-12 max-w-4xl mx-auto">
            Transform your business with our AI-powered optimization platform. 
            Get real-time insights, predictive analytics, and actionable recommendations 
            to drive growth and efficiency.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/simulation">
              <Button className="professional-button text-lg px-8 py-4">
                Start Business Analysis
                <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            </Link>
            <Link to="/sandbox">
              <Button variant="outline" className="border-purple-600 text-purple-600 hover:bg-purple-50 text-lg px-8 py-4">
                Try The Sandbox
                <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>

      {/* Client Testimonials */}
      <Card className="professional-card">
        <CardHeader className="text-center pb-8">
          <CardTitle className="text-4xl professional-heading">
            What Our Clients Say
          </CardTitle>
        </CardHeader>
        <CardContent className="px-12 pb-12">
          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="bg-gray-50 p-8 rounded-lg border border-gray-100">
                <p className="professional-text mb-6 italic text-lg">"{testimonial.quote}"</p>
                <div className="font-semibold text-gray-900 text-lg">{testimonial.name}</div>
                <div className="text-sm text-gray-500 mt-1">{testimonial.company}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Company Overview */}
      <Card className="professional-card">
        <CardContent className="p-12">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl professional-heading mb-6">About SPAIK</h2>
              <p className="professional-text mb-8 text-lg">
                SPAIK is an AI-consulting startup based in Amsterdam, specializing in 
                creating digital twins for businesses. We empower companies to optimize 
                their operations through cutting-edge artificial intelligence and data analytics.
              </p>
              <Link to="/about">
                <Button variant="outline" className="border-purple-600 text-purple-600 hover:bg-purple-50 font-medium px-6 py-3">
                  Learn More About SPAIK
                  <ArrowRight className="ml-2 w-4 h-4" />
                </Button>
              </Link>
            </div>
            <div className="bg-gradient-to-br from-purple-50 to-blue-50 p-10 rounded-lg border border-gray-100">
              <h3 className="text-2xl font-semibold professional-heading mb-6">Key Benefits</h3>
              <ul className="space-y-4">
                {benefits.map((benefit, index) => (
                  <li key={index} className="flex items-start">
                    <div className="w-2 h-2 bg-purple-600 rounded-full mt-3 mr-4 flex-shrink-0"></div>
                    <span className="professional-text text-lg">{benefit}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Overview;
