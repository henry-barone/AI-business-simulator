
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { apiRequest } from '@/lib/api';

interface CompanySetupProps {
  onComplete: (companyData: { id: string; name: string; industry: string }) => void;
}

const CompanySetup: React.FC<CompanySetupProps> = ({ onComplete }) => {
  const [companyName, setCompanyName] = useState('');
  const [industry, setIndustry] = useState('');
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const industries = [
    'Manufacturing',
    'Retail',
    'Technology',
    'Healthcare',
    'Financial Services',
    'Automotive',
    'Food & Beverage',
    'Logistics & Transportation',
    'Construction',
    'Other'
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!companyName.trim() || !industry) {
      toast({
        title: "Missing information",
        description: "Please fill in all required fields.",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    try {
      const data = await apiRequest('/companies', {
        method: 'POST',
        body: JSON.stringify({
          name: companyName.trim(),
          industry: industry
        }),
      });

      onComplete({
        id: data.data.id,
        name: companyName.trim(),
        industry: industry
      });
    } catch (error) {
      console.error('Company setup error:', error);
      toast({
        title: "Error",
        description: "Failed to set up company. Please try again.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="professional-card max-w-lg mx-auto">
      <CardHeader className="text-center">
        <CardTitle className="professional-heading text-2xl">Company Setup</CardTitle>
        <p className="professional-text">
          Let's start by setting up your company profile for the business simulation.
        </p>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="company-name">Company Name *</Label>
            <Input
              id="company-name"
              type="text"
              placeholder="Enter your company name"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="industry">Industry *</Label>
            <select
              id="industry"
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
              required
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="">Select your industry</option>
              {industries.map((ind) => (
                <option key={ind} value={ind}>
                  {ind}
                </option>
              ))}
            </select>
          </div>

          <Button
            type="submit"
            disabled={loading}
            className="w-full professional-button"
          >
            {loading ? 'Setting up...' : 'Continue to File Upload'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};

export default CompanySetup;
