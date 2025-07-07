
import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { Label } from '@/components/ui/label';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { HelpCircle } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { API_BASE_URL } from '@/lib/api';

interface SlidersProps {
  simulationId: string;
  onUpdate: (data: any) => void;
}

interface SliderValues {
  laborAutomation: number;
  qualityAutomation: number;
  inventoryAutomation: number;
  implementationTimeline: number;
}

const AdjustmentSliders: React.FC<SlidersProps> = ({ simulationId, onUpdate }) => {
  const [values, setValues] = useState<SliderValues>({
    laborAutomation: 50,
    qualityAutomation: 30,
    inventoryAutomation: 40,
    implementationTimeline: 6,
  });
  const [isUpdating, setIsUpdating] = useState(false);
  const { toast } = useToast();

  const debouncedUpdate = useCallback(
    debounce(async (newValues: SliderValues) => {
      setIsUpdating(true);
      try {
        const response = await fetch(`${API_BASE_URL}/simulations/${simulationId}/adjust`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(newValues),
        });

        if (!response.ok) {
          throw new Error('Failed to update simulation');
        }

        const data = await response.json();
        onUpdate(data.data);
      } catch (error) {
        toast({
          title: "Update failed",
          description: "Failed to update simulation. Please try again.",
          variant: "destructive"
        });
      } finally {
        setIsUpdating(false);
      }
    }, 500),
    [simulationId, onUpdate]
  );

  useEffect(() => {
    debouncedUpdate(values);
  }, [values, debouncedUpdate]);

  const handleSliderChange = (key: keyof SliderValues, value: number[]) => {
    setValues(prev => ({
      ...prev,
      [key]: value[0]
    }));
  };

  const sliderConfigs = [
    {
      key: 'laborAutomation' as keyof SliderValues,
      label: 'Labor Automation Level',
      tooltip: 'Percentage of manual labor tasks that can be automated through AI and robotics',
      min: 0,
      max: 100,
      step: 5,
      unit: '%'
    },
    {
      key: 'qualityAutomation' as keyof SliderValues,
      label: 'Quality Automation Level',
      tooltip: 'Percentage of quality control processes that can be automated using AI inspection systems',
      min: 0,
      max: 100,
      step: 5,
      unit: '%'
    },
    {
      key: 'inventoryAutomation' as keyof SliderValues,
      label: 'Inventory Automation Level',
      tooltip: 'Percentage of inventory management tasks that can be automated through smart systems',
      min: 0,
      max: 100,
      step: 5,
      unit: '%'
    },
    {
      key: 'implementationTimeline' as keyof SliderValues,
      label: 'Implementation Timeline',
      tooltip: 'Number of months to fully implement the automation solutions',
      min: 3,
      max: 12,
      step: 1,
      unit: ' months'
    }
  ];

  return (
    <Card className="professional-card">
      <CardHeader>
        <CardTitle className="professional-heading flex items-center gap-2">
          Real-time Adjustments
          {isUpdating && (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600"></div>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-8">
        <TooltipProvider>
          {sliderConfigs.map((config) => (
            <div key={config.key} className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Label className="text-sm font-medium text-gray-900">
                    {config.label}
                  </Label>
                  <Tooltip>
                    <TooltipTrigger>
                      <HelpCircle className="h-4 w-4 text-gray-400" />
                    </TooltipTrigger>
                    <TooltipContent>
                      <p className="max-w-xs">{config.tooltip}</p>
                    </TooltipContent>
                  </Tooltip>
                </div>
                <div className="text-sm font-semibold text-purple-600">
                  {values[config.key]}{config.unit}
                </div>
              </div>
              
              <Slider
                value={[values[config.key]]}
                onValueChange={(value) => handleSliderChange(config.key, value)}
                max={config.max}
                min={config.min}
                step={config.step}
                className="w-full"
              />
              
              <div className="flex justify-between text-xs text-gray-500">
                <span>{config.min}{config.unit}</span>
                <span>{config.max}{config.unit}</span>
              </div>
            </div>
          ))}
        </TooltipProvider>
        
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            <strong>Tip:</strong> Adjust the sliders above to see how different automation levels and implementation timelines affect your projected savings and ROI in real-time.
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

// Debounce utility function
function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

export default AdjustmentSliders;
