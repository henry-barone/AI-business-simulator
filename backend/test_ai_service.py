#!/usr/bin/env python3
"""
Comprehensive test script for AI Service.
Tests pain point analysis, recommendation generation, and financial impact estimation.
"""

import sys
import os
import json
from typing import Dict, Any

# Add the backend directory to the path
sys.path.append(os.path.dirname(__file__))

from services.ai_service import AIService, PainPoint, Recommendation, FinancialImpact

class AIServiceTester:
    def __init__(self):
        self.ai_service = AIService()
        self.test_results = []
    
    def test_pain_point_analysis(self):
        """Test pain point analysis with manufacturing scenarios."""
        print("=== Testing Pain Point Analysis ===\n")
        
        # Test cases with different manufacturing pain points
        test_cases = [
            {
                'name': 'Quality Control Issues',
                'text': 'Our biggest challenges are inconsistent product quality due to manual inspection processes. We have frequent defects that require rework, and our quality control is slow and error-prone. This leads to customer complaints and delivery delays.',
                'context': {
                    'industry': 'Metal Manufacturing',
                    'employee_count': '11-50 employees',
                    'product_type': 'Metal Parts',
                    'automation_level': 'Some automated tools'
                }
            },
            {
                'name': 'Inventory Management Problems',
                'text': 'We struggle with tracking inventory in real-time. Our manual stock management leads to frequent stockouts and overstocking. We waste materials and have difficulty coordinating with suppliers.',
                'context': {
                    'industry': 'Electronics Manufacturing',
                    'employee_count': '51-200 employees',
                    'product_type': 'Electronics',
                    'automation_level': 'Partially automated'
                }
            },
            {
                'name': 'Production Efficiency Bottlenecks',
                'text': 'Our production line has significant bottlenecks during peak hours. Setup times are too long, and we have equipment downtime issues. Workers are often idle waiting for materials or machine availability.',
                'context': {
                    'industry': 'Plastic Manufacturing',
                    'employee_count': '11-50 employees',
                    'product_type': 'Plastic Components',
                    'automation_level': 'Fully manual operations'
                }
            },
            {
                'name': 'Multiple Manufacturing Issues',
                'text': 'We face several major challenges: quality inspection is manual and unreliable, our inventory tracking is done on spreadsheets, equipment maintenance is reactive causing unexpected downtime, and our labor costs are high due to inefficient processes. These issues significantly impact our profit margins.',
                'context': {
                    'industry': 'General Manufacturing',
                    'employee_count': '11-50 employees',
                    'product_type': 'Mixed Products',
                    'automation_level': 'Some automated tools'
                }
            }
        ]
        
        for test_case in test_cases:
            print(f"Test Case: {test_case['name']}")
            print(f"Text: {test_case['text'][:100]}...")
            
            # Analyze pain points
            pain_points = self.ai_service.analyze_pain_points(
                test_case['text'], 
                test_case['context']
            )
            
            print(f"Found {len(pain_points)} pain points:")
            for i, pp in enumerate(pain_points, 1):
                print(f"  {i}. {pp.category.replace('_', ' ').title()}: {pp.description}")
                print(f"     Severity: {pp.severity}, Frequency: {pp.frequency}")
                print(f"     Impact Areas: {', '.join(pp.impact_areas)}")
                print(f"     Confidence: {pp.confidence:.2f}")
            
            # Validate results
            assert len(pain_points) > 0, f"No pain points found for {test_case['name']}"
            assert all(pp.confidence > 0 for pp in pain_points), "All pain points should have positive confidence"
            
            print("✓ Pain point analysis successful\n")
        
        print("✓ All pain point analysis tests passed\n")
    
    def test_recommendation_generation(self):
        """Test recommendation generation with manufacturing company data."""
        print("=== Testing Recommendation Generation ===\n")
        
        # Mock company data scenarios
        test_companies = [
            {
                'name': 'Small Metal Parts Manufacturer',
                'data': {
                    'company_profile': {
                        'industry': 'Metal Manufacturing',
                        'product_type': 'Metal Parts',
                        'employee_count': '11-50 employees',
                        'production_volume': '500-5000 units/day',
                        'automation_level': 'Some automated tools'
                    },
                    'financial_data': {
                        'revenue': 750000,
                        'labor_costs': 250000,
                        'overhead_costs': 150000,
                        'cogs': 350000
                    },
                    'pain_points': [
                        PainPoint(
                            category='quality_control',
                            description='Manual inspection leading to inconsistent quality',
                            severity='high',
                            frequency='frequent',
                            impact_areas=['customer satisfaction', 'rework costs'],
                            confidence=0.9
                        ),
                        PainPoint(
                            category='inventory_management',
                            description='Real-time inventory tracking difficulties',
                            severity='medium',
                            frequency='frequent',
                            impact_areas=['stock levels', 'material waste'],
                            confidence=0.8
                        )
                    ]
                }
            },
            {
                'name': 'Medium Electronics Manufacturer',
                'data': {
                    'company_profile': {
                        'industry': 'Electronics Manufacturing',
                        'product_type': 'Electronics',
                        'employee_count': '51-200 employees',
                        'production_volume': '1000-10000 units/day',
                        'automation_level': 'Partially automated'
                    },
                    'financial_data': {
                        'revenue': 2500000,
                        'labor_costs': 800000,
                        'overhead_costs': 400000,
                        'cogs': 1200000
                    },
                    'pain_points': [
                        PainPoint(
                            category='production_efficiency',
                            description='Production bottlenecks during peak hours',
                            severity='high',
                            frequency='frequent',
                            impact_areas=['throughput', 'delivery times'],
                            confidence=0.85
                        ),
                        PainPoint(
                            category='maintenance',
                            description='Reactive maintenance causing unexpected downtime',
                            severity='medium',
                            frequency='occasional',
                            impact_areas=['equipment availability', 'production costs'],
                            confidence=0.75
                        )
                    ]
                }
            }
        ]
        
        for company in test_companies:
            print(f"Testing: {company['name']}")
            
            # Generate recommendations
            recommendations = self.ai_service.generate_recommendations(company['data'])
            
            print(f"Generated {len(recommendations)} recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec.title}")
                print(f"     Category: {rec.category}, Priority: {rec.priority}")
                print(f"     Effort: {rec.implementation_effort}, Timeline: {rec.estimated_timeline}")
                print(f"     Targets: {', '.join(rec.target_pain_points)}")
                print(f"     Confidence: {rec.confidence:.2f}")
                print(f"     Description: {rec.description[:100]}...")
            
            # Validate results
            assert len(recommendations) > 0, f"No recommendations generated for {company['name']}"
            assert all(rec.confidence > 0 for rec in recommendations), "All recommendations should have positive confidence"
            
            # Check that recommendations target identified pain points
            pain_point_categories = [pp.category for pp in company['data']['pain_points']]
            rec_targets = [target for rec in recommendations for target in rec.target_pain_points]
            assert any(target in pain_point_categories for target in rec_targets), "Recommendations should target identified pain points"
            
            print("✓ Recommendation generation successful\n")
        
        print("✓ All recommendation generation tests passed\n")
    
    def test_financial_impact_estimation(self):
        """Test financial impact estimation for recommendations."""
        print("=== Testing Financial Impact Estimation ===\n")
        
        # Test recommendations with company data
        test_scenarios = [
            {
                'name': 'Quality Management System - Small Company',
                'recommendation': Recommendation(
                    title="Digital Quality Management System",
                    description="Implement cloud-based QMS with real-time defect tracking and automated reporting",
                    category="quality",
                    priority="high",
                    implementation_effort="medium",
                    technology_type="software",
                    target_pain_points=["quality_control"],
                    estimated_timeline="3-6 months",
                    confidence=0.85
                ),
                'company_data': {
                    'financial_data': {
                        'revenue': 500000,
                        'labor_costs': 200000,
                        'overhead_costs': 100000
                    },
                    'company_profile': {
                        'employee_count': '11-50 employees',
                        'automation_level': 'Some automated tools'
                    }
                }
            },
            {
                'name': 'Inventory Optimization - Medium Company',
                'recommendation': Recommendation(
                    title="Automated Inventory Management System",
                    description="Deploy RFID-based inventory tracking with predictive analytics",
                    category="inventory",
                    priority="high",
                    implementation_effort="medium",
                    technology_type="software",
                    target_pain_points=["inventory_management"],
                    estimated_timeline="2-4 months",
                    confidence=0.8
                ),
                'company_data': {
                    'financial_data': {
                        'revenue': 1500000,
                        'labor_costs': 500000,
                        'overhead_costs': 250000
                    },
                    'company_profile': {
                        'employee_count': '51-200 employees',
                        'automation_level': 'Partially automated'
                    }
                }
            },
            {
                'name': 'Production Automation - Large Implementation',
                'recommendation': Recommendation(
                    title="Manufacturing Execution System (MES)",
                    description="Comprehensive MES implementation with real-time monitoring and scheduling",
                    category="automation",
                    priority="critical",
                    implementation_effort="high",
                    technology_type="software",
                    target_pain_points=["production_efficiency", "scheduling"],
                    estimated_timeline="6-12 months",
                    confidence=0.9
                ),
                'company_data': {
                    'financial_data': {
                        'revenue': 3000000,
                        'labor_costs': 1000000,
                        'overhead_costs': 500000
                    },
                    'company_profile': {
                        'employee_count': '51-200 employees',
                        'automation_level': 'Some automated tools'
                    }
                }
            }
        ]
        
        for scenario in test_scenarios:
            print(f"Testing: {scenario['name']}")
            print(f"Recommendation: {scenario['recommendation'].title}")
            
            # Estimate financial impact
            impact = self.ai_service.estimate_impact(
                scenario['recommendation'],
                scenario['company_data']
            )
            
            print(f"Financial Impact Analysis:")
            print(f"  Annual Savings: ${impact.cost_savings_annual:,.2f}")
            print(f"  Implementation Cost: ${impact.implementation_cost:,.2f}")
            print(f"  ROI: {impact.roi_percentage:.1f}%")
            print(f"  Payback Period: {impact.payback_months} months")
            print(f"  Revenue Impact: ${impact.revenue_impact:,.2f}")
            print(f"  Confidence: {impact.confidence:.2f}")
            
            print(f"  Cost Breakdown:")
            for category, cost in impact.cost_breakdown.items():
                print(f"    {category.replace('_', ' ').title()}: ${cost:,.2f}")
            
            print(f"  Key Assumptions:")
            for assumption in impact.assumptions:
                print(f"    - {assumption}")
            
            # Validate results
            assert impact.cost_savings_annual >= 0, "Savings should be non-negative"
            assert impact.implementation_cost > 0, "Implementation cost should be positive"
            assert impact.roi_percentage >= 0, "ROI should be non-negative"
            assert impact.payback_months > 0, "Payback period should be positive"
            assert 0 <= impact.confidence <= 1, "Confidence should be between 0 and 1"
            assert len(impact.assumptions) > 0, "Should have at least one assumption"
            
            print("✓ Financial impact estimation successful\n")
        
        print("✓ All financial impact estimation tests passed\n")
    
    def test_comprehensive_analysis(self):
        """Test comprehensive analysis combining all components."""
        print("=== Testing Comprehensive Analysis ===\n")
        
        # Mock questionnaire and financial data
        questionnaire_data = {
            'company_profile': {
                'industry': 'Metal Manufacturing',
                'product_type': 'Metal Parts',
                'employee_count': '11-50 employees',
                'production_volume': '500-5000 units/day',
                'automation_level': 'Some automated tools'
            },
            'responses': [
                {
                    'question_id': 'PAIN_POINTS',
                    'question_text': 'What are your biggest challenges?',
                    'answer': 'Our main challenges are quality control issues with manual inspection, inventory tracking problems, and production scheduling inefficiencies. These lead to customer complaints and increased costs.',
                    'answer_type': 'text'
                },
                {
                    'question_id': 'AUTOMATION_INTEREST',
                    'question_text': 'What would you like to automate?',
                    'answer': 'We want to automate quality inspection, inventory management, and production scheduling to reduce errors and improve efficiency.',
                    'answer_type': 'text'
                }
            ]
        }
        
        financial_data = {
            'revenue': 800000,
            'labor_costs': 300000,
            'overhead_costs': 150000,
            'cogs': 400000
        }
        
        print("Running comprehensive analysis...")
        
        # Run comprehensive analysis
        analysis = self.ai_service.analyze_comprehensive(questionnaire_data, financial_data)
        
        print("Analysis Results:")
        print(f"Timestamp: {analysis['analysis_timestamp']}")
        print(f"Pain Points Found: {len(analysis['pain_points'])}")
        print(f"Recommendations Generated: {len(analysis['recommendations'])}")
        
        print("\nPain Points:")
        for i, pp in enumerate(analysis['pain_points'], 1):
            print(f"  {i}. {pp['category'].replace('_', ' ').title()}: {pp['description']}")
            print(f"     Severity: {pp['severity']}, Confidence: {pp['confidence']:.2f}")
        
        print("\nTop Recommendations (by ROI):")
        for i, rec_impact in enumerate(analysis['recommendations'][:3], 1):
            rec = rec_impact['recommendation']
            impact = rec_impact['financial_impact']
            print(f"  {i}. {rec['title']}")
            print(f"     ROI: {impact['roi_percentage']:.1f}%, Savings: ${impact['cost_savings_annual']:,.0f}")
            print(f"     Implementation: ${impact['implementation_cost']:,.0f}, Payback: {impact['payback_months']} months")
        
        print(f"\nSummary:")
        summary = analysis['summary']
        print(f"  Total Pain Points: {summary['total_pain_points']}")
        print(f"  Total Recommendations: {summary['total_recommendations']}")
        print(f"  Best ROI: {summary['best_roi']:.1f}%")
        print(f"  Total Potential Savings: ${summary['total_potential_savings']:,.2f}")
        
        # Validate comprehensive analysis
        assert 'analysis_timestamp' in analysis, "Should include timestamp"
        assert 'pain_points' in analysis, "Should include pain points"
        assert 'recommendations' in analysis, "Should include recommendations"
        assert 'summary' in analysis, "Should include summary"
        assert len(analysis['pain_points']) > 0, "Should find pain points"
        assert len(analysis['recommendations']) > 0, "Should generate recommendations"
        assert analysis['summary']['total_pain_points'] > 0, "Summary should reflect pain points"
        assert analysis['summary']['total_recommendations'] > 0, "Summary should reflect recommendations"
        
        print("✓ Comprehensive analysis successful\n")
    
    def test_api_integration_status(self):
        """Test API integration status and capabilities."""
        print("=== Testing API Integration Status ===\n")
        
        print(f"OpenAI Client: {'✓ Available' if self.ai_service.openai_client else '✗ Not Available'}")
        print(f"Anthropic Client: {'✓ Available' if self.ai_service.anthropic_client else '✗ Not Available'}")
        
        if not self.ai_service.openai_client and not self.ai_service.anthropic_client:
            print("⚠️  Using fallback analysis methods")
            print("To enable AI API features:")
            print("  - Set OPENAI_API_KEY environment variable")
            print("  - Set ANTHROPIC_API_KEY environment variable")
            print("  - Install openai and anthropic packages")
        else:
            print("✓ AI API integration ready")
        
        print()
    
    def run_all_tests(self):
        """Run all AI service tests."""
        print("🤖 AI SERVICE COMPREHENSIVE TEST SUITE\n")
        print("="*60)
        
        try:
            self.test_api_integration_status()
            self.test_pain_point_analysis()
            self.test_recommendation_generation()
            self.test_financial_impact_estimation()
            self.test_comprehensive_analysis()
            
            print("="*60)
            print("🎉 ALL AI SERVICE TESTS PASSED!")
            print("\nAI Service Features:")
            print("✓ Pain point analysis with manufacturing focus")
            print("✓ AI-powered recommendation generation")
            print("✓ Financial impact estimation with ROI calculation")
            print("✓ Comprehensive analysis combining all components")
            print("✓ Fallback analysis when AI APIs unavailable")
            print("✓ Manufacturing-optimized prompts and templates")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Run the AI service test suite."""
    tester = AIServiceTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()