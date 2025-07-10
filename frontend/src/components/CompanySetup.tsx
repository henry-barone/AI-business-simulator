
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { apiRequest } from '@/lib/api';

interface CompanySetupProps {
  onComplete: (companyData: { id: string; name: string; email: string; emailConsent: boolean }) => void;
}

const CompanySetup: React.FC<CompanySetupProps> = ({ onComplete }) => {
  const [companyName, setCompanyName] = useState('');
  const [email, setEmail] = useState('');
  const [emailConsent, setEmailConsent] = useState(false);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();


  const validateEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!companyName.trim() || !email.trim()) {
      toast({
        title: "Missing information",
        description: "Please fill in all required fields.",
        variant: "destructive"
      });
      return;
    }

    if (!validateEmail(email)) {
      toast({
        title: "Invalid email",
        description: "Please enter a valid email address.",
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
          email: email.trim(),
          emailConsent: emailConsent
        }),
      });

      onComplete({
        id: data.data.id,
        name: companyName.trim(),
        email: email.trim(),
        emailConsent: emailConsent
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
            <Label htmlFor="email">Email Address *</Label>
            <Input
              id="email"
              type="email"
              placeholder="Enter your email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>

          <div className="space-y-3">
            <div className="flex items-start space-x-3">
              <input
                type="checkbox"
                id="emailConsent"
                checked={emailConsent}
                onChange={(e) => setEmailConsent(e.target.checked)}
                className="w-4 h-4 text-purple-600 bg-gray-100 border-gray-300 rounded focus:ring-purple-500 focus:ring-2 mt-1"
              />
              <label htmlFor="emailConsent" className="text-sm text-gray-600 leading-relaxed">
                I agree to receive the AI assessment report via email and occasional updates about SPAIK's AI solutions.
              </label>
            </div>
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
