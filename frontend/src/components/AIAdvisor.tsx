
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Brain, Sparkles } from 'lucide-react';

const AIAdvisor = () => {
  return (
    <Card className="h-fit bg-card/50 backdrop-blur-sm border-border/50">
      <CardHeader>
        <CardTitle className="text-xl font-semibold flex items-center gap-2">
          <Brain className="w-5 h-5 text-purple-400" />
          AI Business Advisor
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="bg-muted/30 rounded-lg p-4 border border-border/30">
          <p className="text-sm text-muted-foreground leading-relaxed">
            Your personalized recommendations for automation and process improvements will appear here once you create your digital twin.
          </p>
        </div>
        
        <Button className="w-full gradient-button text-white py-3 px-6 text-sm font-medium flex items-center justify-center gap-2">
          <Sparkles className="w-4 h-4" />
          Create Your Company's Digital Twin
        </Button>
      </CardContent>
    </Card>
  );
};

export default AIAdvisor;
