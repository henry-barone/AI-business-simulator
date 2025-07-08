#!/usr/bin/env python3
"""
Test script for Enhanced Manufacturing Simulation Engine

Tests all manufacturing-specific calculations including:
- Labor optimization
- Quality control savings  
- Inventory optimization
- Customer service automation
- Monthly cash flow projections
- Break-even analysis
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.enhanced_simulation_engine import (
    EnhancedSimulationEngine, 
    EnhancedBaselineModel,
    ManufacturingMetrics,
    CostBreakdown
)
import json

def test_enhanced_simulation_engine():
    """Test the enhanced simulation engine with sample manufacturing data."""
    
    print("🏭 Testing Enhanced Manufacturing Simulation Engine")
    print("=" * 60)
    
    # Create engine instance
    engine = EnhancedSimulationEngine()
    
    # Sample company data (manufacturing company)
    company_data = {
        'financial_data': {
            'revenue': 5000000,  # $5M annual revenue
            'cogs': 3000000,     # $3M COGS
            'labor_costs': 1200000,  # $1.2M labor
            'overhead_costs': 500000  # $500k overhead
        },
        'company_profile': {
            'production_volume': '1000-10000 units/day',
            'employee_count': '51-200',
            'automation_level': 'Some automated tools',
            'industry': 'Manufacturing'
        }
    }
    
    print("\n📊 Creating Enhanced Baseline Model...")
    baseline = engine.create_enhanced_baseline(company_data)
    
    print(f"Revenue: ${baseline.revenue:,.2f}")
    print(f"COGS: ${baseline.cogs:,.2f}")
    print(f"Labor Costs: ${baseline.labor_costs:,.2f}")
    print(f"Overhead Costs: ${baseline.overhead_costs:,.2f}")
    print(f"Production Volume: {baseline.production_volume:,} units/year")
    print(f"Employee Count: {baseline.employee_count}")
    print(f"Automation Level: {baseline.automation_level}")
    
    print(f"\n💰 Detailed Cost Breakdown:")
    print(f"Direct Labor: ${baseline.cost_breakdown.direct_labor_cost:,.2f}")
    print(f"Indirect Labor: ${baseline.cost_breakdown.indirect_labor_cost:,.2f}")
    print(f"Rework Cost: ${baseline.cost_breakdown.rework_cost:,.2f}")
    print(f"Scrap Cost: ${baseline.cost_breakdown.scrap_cost:,.2f}")
    print(f"Carrying Cost: ${baseline.cost_breakdown.carrying_cost:,.2f}")
    print(f"Agent Salaries: ${baseline.cost_breakdown.agent_salaries:,.2f}")
    print(f"Total Operational Costs: ${baseline.cost_breakdown.total_costs():,.2f}")
    
    # Test labor optimization
    print("\n🔧 Testing Labor Optimization (50% automation)...")
    labor_results = engine.calculate_labor_optimization(baseline, 0.5)
    
    print(f"Direct Labor Savings: ${labor_results['direct_labor_savings']:,.2f}")
    print(f"Indirect Labor Savings: ${labor_results['indirect_labor_savings']:,.2f}")
    print(f"Overtime Savings: ${labor_results['overtime_savings']:,.2f}")
    print(f"Total Annual Savings: ${labor_results['total_annual_savings']:,.2f}")
    print(f"Implementation Cost: ${labor_results['implementation_cost']:,.2f}")
    print(f"Training Cost: ${labor_results['training_cost']:,.2f}")
    print(f"Net Savings Year 1: ${labor_results['net_savings_year_1']:,.2f}")
    print(f"Payback Period: {labor_results['payback_months']:.1f} months")
    print(f"ROI: {labor_results['roi_percentage']:.1f}%")
    
    # Test quality optimization
    print("\n🎯 Testing Quality Optimization (60% automation)...")
    quality_results = engine.calculate_quality_optimization(baseline, 0.6)
    
    print(f"Rework Savings: ${quality_results['rework_savings']:,.2f}")
    print(f"Scrap Savings: ${quality_results['scrap_savings']:,.2f}")
    print(f"Inspection Savings: ${quality_results['inspection_savings']:,.2f}")
    print(f"Warranty Savings: ${quality_results['warranty_savings']:,.2f}")
    print(f"Total Annual Savings: ${quality_results['total_annual_savings']:,.2f}")
    print(f"Quality System Cost: ${quality_results['quality_system_cost']:,.2f}")
    print(f"Net Savings Year 1: ${quality_results['net_savings_year_1']:,.2f}")
    print(f"Payback Period: {quality_results['payback_months']:.1f} months")
    print(f"ROI: {quality_results['roi_percentage']:.1f}%")
    
    # Test inventory optimization
    print("\n📦 Testing Inventory Optimization (40% automation)...")
    inventory_results = engine.calculate_inventory_optimization(baseline, 0.4)
    
    print(f"Carrying Cost Savings: ${inventory_results['carrying_cost_savings']:,.2f}")
    print(f"Storage Savings: ${inventory_results['storage_savings']:,.2f}")
    print(f"Obsolescence Savings: ${inventory_results['obsolescence_savings']:,.2f}")
    print(f"Working Capital Benefit: ${inventory_results['working_capital_benefit']:,.2f}")
    print(f"Working Capital Freed: ${inventory_results['working_capital_freed']:,.2f}")
    print(f"Total Annual Savings: ${inventory_results['total_annual_savings']:,.2f}")
    print(f"System Cost: ${inventory_results['system_cost']:,.2f}")
    print(f"Net Savings Year 1: ${inventory_results['net_savings_year_1']:,.2f}")
    print(f"Payback Period: {inventory_results['payback_months']:.1f} months")
    print(f"ROI: {inventory_results['roi_percentage']:.1f}%")
    
    # Test service automation
    print("\n📞 Testing Customer Service Automation (30% automation)...")
    service_results = engine.calculate_service_automation(baseline, 0.3)
    
    print(f"Agent Cost Savings: ${service_results['agent_cost_savings']:,.2f}")
    print(f"Productivity Savings: ${service_results['productivity_savings']:,.2f}")
    print(f"System Efficiency Savings: ${service_results['system_efficiency_savings']:,.2f}")
    print(f"Total Annual Savings: ${service_results['total_annual_savings']:,.2f}")
    print(f"Platform Cost: ${service_results['automation_platform_cost']:,.2f}")
    print(f"Net Savings Year 1: ${service_results['net_savings_year_1']:,.2f}")
    print(f"Payback Period: {service_results['payback_months']:.1f} months")
    print(f"ROI: {service_results['roi_percentage']:.1f}%")
    
    # Test monthly projections
    print("\n📈 Testing Monthly Cash Flow Projections (24 months)...")
    automation_levels = {
        'labor': 0.5,
        'quality': 0.6,
        'inventory': 0.4,
        'service': 0.3
    }
    
    projections = engine.generate_monthly_projections(baseline, automation_levels, 24)
    
    print(f"Generated {len(projections)} monthly projections")
    
    # Show key months
    key_months = [1, 6, 12, 18, 24]
    for month_num in key_months:
        if month_num <= len(projections):
            p = projections[month_num - 1]
            print(f"\nMonth {p.month}:")
            print(f"  Monthly Savings: ${p.total_savings:,.2f}")
            print(f"  Implementation Costs: ${p.implementation_costs:,.2f}")
            print(f"  Monthly Cash Flow: ${p.monthly_cash_flow:,.2f}")
            print(f"  Cumulative Cash Flow: ${p.cumulative_cash_flow:,.2f}")
            print(f"  ROI to Date: {p.roi_to_date:.1f}%")
            print(f"  Payback Achieved: {p.payback_achieved}")
    
    # Test break-even analysis
    print("\n⚖️  Testing Break-Even Analysis...")
    break_even = engine.analyze_break_even(projections)
    
    print(f"Break-Even Month: {break_even['break_even_month']}")
    print(f"Total Investment: ${break_even['total_investment']:,.2f}")
    print(f"Total Savings: ${break_even['total_savings']:,.2f}")
    print(f"Net Benefit: ${break_even['net_benefit']:,.2f}")
    print(f"Final ROI: {break_even['final_roi_percentage']:.1f}%")
    print(f"Payback Achieved: {break_even['payback_achieved']}")
    print(f"Final Cumulative Cash Flow: ${break_even['cumulative_cash_flow_final']:,.2f}")
    print(f"Average Monthly Savings: ${break_even['average_monthly_savings']:,.2f}")
    print(f"Investment Recovery Timeline: {break_even['investment_recovery_timeline']}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 SIMULATION SUMMARY")
    print("=" * 60)
    
    total_annual_savings = (
        labor_results['total_annual_savings'] +
        quality_results['total_annual_savings'] +
        inventory_results['total_annual_savings'] +
        service_results['total_annual_savings']
    )
    
    total_implementation = (
        labor_results['implementation_cost'] + labor_results['training_cost'] +
        quality_results['quality_system_cost'] + quality_results['training_cost'] +
        inventory_results['system_cost'] + inventory_results['training_cost'] +
        service_results['automation_platform_cost'] + service_results['setup_cost']
    )
    
    print(f"Total Annual Savings: ${total_annual_savings:,.2f}")
    print(f"Total Implementation Cost: ${total_implementation:,.2f}")
    print(f"Net Benefit Year 1: ${total_annual_savings - total_implementation:,.2f}")
    print(f"Overall ROI Year 1: {((total_annual_savings - total_implementation) / total_implementation * 100):.1f}%")
    print(f"Monthly Savings Potential: ${total_annual_savings / 12:,.2f}")
    
    print("\n✅ Enhanced Simulation Engine Test Completed Successfully!")
    
    return {
        'baseline': baseline,
        'labor_optimization': labor_results,
        'quality_optimization': quality_results,
        'inventory_optimization': inventory_results,
        'service_automation': service_results,
        'monthly_projections': projections,
        'break_even_analysis': break_even,
        'summary': {
            'total_annual_savings': total_annual_savings,
            'total_implementation_cost': total_implementation,
            'net_benefit_year_1': total_annual_savings - total_implementation,
            'overall_roi_year_1': ((total_annual_savings - total_implementation) / total_implementation * 100) if total_implementation > 0 else 0
        }
    }

if __name__ == "__main__":
    try:
        results = test_enhanced_simulation_engine()
        print(f"\n🎯 Test completed successfully!")
        print(f"Results saved for integration with existing simulation routes.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()