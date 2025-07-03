#!/usr/bin/env python3
"""
Manufacturing Digital Twin Simulation Engine

Integrates with existing PLAnalyzer, Questionnaire System, and AIService
to create comprehensive manufacturing business simulations with optimization projections.
"""

import logging
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

from services.pl_analyzer import PLAnalyzer
from services.ai_service import AIService, Recommendation, FinancialImpact

logger = logging.getLogger(__name__)

@dataclass
class BaselineModel:
    """Current state financial model of the manufacturing company."""
    # Financial metrics (annual)
    revenue: float
    cogs: float
    labor_costs: float
    overhead_costs: float
    
    # Operational metrics
    production_volume: int  # units per year
    employee_count: int
    automation_level: str
    
    # Efficiency metrics
    quality_defect_rate: float  # percentage
    labor_efficiency: float  # percentage
    inventory_turnover: float  # times per year
    equipment_uptime: float  # percentage
    
    # Monthly breakdown (calculated automatically)
    monthly_revenue: float = 0
    monthly_costs: float = 0
    monthly_profit: float = 0
    
    def __post_init__(self):
        """Calculate monthly metrics from annual figures."""
        self.monthly_revenue = self.revenue / 12
        self.monthly_costs = (self.cogs + self.labor_costs + self.overhead_costs) / 12
        self.monthly_profit = self.monthly_revenue - self.monthly_costs

@dataclass
class OptimizationScenario:
    """Represents an optimization scenario with applied recommendations."""
    name: str
    baseline: BaselineModel
    applied_recommendations: List[Recommendation]
    implementation_costs: Dict[str, float]
    
    # Optimized metrics
    optimized_labor_efficiency: float
    optimized_quality_rate: float
    optimized_inventory_turnover: float
    optimized_equipment_uptime: float
    
    # Timeline and ramp-up
    implementation_months: int
    ramp_up_months: int
    
    def calculate_monthly_savings(self, month: int) -> Dict[str, float]:
        """Calculate cost savings for a specific month during implementation."""
        if month <= self.implementation_months:
            # During implementation, apply gradual ramp-up
            ramp_factor = min(month / self.implementation_months, 1.0)
        else:
            # Full benefits after implementation
            ramp_factor = 1.0
        
        # Calculate savings by category
        labor_savings = (self.baseline.labor_costs / 12) * (self.optimized_labor_efficiency - 1.0) * ramp_factor
        quality_savings = (self.baseline.cogs / 12) * (1.0 - self.optimized_quality_rate) * ramp_factor
        inventory_savings = (self.baseline.overhead_costs / 12) * 0.1 * (self.optimized_inventory_turnover - 1.0) * ramp_factor
        
        return {
            'labor_savings': abs(labor_savings),
            'quality_savings': abs(quality_savings),
            'inventory_savings': abs(inventory_savings),
            'total_savings': abs(labor_savings + quality_savings + inventory_savings)
        }

@dataclass
class ProjectionPeriod:
    """Financial projections for a specific time period."""
    period_name: str  # "30 days", "90 days", etc.
    months: int
    
    # Cumulative metrics
    cumulative_savings: float
    cumulative_costs: float
    net_benefit: float
    
    # Cash flow
    monthly_cash_flow: List[float]
    cumulative_cash_flow: List[float]
    
    # ROI metrics
    roi_percentage: float
    payback_achieved: bool
    break_even_month: Optional[int]

class SimulationEngine:
    """
    Manufacturing Digital Twin Simulation Engine.
    
    Integrates with existing services to create comprehensive business simulations
    with automation optimization projections and financial impact analysis.
    """
    
    def __init__(self):
        self.pl_analyzer = PLAnalyzer()
        self.ai_service = AIService()
        
        # Default efficiency assumptions for manufacturing
        self.default_efficiency_metrics = {
            'quality_defect_rate': 0.05,  # 5% defect rate
            'labor_efficiency': 1.0,  # 100% baseline
            'inventory_turnover': 4.0,  # 4x per year
            'equipment_uptime': 0.85  # 85% uptime
        }
        
        # Optimization impact factors
        self.optimization_factors = {
            'labor_automation': {
                'labor_efficiency_gain': 0.15,  # 15% improvement
                'implementation_months': 3,
                'ramp_up_months': 2
            },
            'quality_automation': {
                'defect_reduction': 0.60,  # 60% reduction in defects
                'implementation_months': 4,
                'ramp_up_months': 3
            },
            'inventory_automation': {
                'turnover_improvement': 0.25,  # 25% improvement
                'implementation_months': 2,
                'ramp_up_months': 1
            }
        }
    
    def create_baseline(self, company_data: Dict[str, Any]) -> BaselineModel:
        """
        Create baseline financial model from P&L data and questionnaire responses.
        
        Args:
            company_data: Combined data from PLAnalyzer and questionnaire
            
        Returns:
            BaselineModel representing current state
        """
        try:
            # Extract financial data (from PLAnalyzer)
            financial_data = company_data.get('financial_data', {})
            revenue = financial_data.get('revenue', 0)
            cogs = financial_data.get('cogs', 0)
            labor_costs = financial_data.get('labor_costs', 0)
            overhead_costs = financial_data.get('overhead_costs', 0)
            
            # Extract operational data (from questionnaire)
            company_profile = company_data.get('company_profile', {})
            
            # Parse production volume
            volume_str = company_profile.get('production_volume', '1000-10000 units/day')
            production_volume = self._parse_production_volume(volume_str)
            
            # Parse employee count
            employee_str = company_profile.get('employee_count', '11-50 employees')
            employee_count = self._parse_employee_count(employee_str)
            
            automation_level = company_profile.get('automation_level', 'Some automated tools')
            
            # Estimate efficiency metrics based on questionnaire responses
            efficiency_metrics = self._estimate_efficiency_metrics(company_data)
            
            baseline = BaselineModel(
                revenue=revenue,
                cogs=cogs,
                labor_costs=labor_costs,
                overhead_costs=overhead_costs,
                production_volume=production_volume,
                employee_count=employee_count,
                automation_level=automation_level,
                quality_defect_rate=efficiency_metrics['quality_defect_rate'],
                labor_efficiency=efficiency_metrics['labor_efficiency'],
                inventory_turnover=efficiency_metrics['inventory_turnover'],
                equipment_uptime=efficiency_metrics['equipment_uptime']
            )
            
            logger.info(f"Created baseline model: Revenue ${revenue:,.2f}, Employees {employee_count}")
            return baseline
            
        except Exception as e:
            logger.error(f"Failed to create baseline model: {e}")
            raise ValueError(f"Baseline creation failed: {e}")
    
    def apply_optimizations(self, baseline: BaselineModel, recommendations: List[Recommendation]) -> List[OptimizationScenario]:
        """
        Apply AI recommendations to baseline model to create optimization scenarios.
        
        Args:
            baseline: Current state model
            recommendations: AI-generated recommendations
            
        Returns:
            List of optimization scenarios with projected improvements
        """
        try:
            scenarios = []
            
            for i, recommendation in enumerate(recommendations):
                # Calculate optimization factors based on recommendation category
                opt_factors = self._get_optimization_factors(recommendation)
                
                # Apply improvements to baseline metrics
                optimized_metrics = self._apply_recommendation_improvements(baseline, recommendation, opt_factors)
                
                # Estimate implementation costs
                impl_costs = self._estimate_implementation_costs(recommendation, baseline)
                
                scenario = OptimizationScenario(
                    name=recommendation.title,
                    baseline=baseline,
                    applied_recommendations=[recommendation],
                    implementation_costs=impl_costs,
                    optimized_labor_efficiency=optimized_metrics['labor_efficiency'],
                    optimized_quality_rate=optimized_metrics['quality_rate'],
                    optimized_inventory_turnover=optimized_metrics['inventory_turnover'],
                    optimized_equipment_uptime=optimized_metrics['equipment_uptime'],
                    implementation_months=opt_factors['implementation_months'],
                    ramp_up_months=opt_factors['ramp_up_months']
                )
                
                scenarios.append(scenario)
                logger.info(f"Created optimization scenario: {scenario.name}")
            
            return scenarios
            
        except Exception as e:
            logger.error(f"Failed to apply optimizations: {e}")
            raise ValueError(f"Optimization application failed: {e}")
    
    def project_timeline(self, optimized_model: OptimizationScenario, months: int = 12) -> Dict[str, ProjectionPeriod]:
        """
        Generate financial projections for multiple time periods.
        
        Args:
            optimized_model: Optimization scenario to project
            months: Maximum projection period in months
            
        Returns:
            Dictionary of projections for different time periods
        """
        try:
            projections = {}
            
            # Define projection periods
            periods = [
                ('30_days', 1),
                ('60_days', 2),
                ('90_days', 3),
                ('180_days', 6),
                ('365_days', 12)
            ]
            
            for period_name, period_months in periods:
                if period_months <= months:
                    projection = self._calculate_period_projection(optimized_model, period_months)
                    projections[period_name] = projection
            
            logger.info(f"Generated projections for {len(projections)} periods")
            return projections
            
        except Exception as e:
            logger.error(f"Failed to project timeline: {e}")
            raise ValueError(f"Timeline projection failed: {e}")
    
    def calculate_roi(self, baseline: BaselineModel, optimized: OptimizationScenario, timeframe_months: int = 12) -> Dict[str, Any]:
        """
        Calculate comprehensive ROI metrics for the optimization.
        
        Args:
            baseline: Current state model
            optimized: Optimized scenario
            timeframe_months: Analysis timeframe in months
            
        Returns:
            Dictionary with ROI metrics including payback, NPV, IRR
        """
        try:
            # Calculate total implementation costs
            total_impl_cost = sum(optimized.implementation_costs.values())
            
            # Calculate monthly savings over timeframe
            monthly_savings = []
            cumulative_savings = 0
            
            for month in range(1, timeframe_months + 1):
                month_savings = optimized.calculate_monthly_savings(month)
                monthly_savings.append(month_savings['total_savings'])
                cumulative_savings += month_savings['total_savings']
            
            # Calculate payback period
            payback_months = self._calculate_payback_period(total_impl_cost, monthly_savings)
            
            # Calculate ROI percentage
            roi_percentage = ((cumulative_savings - total_impl_cost) / total_impl_cost) * 100 if total_impl_cost > 0 else 0
            
            # Calculate NPV (assuming 8% discount rate)
            discount_rate = 0.08 / 12  # Monthly discount rate
            npv = self._calculate_npv(total_impl_cost, monthly_savings, discount_rate)
            
            # Calculate break-even timeline
            break_even_month = self._calculate_break_even(total_impl_cost, monthly_savings)
            
            # Calculate cash flow impact
            cash_flow = self._calculate_cash_flow_impact(baseline, optimized, timeframe_months)
            
            roi_metrics = {
                'payback_months': payback_months,
                'roi_percentage': roi_percentage,
                'npv': npv,
                'break_even_month': break_even_month,
                'total_implementation_cost': total_impl_cost,
                'total_savings': cumulative_savings,
                'net_benefit': cumulative_savings - total_impl_cost,
                'monthly_savings': monthly_savings,
                'cash_flow_impact': cash_flow,
                'roi_valid': payback_months is not None and payback_months <= timeframe_months
            }
            
            logger.info(f"ROI calculated: {roi_percentage:.1f}%, Payback: {payback_months} months")
            return roi_metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate ROI: {e}")
            raise ValueError(f"ROI calculation failed: {e}")
    
    def adjust_real_time(self, baseline: BaselineModel, adjustments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle real-time slider adjustments without database calls.
        
        Args:
            baseline: Current baseline model
            adjustments: Real-time adjustment parameters
            
        Returns:
            Lightweight recalculated projections
        """
        try:
            # Extract adjustment parameters
            labor_automation = adjustments.get('labor_automation', 0) / 100  # Convert to decimal
            quality_automation = adjustments.get('quality_automation', 0) / 100
            inventory_automation = adjustments.get('inventory_automation', 0) / 100
            timeline_months = adjustments.get('timeline_months', 6)
            
            # Calculate adjusted efficiency improvements
            labor_improvement = 1.0 + (labor_automation * 0.20)  # Up to 20% improvement
            quality_improvement = 1.0 - (quality_automation * 0.50)  # Up to 50% defect reduction
            inventory_improvement = 1.0 + (inventory_automation * 0.30)  # Up to 30% improvement
            
            # Calculate monthly savings
            monthly_labor_savings = (baseline.labor_costs / 12) * (labor_improvement - 1.0)
            monthly_quality_savings = (baseline.cogs / 12) * (1.0 - quality_improvement) * 0.1  # 10% of COGS affected
            monthly_inventory_savings = (baseline.overhead_costs / 12) * (inventory_improvement - 1.0) * 0.15  # 15% of overhead affected
            
            total_monthly_savings = monthly_labor_savings + monthly_quality_savings + monthly_inventory_savings
            
            # Estimate implementation cost based on automation levels
            impl_cost = baseline.revenue * 0.05 * (labor_automation + quality_automation + inventory_automation)
            
            # Generate quick projections
            projections = []
            cumulative_savings = 0
            cumulative_cost = impl_cost
            
            for month in range(1, timeline_months + 1):
                # Apply ramp-up factor
                ramp_factor = min(month / 3, 1.0)  # 3-month ramp-up
                month_savings = total_monthly_savings * ramp_factor
                cumulative_savings += month_savings
                
                net_benefit = cumulative_savings - cumulative_cost
                
                projections.append({
                    'month': month,
                    'monthly_savings': month_savings,
                    'cumulative_savings': cumulative_savings,
                    'net_benefit': net_benefit,
                    'roi_percentage': (net_benefit / impl_cost * 100) if impl_cost > 0 else 0
                })
            
            # Calculate summary metrics
            payback_months = impl_cost / total_monthly_savings if total_monthly_savings > 0 else None
            final_roi = (cumulative_savings - impl_cost) / impl_cost * 100 if impl_cost > 0 else 0
            
            return {
                'success': True,
                'projections': projections,
                'summary': {
                    'total_implementation_cost': impl_cost,
                    'monthly_savings': total_monthly_savings,
                    'payback_months': payback_months,
                    'final_roi_percentage': final_roi,
                    'total_savings': cumulative_savings,
                    'net_benefit': cumulative_savings - impl_cost
                },
                'breakdown': {
                    'labor_savings': monthly_labor_savings,
                    'quality_savings': monthly_quality_savings,
                    'inventory_savings': monthly_inventory_savings
                }
            }
            
        except Exception as e:
            logger.error(f"Real-time adjustment failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # Helper methods
    
    def _parse_production_volume(self, volume_str: str) -> int:
        """Parse production volume from questionnaire response."""
        if 'day' in volume_str.lower():
            # Extract number and convert to annual
            if '< 100' in volume_str:
                return 50 * 250  # 50 units/day * 250 working days
            elif '100-1000' in volume_str:
                return 500 * 250
            elif '1000-10000' in volume_str:
                return 5000 * 250
            elif '> 10000' in volume_str:
                return 15000 * 250
        return 500000  # Default annual volume
    
    def _parse_employee_count(self, employee_str: str) -> int:
        """Parse employee count from questionnaire response."""
        if '1-10' in employee_str:
            return 5
        elif '11-50' in employee_str:
            return 25
        elif '51-200' in employee_str:
            return 100
        elif '200+' in employee_str:
            return 300
        return 25  # Default
    
    def _estimate_efficiency_metrics(self, company_data: Dict[str, Any]) -> Dict[str, float]:
        """Estimate efficiency metrics based on questionnaire responses."""
        metrics = self.default_efficiency_metrics.copy()
        
        # Adjust based on automation level
        automation_level = company_data.get('company_profile', {}).get('automation_level', '')
        
        if 'fully manual' in automation_level.lower():
            metrics['labor_efficiency'] = 0.85
            metrics['quality_defect_rate'] = 0.08
            metrics['equipment_uptime'] = 0.80
        elif 'highly automated' in automation_level.lower():
            metrics['labor_efficiency'] = 1.15
            metrics['quality_defect_rate'] = 0.02
            metrics['equipment_uptime'] = 0.92
        
        return metrics
    
    def _get_optimization_factors(self, recommendation: Recommendation) -> Dict[str, Any]:
        """Get optimization factors based on recommendation category."""
        category = recommendation.category.lower()
        
        if 'quality' in category:
            return self.optimization_factors['quality_automation']
        elif 'inventory' in category:
            return self.optimization_factors['inventory_automation']
        else:
            return self.optimization_factors['labor_automation']
    
    def _apply_recommendation_improvements(self, baseline: BaselineModel, recommendation: Recommendation, factors: Dict[str, Any]) -> Dict[str, float]:
        """Apply recommendation improvements to baseline metrics."""
        metrics = {
            'labor_efficiency': baseline.labor_efficiency,
            'quality_rate': baseline.quality_defect_rate,
            'inventory_turnover': baseline.inventory_turnover,
            'equipment_uptime': baseline.equipment_uptime
        }
        
        category = recommendation.category.lower()
        
        if 'quality' in category:
            metrics['quality_rate'] = baseline.quality_defect_rate * (1 - factors.get('defect_reduction', 0.5))
        elif 'inventory' in category:
            metrics['inventory_turnover'] = baseline.inventory_turnover * (1 + factors.get('turnover_improvement', 0.25))
        else:
            metrics['labor_efficiency'] = baseline.labor_efficiency * (1 + factors.get('labor_efficiency_gain', 0.15))
        
        return metrics
    
    def _estimate_implementation_costs(self, recommendation: Recommendation, baseline: BaselineModel) -> Dict[str, float]:
        """Estimate implementation costs for a recommendation."""
        # Base cost as percentage of revenue
        base_cost_pct = {
            'low': 0.02,
            'medium': 0.05,
            'high': 0.10
        }
        
        effort = recommendation.implementation_effort.lower()
        base_cost = baseline.revenue * base_cost_pct.get(effort, 0.05)
        
        return {
            'software_license': base_cost * 0.4,
            'implementation_services': base_cost * 0.4,
            'training': base_cost * 0.1,
            'hardware': base_cost * 0.1
        }
    
    def _calculate_period_projection(self, scenario: OptimizationScenario, months: int) -> ProjectionPeriod:
        """Calculate projections for a specific time period."""
        monthly_cash_flow = []
        cumulative_cash_flow = []
        cumulative_savings = 0
        cumulative_costs = sum(scenario.implementation_costs.values())
        
        running_cumulative = -cumulative_costs  # Start with negative (implementation cost)
        
        for month in range(1, months + 1):
            month_savings = scenario.calculate_monthly_savings(month)
            monthly_cash_flow.append(month_savings['total_savings'])
            cumulative_savings += month_savings['total_savings']
            
            running_cumulative += month_savings['total_savings']
            cumulative_cash_flow.append(running_cumulative)
        
        net_benefit = cumulative_savings - cumulative_costs
        roi_percentage = (net_benefit / cumulative_costs * 100) if cumulative_costs > 0 else 0
        
        # Check if payback achieved
        payback_achieved = running_cumulative >= 0
        break_even_month = None
        
        for i, cf in enumerate(cumulative_cash_flow):
            if cf >= 0:
                break_even_month = i + 1
                break
        
        return ProjectionPeriod(
            period_name=f"{months}_months",
            months=months,
            cumulative_savings=cumulative_savings,
            cumulative_costs=cumulative_costs,
            net_benefit=net_benefit,
            monthly_cash_flow=monthly_cash_flow,
            cumulative_cash_flow=cumulative_cash_flow,
            roi_percentage=roi_percentage,
            payback_achieved=payback_achieved,
            break_even_month=break_even_month
        )
    
    def _calculate_payback_period(self, initial_cost: float, monthly_savings: List[float]) -> Optional[int]:
        """Calculate payback period in months."""
        cumulative = 0
        for month, savings in enumerate(monthly_savings, 1):
            cumulative += savings
            if cumulative >= initial_cost:
                return month
        return None
    
    def _calculate_npv(self, initial_cost: float, monthly_savings: List[float], discount_rate: float) -> float:
        """Calculate Net Present Value."""
        npv = -initial_cost
        
        for month, savings in enumerate(monthly_savings, 1):
            present_value = savings / ((1 + discount_rate) ** month)
            npv += present_value
        
        return npv
    
    def _calculate_break_even(self, initial_cost: float, monthly_savings: List[float]) -> Optional[int]:
        """Calculate break-even month."""
        return self._calculate_payback_period(initial_cost, monthly_savings)
    
    def _calculate_cash_flow_impact(self, baseline: BaselineModel, optimized: OptimizationScenario, months: int) -> Dict[str, List[float]]:
        """Calculate detailed cash flow impact."""
        baseline_flow = [baseline.monthly_profit] * months
        optimized_flow = []
        
        for month in range(1, months + 1):
            month_savings = optimized.calculate_monthly_savings(month)
            optimized_monthly = baseline.monthly_profit + month_savings['total_savings']
            optimized_flow.append(optimized_monthly)
        
        return {
            'baseline_monthly': baseline_flow,
            'optimized_monthly': optimized_flow,
            'improvement': [opt - base for opt, base in zip(optimized_flow, baseline_flow)]
        }