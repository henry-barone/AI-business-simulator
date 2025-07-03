#!/usr/bin/env python3
"""
Complete example demonstrating the AI Service integration.
Shows how to use AI analysis for manufacturing SME recommendations.
"""

import requests
import json
import time
from typing import Dict, Any

class AIServiceDemo:
    """Demonstrates AI service capabilities with real manufacturing scenarios."""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
    
    def demo_pain_point_analysis(self):
        """Demonstrate pain point analysis API."""
        print("=== AI Pain Point Analysis Demo ===\n")
        
        # Manufacturing pain point scenarios
        scenarios = [
            {
                'name': 'Quality Control Issues',
                'text_response': 'Our biggest challenges are quality control problems. We have manual inspection processes that are slow and inconsistent. Defects are found late in production, leading to expensive rework and customer complaints. Our quality team is overwhelmed and we need better tracking of defect patterns.',
                'context': {
                    'industry': 'Metal Manufacturing',
                    'employee_count': '11-50 employees',
                    'product_type': 'Metal Parts',
                    'automation_level': 'Some automated tools'
                }
            },
            {
                'name': 'Inventory and Production Challenges',
                'text_response': 'We struggle with inventory management and production scheduling. Our stock tracking is manual using spreadsheets, leading to stockouts and overstocking. Production bottlenecks occur frequently, especially during high-demand periods. Equipment downtime is unpredictable and affects our delivery commitments.',
                'context': {
                    'industry': 'Electronics Manufacturing',
                    'employee_count': '51-200 employees',
                    'product_type': 'Electronics',
                    'automation_level': 'Partially automated'
                }
            }
        ]
        
        for scenario in scenarios:
            print(f"Scenario: {scenario['name']}")
            
            # Call pain point analysis API
            response = requests.post(
                f"{self.base_url}/api/ai/analyze-pain-points",
                json={
                    'text_response': scenario['text_response'],
                    'context': scenario['context']
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                pain_points = result['pain_points']
                
                print(f"Found {len(pain_points)} pain points:")
                for i, pp in enumerate(pain_points, 1):
                    print(f"  {i}. {pp['category'].replace('_', ' ').title()}")
                    print(f"     Description: {pp['description']}")
                    print(f"     Severity: {pp['severity']}, Frequency: {pp['frequency']}")
                    print(f"     Impact Areas: {', '.join(pp['impact_areas'])}")
                    print(f"     Confidence: {pp['confidence']:.2f}")
                
                print("✓ Pain point analysis successful\n")
            else:
                print(f"❌ API call failed: {response.status_code}")
                print(f"Error: {response.text}\n")
    
    def demo_recommendation_generation(self):
        """Demonstrate AI recommendation generation."""
        print("=== AI Recommendation Generation Demo ===\n")
        
        # Mock company data with pain points
        company_data = {
            'company_profile': {
                'industry': 'Metal Manufacturing',
                'product_type': 'Metal Parts',
                'employee_count': '11-50 employees',
                'production_volume': '500-5000 units/day',
                'automation_level': 'Some automated tools'
            },
            'financial_data': {
                'revenue': 800000,
                'labor_costs': 300000,
                'overhead_costs': 150000,
                'cogs': 400000
            },
            'pain_points': [
                {
                    'category': 'quality_control',
                    'description': 'Manual inspection leading to inconsistent quality',
                    'severity': 'high',
                    'frequency': 'frequent',
                    'impact_areas': ['customer satisfaction', 'rework costs'],
                    'confidence': 0.9
                },
                {
                    'category': 'inventory_management',
                    'description': 'Real-time inventory tracking difficulties',
                    'severity': 'medium',
                    'frequency': 'frequent',
                    'impact_areas': ['stock levels', 'material waste'],
                    'confidence': 0.8
                },
                {
                    'category': 'production_efficiency',
                    'description': 'Production bottlenecks during peak hours',
                    'severity': 'medium',
                    'frequency': 'occasional',
                    'impact_areas': ['throughput', 'delivery times'],
                    'confidence': 0.7
                }
            ]
        }
        
        print("Company Profile:")
        print(f"  Industry: {company_data['company_profile']['industry']}")
        print(f"  Size: {company_data['company_profile']['employee_count']}")
        print(f"  Revenue: ${company_data['financial_data']['revenue']:,}")
        print(f"  Pain Points: {len(company_data['pain_points'])}")
        
        # Call recommendation generation API
        response = requests.post(
            f"{self.base_url}/api/ai/generate-recommendations",
            json={'company_data': company_data}
        )
        
        if response.status_code == 200:
            result = response.json()
            recommendations = result['recommendations']
            
            print(f"\nGenerated {len(recommendations)} recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"\n  {i}. {rec['title']}")
                print(f"     Category: {rec['category']}, Priority: {rec['priority']}")
                print(f"     Implementation Effort: {rec['implementation_effort']}")
                print(f"     Technology Type: {rec['technology_type']}")
                print(f"     Timeline: {rec['estimated_timeline']}")
                print(f"     Targets: {', '.join(rec['target_pain_points'])}")
                print(f"     Confidence: {rec['confidence']:.2f}")
                print(f"     Description: {rec['description'][:150]}...")
            
            print("\n✓ Recommendation generation successful\n")
            return recommendations
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"Error: {response.text}\n")
            return []
    
    def demo_financial_impact_estimation(self, recommendations):
        """Demonstrate financial impact estimation."""
        print("=== Financial Impact Estimation Demo ===\n")
        
        if not recommendations:
            print("No recommendations available for impact analysis\n")
            return
        
        company_data = {
            'financial_data': {
                'revenue': 800000,
                'labor_costs': 300000,
                'overhead_costs': 150000
            },
            'company_profile': {
                'employee_count': '11-50 employees',
                'automation_level': 'Some automated tools'
            }
        }
        
        # Analyze impact for each recommendation
        for i, rec in enumerate(recommendations[:3], 1):  # Top 3 recommendations
            print(f"Impact Analysis {i}: {rec['title']}")
            
            response = requests.post(
                f"{self.base_url}/api/ai/estimate-impact",
                json={
                    'recommendation': rec,
                    'company_data': company_data
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                impact = result['financial_impact']
                
                print(f"  Annual Savings: ${impact['cost_savings_annual']:,.2f}")
                print(f"  Implementation Cost: ${impact['implementation_cost']:,.2f}")
                print(f"  ROI: {impact['roi_percentage']:.1f}%")
                print(f"  Payback Period: {impact['payback_months']} months")
                print(f"  Revenue Impact: ${impact['revenue_impact']:,.2f}")
                print(f"  Confidence: {impact['confidence']:.2f}")
                
                print(f"  Cost Breakdown:")
                for category, cost in impact['cost_breakdown'].items():
                    print(f"    {category.replace('_', ' ').title()}: ${cost:,.2f}")
                
                print(f"  Key Assumptions:")
                for assumption in impact['assumptions'][:2]:  # First 2 assumptions
                    print(f"    - {assumption}")
                
                print()
            else:
                print(f"❌ Impact analysis failed: {response.status_code}\n")
        
        print("✓ Financial impact estimation completed\n")
    
    def demo_comprehensive_analysis(self):
        """Demonstrate comprehensive analysis with mock session."""
        print("=== Comprehensive Analysis Demo ===\n")
        
        # This would typically use a real questionnaire session
        # For demo, we'll create mock data
        comprehensive_data = {
            'session_id': 'demo-session-123',
            'financial_data': {
                'revenue': 1200000,
                'labor_costs': 400000,
                'overhead_costs': 200000,
                'cogs': 600000
            }
        }
        
        print("Running comprehensive analysis...")
        print(f"Mock Session ID: {comprehensive_data['session_id']}")
        print(f"Financial Data: Revenue ${comprehensive_data['financial_data']['revenue']:,}")
        
        # Note: This would fail in demo since session doesn't exist
        # But shows the API structure
        print("⚠️  This demo shows API structure - requires real questionnaire session")
        print("   Use questionnaire completion flow to generate real analysis\n")
    
    def demo_ai_capabilities(self):
        """Show AI service capabilities."""
        print("=== AI Service Capabilities ===\n")
        
        response = requests.get(f"{self.base_url}/api/ai/capabilities")
        
        if response.status_code == 200:
            result = response.json()
            capabilities = result['capabilities']
            
            print("API Integration Status:")
            print(f"  OpenAI: {'✓ Available' if capabilities['openai_available'] else '✗ Not Available'}")
            print(f"  Anthropic: {'✓ Available' if capabilities['anthropic_available'] else '✗ Not Available'}")
            print(f"  Fallback Analysis: {'✓ Available' if capabilities['fallback_analysis'] else '✗ Not Available'}")
            
            print("\nFeatures:")
            for feature, available in capabilities['features'].items():
                status = '✓' if available else '✗'
                print(f"  {status} {feature.replace('_', ' ').title()}")
            
            print(f"\nManufacturing Categories:")
            for category in capabilities['manufacturing_categories']:
                print(f"  • {category.replace('_', ' ').title()}")
            
            print(f"\nSupported File Formats:")
            for fmt in capabilities['supported_file_formats']:
                print(f"  • {fmt}")
            
            print("\n✓ Capabilities retrieved successfully\n")
        else:
            print(f"❌ Failed to get capabilities: {response.status_code}\n")
    
    def run_complete_demo(self):
        """Run the complete AI service demonstration."""
        print("🤖 AI SERVICE COMPLETE DEMONSTRATION\n")
        print("="*60)
        
        try:
            # Check if server is running
            response = requests.get(f"{self.base_url}/api/ai/capabilities")
            if response.status_code != 200:
                print("❌ Flask server is not running or AI endpoints not available!")
                print("Start the server and ensure AI routes are registered")
                return
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server!")
            print("Start the Flask server with: python app.py")
            return
        
        print("✅ Server is running with AI endpoints\n")
        
        # Run all demos
        self.demo_ai_capabilities()
        self.demo_pain_point_analysis()
        recommendations = self.demo_recommendation_generation()
        self.demo_financial_impact_estimation(recommendations)
        self.demo_comprehensive_analysis()
        
        print("="*60)
        print("🎉 AI SERVICE DEMO COMPLETED!")
        print("\nNext Steps:")
        print("1. Complete a questionnaire session")
        print("2. Upload P&L financial data")
        print("3. Run comprehensive analysis")
        print("4. Get AI-powered recommendations with ROI estimates")

def main():
    """Run the AI service demonstration."""
    demo = AIServiceDemo()
    demo.run_complete_demo()

if __name__ == "__main__":
    main()