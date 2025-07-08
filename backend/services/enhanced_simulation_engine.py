#!/usr/bin/env python3
"""
Enhanced Manufacturing Digital Twin Simulation Engine

Advanced manufacturing-specific calculations including:
- Labor optimization through automation
- Defect reduction and quality control savings
- Inventory optimization and carrying cost reduction
- Customer service automation efficiency gains
- Month-by-month cash flow projections
- Break-even analysis for AI investments
- Cumulative savings tracking over time
"""

import logging
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum

logger = logging.getLogger(__name__)

class AutomationType(Enum):
    """Types of automation implementations."""
    LABOR = "labor"
    QUALITY = "quality"
    INVENTORY = "inventory"
    CUSTOMER_SERVICE = "customer_service"

class ImplementationPhase(Enum):
    """Phases of automation implementation."""
    PLANNING = "planning"
    INSTALLATION = "installation"
    TESTING = "testing"
    TRAINING = "training"
    ROLLOUT = "rollout"
    OPTIMIZATION = "optimization"

@dataclass
class ManufacturingMetrics:
    """Detailed manufacturing operational metrics."""
    # Production metrics
    units_per_hour: float = 100.0
    setup_time_hours: float = 2.0
    changeover_time_hours: float = 1.5
    
    # Quality metrics
    first_pass_yield: float = 0.95  # 95% pass rate
    rework_rate: float = 0.03  # 3% require rework
    scrap_rate: float = 0.02  # 2% scrap
    
    # Labor metrics
    direct_labor_hours_per_unit: float = 0.5
    indirect_labor_ratio: float = 0.3  # 30% indirect vs direct
    overtime_percentage: float = 0.10  # 10% overtime
    labor_utilization: float = 0.85  # 85% utilization
    
    # Inventory metrics
    raw_material_days: float = 30.0
    wip_days: float = 15.0
    finished_goods_days: float = 45.0
    safety_stock_percentage: float = 0.20  # 20% safety stock
    
    # Customer service metrics
    order_processing_time_hours: float = 4.0
    inquiry_response_time_hours: float = 24.0
    service_agent_capacity_per_day: int = 50  # requests per agent per day

@dataclass
class CostBreakdown:
    """Detailed cost breakdown for manufacturing operations."""
    # Labor costs (annual)
    direct_labor_cost: float = 0.0
    indirect_labor_cost: float = 0.0
    overtime_cost: float = 0.0
    benefits_cost: float = 0.0  # Healthcare, etc.
    
    # Quality costs (annual)
    rework_cost: float = 0.0
    scrap_cost: float = 0.0
    inspection_cost: float = 0.0
    warranty_cost: float = 0.0
    
    # Inventory costs (annual)
    carrying_cost: float = 0.0
    obsolescence_cost: float = 0.0
    storage_cost: float = 0.0
    insurance_cost: float = 0.0
    
    # Customer service costs (annual)
    agent_salaries: float = 0.0
    system_costs: float = 0.0
    training_costs: float = 0.0
    
    def total_costs(self) -> float:
        """Calculate total operational costs."""
        return (
            self.direct_labor_cost + self.indirect_labor_cost + self.overtime_cost + self.benefits_cost +
            self.rework_cost + self.scrap_cost + self.inspection_cost + self.warranty_cost +
            self.carrying_cost + self.obsolescence_cost + self.storage_cost + self.insurance_cost +
            self.agent_salaries + self.system_costs + self.training_costs
        )

@dataclass
class AutomationImpact:
    """Impact of automation on specific operational areas."""
    automation_type: AutomationType
    
    # Efficiency improvements (as multipliers, e.g., 1.15 = 15% improvement)
    productivity_improvement: float = 1.0
    quality_improvement: float = 1.0  # reduction in defects
    cost_reduction: float = 1.0  # reduction in operating costs
    
    # Implementation details
    implementation_cost: float = 0.0
    implementation_months: int = 6
    ramp_up_months: int = 3
    
    # Ongoing costs
    annual_maintenance_cost: float = 0.0
    annual_license_cost: float = 0.0
    training_cost_per_employee: float = 0.0

@dataclass
class MonthlyProjection:
    """Month-by-month financial projections."""
    month: int
    
    # Revenue and costs
    revenue: float = 0.0
    labor_costs: float = 0.0
    quality_costs: float = 0.0
    inventory_costs: float = 0.0
    service_costs: float = 0.0
    implementation_costs: float = 0.0
    
    # Savings
    labor_savings: float = 0.0
    quality_savings: float = 0.0
    inventory_savings: float = 0.0
    service_savings: float = 0.0
    total_savings: float = 0.0
    
    # Cash flow
    monthly_cash_flow: float = 0.0
    cumulative_cash_flow: float = 0.0
    
    # Metrics
    roi_to_date: float = 0.0
    payback_achieved: bool = False

@dataclass
class EnhancedBaselineModel:
    """Enhanced baseline model with detailed manufacturing metrics."""
    # Financial data (from P&L)
    revenue: float
    cogs: float
    labor_costs: float
    overhead_costs: float
    
    # Operational data
    production_volume: int
    employee_count: int
    automation_level: str
    
    # Detailed manufacturing metrics
    manufacturing_metrics: ManufacturingMetrics = field(default_factory=ManufacturingMetrics)
    cost_breakdown: CostBreakdown = field(default_factory=CostBreakdown)
    
    def __post_init__(self):
        """Calculate detailed cost breakdown from high-level P&L data."""
        self._calculate_detailed_costs()
    
    def _calculate_detailed_costs(self):
        """Break down high-level costs into detailed categories."""
        # Labor cost breakdown
        total_labor = self.labor_costs
        self.cost_breakdown.direct_labor_cost = total_labor * 0.7  # 70% direct
        self.cost_breakdown.indirect_labor_cost = total_labor * 0.2  # 20% indirect
        self.cost_breakdown.overtime_cost = total_labor * 0.05  # 5% overtime
        self.cost_breakdown.benefits_cost = total_labor * 0.05  # 5% benefits
        
        # Quality cost breakdown (from COGS)
        quality_portion = self.cogs * 0.15  # 15% of COGS related to quality issues
        self.cost_breakdown.rework_cost = quality_portion * 0.4  # 40% rework
        self.cost_breakdown.scrap_cost = quality_portion * 0.3  # 30% scrap
        self.cost_breakdown.inspection_cost = quality_portion * 0.2  # 20% inspection
        self.cost_breakdown.warranty_cost = quality_portion * 0.1  # 10% warranty
        
        # Inventory cost breakdown (from overhead)
        inventory_portion = self.overhead_costs * 0.25  # 25% of overhead is inventory-related
        self.cost_breakdown.carrying_cost = inventory_portion * 0.6  # 60% carrying
        self.cost_breakdown.storage_cost = inventory_portion * 0.25  # 25% storage
        self.cost_breakdown.obsolescence_cost = inventory_portion * 0.10  # 10% obsolescence
        self.cost_breakdown.insurance_cost = inventory_portion * 0.05  # 5% insurance
        
        # Customer service cost breakdown
        service_portion = self.overhead_costs * 0.10  # 10% of overhead is service-related
        self.cost_breakdown.agent_salaries = service_portion * 0.7  # 70% salaries
        self.cost_breakdown.system_costs = service_portion * 0.2  # 20% systems
        self.cost_breakdown.training_costs = service_portion * 0.1  # 10% training

class EnhancedSimulationEngine:
    """
    Enhanced Manufacturing Digital Twin Simulation Engine.
    
    Provides detailed manufacturing-specific calculations with:
    - Advanced labor optimization modeling
    - Quality control and defect reduction analysis
    - Inventory optimization with carrying cost calculations
    - Customer service automation benefits
    - Month-by-month cash flow projections
    - Break-even analysis for AI investments
    """
    
    def __init__(self):
        # Manufacturing-specific optimization factors - realistic ranges
        self.labor_optimization_factors = {
            'productivity_gain': 0.25,  # 25% productivity improvement
            'error_reduction': 0.30,  # 30% reduction in human errors
            'overtime_reduction': 0.35,  # 35% reduction in overtime
            'setup_time_reduction': 0.20,  # 20% faster setup
            'implementation_months': 4,
            'ramp_up_months': 2
        }
        
        self.quality_optimization_factors = {
            'defect_reduction': 0.50,  # 50% reduction in defects (realistic)
            'first_pass_yield_improvement': 0.10,  # 10% improvement
            'rework_reduction': 0.60,  # 60% reduction in rework  
            'scrap_reduction': 0.40,  # 40% reduction in scrap
            'implementation_months': 6,
            'ramp_up_months': 4
        }
        
        self.inventory_optimization_factors = {
            'turnover_improvement': 0.20,  # 20% faster turnover (realistic)
            'safety_stock_reduction': 0.15,  # 15% less safety stock
            'obsolescence_reduction': 0.25,  # 25% less obsolescence
            'carrying_cost_reduction': 0.20,  # 20% lower carrying costs
            'implementation_months': 3,
            'ramp_up_months': 2
        }
        
        self.service_optimization_factors = {
            'response_time_improvement': 0.70,  # 70% faster response
            'agent_productivity_gain': 0.40,  # 40% more efficient agents
            'automation_rate': 0.60,  # 60% of inquiries automated
            'cost_per_interaction_reduction': 0.50,  # 50% lower cost per interaction
            'implementation_months': 2,
            'ramp_up_months': 1
        }
    
    def create_enhanced_baseline(self, company_data: Dict[str, Any], questionnaire_analysis: Dict[str, Any] = None) -> EnhancedBaselineModel:
        """
        Create enhanced baseline model with detailed manufacturing metrics.
        
        Args:
            company_data: Combined P&L data and questionnaire responses
            questionnaire_analysis: Enhanced AI analysis of 12-question assessment
            
        Returns:
            EnhancedBaselineModel with detailed cost breakdown
        """
        try:
            # Extract basic financial data
            financial_data = company_data.get('financial_data', {})
            revenue = financial_data.get('revenue', 0)
            cogs = financial_data.get('cogs', 0)
            labor_costs = financial_data.get('labor_costs', 0)
            overhead_costs = financial_data.get('overhead_costs', 0)
            
            # Extract operational data with enhanced questionnaire analysis
            company_profile = company_data.get('company_profile', {})
            
            # Use questionnaire analysis for more accurate baseline if available
            if questionnaire_analysis:
                operational_assessment = questionnaire_analysis.get('operational_assessment', {})
                company_profile_enhanced = questionnaire_analysis.get('company_profile', {})
                
                # Get more accurate production volume from analysis
                production_volume = self._parse_production_volume_from_analysis(
                    operational_assessment.get('production_volume_annual', '250,000 units/year')
                )
                employee_count = self._parse_employee_count_enhanced(
                    company_profile_enhanced.get('size_category', 'medium')
                )
                automation_level = operational_assessment.get('automation_percentage', '25%')
                
                # Extract specific metrics from detailed analysis
                quality_loss_pct = self._extract_percentage(
                    operational_assessment.get('quality_loss_percentage', '10-20%')
                )
                
            else:
                # Fallback to original parsing
                production_volume = self._parse_production_volume(
                    company_profile.get('production_volume', '1000-10000 units/day')
                )
                employee_count = self._parse_employee_count(
                    company_profile.get('employee_count', '11-50 employees')
                )
                automation_level = company_profile.get('automation_level', 'Some automated tools')
                quality_loss_pct = 0.15  # Default 15%
            
            # Create detailed manufacturing metrics based on enhanced data
            manufacturing_metrics = self._estimate_manufacturing_metrics_enhanced(
                revenue, production_volume, employee_count, automation_level, 
                quality_loss_pct, questionnaire_analysis
            )
            
            baseline = EnhancedBaselineModel(
                revenue=revenue,
                cogs=cogs,
                labor_costs=labor_costs,
                overhead_costs=overhead_costs,
                production_volume=production_volume,
                employee_count=employee_count,
                automation_level=automation_level,
                manufacturing_metrics=manufacturing_metrics
            )
            
            logger.info(f"Created enhanced baseline: Revenue ${revenue:,.2f}, Volume {production_volume:,} units")
            return baseline
            
        except Exception as e:
            logger.error(f"Failed to create enhanced baseline: {e}")
            raise ValueError(f"Enhanced baseline creation failed: {e}")
    
    def calculate_labor_optimization(self, baseline: EnhancedBaselineModel, automation_level: float = 0.5) -> Dict[str, float]:
        """
        Calculate detailed labor cost optimization through automation.
        
        Args:
            baseline: Current baseline model
            automation_level: Level of automation (0.0 to 1.0)
            
        Returns:
            Dictionary with detailed labor savings breakdown
        """
        try:
            factors = self.labor_optimization_factors
            
            # Calculate base savings potential
            productivity_gain = factors['productivity_gain'] * automation_level
            error_reduction = factors['error_reduction'] * automation_level
            overtime_reduction = factors['overtime_reduction'] * automation_level
            
            # Calculate specific savings with company size adjustments
            direct_labor_savings = baseline.cost_breakdown.direct_labor_cost * productivity_gain
            indirect_labor_savings = baseline.cost_breakdown.indirect_labor_cost * (error_reduction * 0.5)
            overtime_savings = baseline.cost_breakdown.overtime_cost * overtime_reduction
            
            # Adjust savings based on company size and current automation level
            if baseline.employee_count > 200:  # Large company
                direct_labor_savings *= 1.15  # 15% bonus for economies of scale
                implementation_cost_multiplier = 0.015  # Lower per-revenue cost
            elif baseline.employee_count < 25:  # Small company  
                direct_labor_savings *= 0.85  # 15% reduction for small scale
                implementation_cost_multiplier = 0.025  # Higher per-revenue cost
            else:  # Medium company
                implementation_cost_multiplier = 0.02  # Reduced cost
            
            # Training and reskilling costs - vary by company size (reduced costs)
            base_training_cost = 800 if baseline.employee_count < 50 else 1200
            training_cost = baseline.employee_count * base_training_cost * automation_level
            
            # Implementation costs - scale with revenue and automation level
            implementation_cost = baseline.revenue * implementation_cost_multiplier * automation_level
            
            total_annual_savings = direct_labor_savings + indirect_labor_savings + overtime_savings
            net_savings_year_1 = total_annual_savings - training_cost - implementation_cost
            
            return {
                'direct_labor_savings': direct_labor_savings,
                'indirect_labor_savings': indirect_labor_savings,
                'overtime_savings': overtime_savings,
                'total_annual_savings': total_annual_savings,
                'training_cost': training_cost,
                'implementation_cost': implementation_cost,
                'net_savings_year_1': net_savings_year_1,
                'payback_months': (training_cost + implementation_cost) / (total_annual_savings / 12) if total_annual_savings > 0 else 999,
                'roi_percentage': (net_savings_year_1 / (training_cost + implementation_cost) * 100) if (training_cost + implementation_cost) > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Labor optimization calculation failed: {e}")
            raise
    
    def calculate_quality_optimization(self, baseline: EnhancedBaselineModel, automation_level: float = 0.5) -> Dict[str, float]:
        """
        Calculate quality control savings through defect reduction.
        
        Args:
            baseline: Current baseline model
            automation_level: Level of quality automation (0.0 to 1.0)
            
        Returns:
            Dictionary with detailed quality savings breakdown
        """
        try:
            factors = self.quality_optimization_factors
            
            # Calculate improvement rates
            defect_reduction = factors['defect_reduction'] * automation_level
            rework_reduction = factors['rework_reduction'] * automation_level
            scrap_reduction = factors['scrap_reduction'] * automation_level
            
            # Calculate specific savings with realistic scaling
            rework_savings = baseline.cost_breakdown.rework_cost * rework_reduction
            scrap_savings = baseline.cost_breakdown.scrap_cost * scrap_reduction
            inspection_savings = baseline.cost_breakdown.inspection_cost * (defect_reduction * 0.3)  # Less inspection needed
            warranty_savings = baseline.cost_breakdown.warranty_cost * defect_reduction
            
            # Adjust quality savings based on production volume and complexity
            if baseline.production_volume > 1000000:  # High volume operations
                # Higher volumes = more savings from quality improvements
                rework_savings *= 1.2
                scrap_savings *= 1.2
                quality_system_cost_multiplier = 0.008  # Economies of scale
            elif baseline.production_volume < 100000:  # Low volume
                # Lower volumes = less dramatic savings
                rework_savings *= 0.8
                scrap_savings *= 0.8
                quality_system_cost_multiplier = 0.015  # Higher per-revenue cost
            else:
                quality_system_cost_multiplier = 0.012  # Reduced cost
            
            # Implementation costs for quality systems
            quality_system_cost = baseline.revenue * quality_system_cost_multiplier * automation_level
            training_cost = baseline.employee_count * 600 * automation_level  # Reduced base cost
            
            total_annual_savings = rework_savings + scrap_savings + inspection_savings + warranty_savings
            net_savings_year_1 = total_annual_savings - quality_system_cost - training_cost
            
            return {
                'rework_savings': rework_savings,
                'scrap_savings': scrap_savings,
                'inspection_savings': inspection_savings,
                'warranty_savings': warranty_savings,
                'total_annual_savings': total_annual_savings,
                'quality_system_cost': quality_system_cost,
                'training_cost': training_cost,
                'net_savings_year_1': net_savings_year_1,
                'payback_months': (quality_system_cost + training_cost) / (total_annual_savings / 12) if total_annual_savings > 0 else 999,
                'roi_percentage': (net_savings_year_1 / (quality_system_cost + training_cost) * 100) if (quality_system_cost + training_cost) > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Quality optimization calculation failed: {e}")
            raise
    
    def calculate_inventory_optimization(self, baseline: EnhancedBaselineModel, automation_level: float = 0.5) -> Dict[str, float]:
        """
        Calculate inventory carrying cost reduction through optimization.
        
        Args:
            baseline: Current baseline model
            automation_level: Level of inventory automation (0.0 to 1.0)
            
        Returns:
            Dictionary with detailed inventory savings breakdown
        """
        try:
            factors = self.inventory_optimization_factors
            
            # Calculate improvement rates
            turnover_improvement = factors['turnover_improvement'] * automation_level
            carrying_cost_reduction = factors['carrying_cost_reduction'] * automation_level
            obsolescence_reduction = factors['obsolescence_reduction'] * automation_level
            
            # Calculate specific savings
            carrying_cost_savings = baseline.cost_breakdown.carrying_cost * carrying_cost_reduction
            storage_savings = baseline.cost_breakdown.storage_cost * (turnover_improvement * 0.5)
            obsolescence_savings = baseline.cost_breakdown.obsolescence_cost * obsolescence_reduction
            
            # Working capital freed up (estimated)
            inventory_value = baseline.cogs * 0.25  # Assume 25% of COGS in inventory
            working_capital_freed = inventory_value * turnover_improvement
            working_capital_benefit = working_capital_freed * 0.08  # 8% cost of capital
            
            # Implementation costs (reduced)
            system_cost = baseline.revenue * 0.008 * automation_level  # 0.8% of revenue
            training_cost = baseline.employee_count * 500 * automation_level  # $500 per employee
            
            total_annual_savings = carrying_cost_savings + storage_savings + obsolescence_savings + working_capital_benefit
            net_savings_year_1 = total_annual_savings - system_cost - training_cost
            
            return {
                'carrying_cost_savings': carrying_cost_savings,
                'storage_savings': storage_savings,
                'obsolescence_savings': obsolescence_savings,
                'working_capital_benefit': working_capital_benefit,
                'working_capital_freed': working_capital_freed,
                'total_annual_savings': total_annual_savings,
                'system_cost': system_cost,
                'training_cost': training_cost,
                'net_savings_year_1': net_savings_year_1,
                'payback_months': (system_cost + training_cost) / (total_annual_savings / 12) if total_annual_savings > 0 else 999,
                'roi_percentage': (net_savings_year_1 / (system_cost + training_cost) * 100) if (system_cost + training_cost) > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Inventory optimization calculation failed: {e}")
            raise
    
    def calculate_service_automation(self, baseline: EnhancedBaselineModel, automation_level: float = 0.5) -> Dict[str, float]:
        """
        Calculate customer service efficiency gains through automation.
        
        Args:
            baseline: Current baseline model
            automation_level: Level of service automation (0.0 to 1.0)
            
        Returns:
            Dictionary with detailed service efficiency gains
        """
        try:
            factors = self.service_optimization_factors
            
            # Calculate improvement rates
            automation_rate = factors['automation_rate'] * automation_level
            productivity_gain = factors['agent_productivity_gain'] * automation_level
            cost_reduction = factors['cost_per_interaction_reduction'] * automation_level
            
            # Calculate specific savings
            agent_cost_savings = baseline.cost_breakdown.agent_salaries * (automation_rate * 0.6)  # 60% of automated interactions save agent time
            productivity_savings = baseline.cost_breakdown.agent_salaries * productivity_gain
            system_efficiency_savings = baseline.cost_breakdown.system_costs * cost_reduction
            
            # Implementation costs (reduced)
            automation_platform_cost = baseline.revenue * 0.005 * automation_level  # 0.5% of revenue
            setup_cost = 15000 * automation_level  # Reduced base setup cost
            
            total_annual_savings = agent_cost_savings + productivity_savings + system_efficiency_savings
            net_savings_year_1 = total_annual_savings - automation_platform_cost - setup_cost
            
            return {
                'agent_cost_savings': agent_cost_savings,
                'productivity_savings': productivity_savings,
                'system_efficiency_savings': system_efficiency_savings,
                'total_annual_savings': total_annual_savings,
                'automation_platform_cost': automation_platform_cost,
                'setup_cost': setup_cost,
                'net_savings_year_1': net_savings_year_1,
                'payback_months': (automation_platform_cost + setup_cost) / (total_annual_savings / 12) if total_annual_savings > 0 else 999,
                'roi_percentage': (net_savings_year_1 / (automation_platform_cost + setup_cost) * 100) if (automation_platform_cost + setup_cost) > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Service automation calculation failed: {e}")
            raise
    
    def generate_monthly_projections(self, baseline: EnhancedBaselineModel, automation_levels: Dict[str, float], months: int = 24) -> List[MonthlyProjection]:
        """
        Generate month-by-month cash flow projections with cumulative savings.
        
        Args:
            baseline: Current baseline model
            automation_levels: Dict with automation levels for each area
            months: Number of months to project
            
        Returns:
            List of monthly projections
        """
        try:
            # Calculate optimization savings for each area
            labor_opt = self.calculate_labor_optimization(baseline, automation_levels.get('labor', 0.5))
            quality_opt = self.calculate_quality_optimization(baseline, automation_levels.get('quality', 0.5))
            inventory_opt = self.calculate_inventory_optimization(baseline, automation_levels.get('inventory', 0.5))
            service_opt = self.calculate_service_automation(baseline, automation_levels.get('service', 0.5))
            
            # Calculate total implementation costs
            total_implementation_cost = (
                labor_opt['implementation_cost'] + labor_opt['training_cost'] +
                quality_opt['quality_system_cost'] + quality_opt['training_cost'] +
                inventory_opt['system_cost'] + inventory_opt['training_cost'] +
                service_opt['automation_platform_cost'] + service_opt['setup_cost']
            )
            
            # Generate monthly projections
            projections = []
            cumulative_cash_flow = -total_implementation_cost  # Start with negative implementation cost
            cumulative_savings = 0
            
            for month in range(1, months + 1):
                # Calculate ramp-up factors for each optimization area
                labor_ramp = self._calculate_ramp_factor(month, 4, 2)  # 4 month implementation, 2 month ramp
                quality_ramp = self._calculate_ramp_factor(month, 6, 4)  # 6 month implementation, 4 month ramp
                inventory_ramp = self._calculate_ramp_factor(month, 3, 2)  # 3 month implementation, 2 month ramp
                service_ramp = self._calculate_ramp_factor(month, 2, 1)  # 2 month implementation, 1 month ramp
                
                # Calculate monthly savings with ramp-up
                monthly_labor_savings = (labor_opt['total_annual_savings'] / 12) * labor_ramp
                monthly_quality_savings = (quality_opt['total_annual_savings'] / 12) * quality_ramp
                monthly_inventory_savings = (inventory_opt['total_annual_savings'] / 12) * inventory_ramp
                monthly_service_savings = (service_opt['total_annual_savings'] / 12) * service_ramp
                
                total_monthly_savings = (
                    monthly_labor_savings + monthly_quality_savings + 
                    monthly_inventory_savings + monthly_service_savings
                )
                
                # Calculate implementation costs for this month (front-loaded)
                monthly_implementation_cost = 0
                if month <= 6:  # Spread implementation over first 6 months
                    monthly_implementation_cost = total_implementation_cost / 6
                
                # Calculate cash flow
                monthly_cash_flow = total_monthly_savings - monthly_implementation_cost
                cumulative_cash_flow += monthly_cash_flow
                cumulative_savings += total_monthly_savings
                
                # Calculate corrected ROI to date
                total_invested = total_implementation_cost
                # ROI calculation: (cumulative_savings - total_investment) / total_investment * 100
                # This should be negative early on and become positive after break-even
                roi_to_date = (cumulative_savings - total_invested) / total_invested * 100 if total_invested > 0 else 0
                
                projection = MonthlyProjection(
                    month=month,
                    revenue=baseline.revenue / 12,  # Monthly revenue stays constant
                    labor_costs=baseline.labor_costs / 12,
                    quality_costs=baseline.cost_breakdown.rework_cost + baseline.cost_breakdown.scrap_cost / 12,
                    inventory_costs=baseline.cost_breakdown.carrying_cost / 12,
                    service_costs=baseline.cost_breakdown.agent_salaries / 12,
                    implementation_costs=monthly_implementation_cost,
                    labor_savings=monthly_labor_savings,
                    quality_savings=monthly_quality_savings,
                    inventory_savings=monthly_inventory_savings,
                    service_savings=monthly_service_savings,
                    total_savings=total_monthly_savings,
                    monthly_cash_flow=monthly_cash_flow,
                    cumulative_cash_flow=cumulative_cash_flow,
                    roi_to_date=roi_to_date,
                    payback_achieved=cumulative_cash_flow >= 0
                )
                
                projections.append(projection)
            
            logger.info(f"Generated {len(projections)} monthly projections")
            return projections
            
        except Exception as e:
            logger.error(f"Monthly projection generation failed: {e}")
            raise
    
    def analyze_break_even(self, projections: List[MonthlyProjection]) -> Dict[str, Any]:
        """
        Analyze break-even points and investment recovery timeline with comprehensive ROI metrics.
        
        Args:
            projections: List of monthly projections
            
        Returns:
            Dictionary with break-even analysis and ROI metrics
        """
        try:
            break_even_month = None
            total_investment = 0
            
            # Find break-even point
            for projection in projections:
                if projection.implementation_costs > 0:
                    total_investment += projection.implementation_costs
                
                if projection.cumulative_cash_flow >= 0 and break_even_month is None:
                    break_even_month = projection.month
                    break
            
            # Calculate final metrics
            final_projection = projections[-1] if projections else None
            
            if final_projection:
                total_savings = sum(p.total_savings for p in projections)
                net_benefit = total_savings - total_investment
                
                # Calculate corrected ROI metrics
                annual_roi = 0
                three_year_roi = 0
                five_year_roi = 0
                
                if total_investment > 0:
                    # Annual ROI (12 months savings vs total investment)
                    annual_savings = sum(p.total_savings for p in projections[:12]) if len(projections) >= 12 else total_savings
                    annual_roi = ((annual_savings - total_investment) / total_investment) * 100
                    
                    # 3-year ROI (36 months or available projections)
                    three_year_months = min(36, len(projections))
                    three_year_savings = sum(p.total_savings for p in projections[:three_year_months])
                    three_year_roi = ((three_year_savings - total_investment) / total_investment) * 100
                    
                    # 5-year ROI (extrapolate if needed)
                    if len(projections) >= 60:
                        five_year_savings = sum(p.total_savings for p in projections[:60])
                    else:
                        # Use the average monthly savings from available data to extrapolate
                        if len(projections) >= 12:
                            avg_monthly_savings = annual_savings / 12
                            five_year_savings = avg_monthly_savings * 60
                        else:
                            # If less than 12 months, extrapolate from available data
                            avg_monthly_savings = total_savings / len(projections) if len(projections) > 0 else 0
                            five_year_savings = avg_monthly_savings * 60
                    
                    five_year_roi = ((five_year_savings - total_investment) / total_investment) * 100
                
                # Calculate break-even date
                break_even_date = None
                if break_even_month:
                    from datetime import datetime, timedelta
                    start_date = datetime.now()
                    break_even_date = (start_date + timedelta(days=30 * break_even_month)).strftime('%Y-%m-%d')
                
                return {
                    'break_even_month': break_even_month,
                    'total_investment': total_investment,
                    'total_savings': total_savings,
                    'net_benefit': net_benefit,
                    'payback_achieved': break_even_month is not None,
                    'cumulative_cash_flow_final': final_projection.cumulative_cash_flow,
                    'average_monthly_savings': total_savings / len(projections),
                    'investment_recovery_timeline': f"{break_even_month} months" if break_even_month else "Not achieved in projection period",
                    'roi_metrics': {
                        'total_investment': total_investment,
                        'annual_roi': annual_roi,
                        'three_year_roi': three_year_roi,
                        'five_year_roi': five_year_roi,
                        'payback_months': break_even_month or len(projections),
                        'break_even_date': break_even_date
                    }
                }
            else:
                return {
                    'break_even_month': None,
                    'total_investment': 0,
                    'total_savings': 0,
                    'net_benefit': 0,
                    'payback_achieved': False,
                    'error': 'No projections available',
                    'roi_metrics': {
                        'total_investment': 0,
                        'annual_roi': 0,
                        'three_year_roi': 0,
                        'five_year_roi': 0,
                        'payback_months': 999,
                        'break_even_date': None
                    }
                }
                
        except Exception as e:
            logger.error(f"Break-even analysis failed: {e}")
            raise
    
    # Helper methods
    
    def _parse_production_volume(self, volume_str: str) -> int:
        """Parse production volume from questionnaire response."""
        if '< 100' in volume_str or 'under' in volume_str.lower():
            return 50 * 250  # 50 units/day * 250 working days
        elif '100-1000' in volume_str:
            return 500 * 250
        elif '1000-10000' in volume_str:
            return 5000 * 250
        elif '> 10000' in volume_str or 'over' in volume_str.lower():
            return 15000 * 250
        return 500000  # Default
    
    def _parse_employee_count(self, employee_str: str) -> int:
        """Parse employee count from questionnaire response."""
        if '1-10' in employee_str:
            return 5
        elif '11-50' in employee_str:
            return 25
        elif '51-200' in employee_str:
            return 100
        elif '200+' in employee_str or 'over' in employee_str.lower():
            return 300
        return 25  # Default
    
    def _estimate_manufacturing_metrics(self, revenue: float, volume: int, employees: int, automation: str) -> ManufacturingMetrics:
        """Estimate detailed manufacturing metrics based on company profile."""
        metrics = ManufacturingMetrics()
        
        # Adjust based on company size and automation level
        if 'manual' in automation.lower():
            metrics.first_pass_yield = 0.90
            metrics.rework_rate = 0.05
            metrics.labor_utilization = 0.80
        elif 'highly automated' in automation.lower():
            metrics.first_pass_yield = 0.98
            metrics.rework_rate = 0.01
            metrics.labor_utilization = 0.90
        
        # Scale metrics based on production volume
        if volume > 1000000:  # High volume
            metrics.units_per_hour = 200
            metrics.setup_time_hours = 1.0
        elif volume < 100000:  # Low volume
            metrics.units_per_hour = 50
            metrics.setup_time_hours = 4.0
        
        return metrics
    
    def _parse_production_volume_from_analysis(self, annual_volume_str: str) -> int:
        """Parse annual production volume from AI analysis."""
        volume_str = annual_volume_str.lower()
        if '25,000' in volume_str or '25000' in volume_str:
            return 25000
        elif '75,000' in volume_str or '75000' in volume_str:
            return 75000
        elif '375,000' in volume_str or '375000' in volume_str:
            return 375000
        elif '1.5m' in volume_str or '1,500,000' in volume_str:
            return 1500000
        elif '7.5m' in volume_str or '7,500,000' in volume_str:
            return 7500000
        elif '15m' in volume_str or '15,000,000' in volume_str:
            return 15000000
        return 250000  # Default
    
    def _parse_employee_count_enhanced(self, size_category: str) -> int:
        """Parse employee count from enhanced size category."""
        if size_category == 'small':
            return 15
        elif size_category == 'large':
            return 350
        else:  # medium
            return 75
    
    def _extract_percentage(self, percentage_str: str) -> float:
        """Extract percentage value from string like '10-20%' or '15%'."""
        import re
        numbers = re.findall(r'\d+', percentage_str)
        if len(numbers) >= 2:
            # Range like "10-20%", take average
            return (int(numbers[0]) + int(numbers[1])) / 200.0
        elif len(numbers) == 1:
            # Single value like "15%"
            return int(numbers[0]) / 100.0
        return 0.15  # Default 15%
    
    def _estimate_manufacturing_metrics_enhanced(self, revenue: float, volume: int, employees: int, 
                                               automation_level: str, quality_loss_pct: float,
                                               questionnaire_analysis: Dict[str, Any] = None) -> ManufacturingMetrics:
        """Enhanced manufacturing metrics estimation using questionnaire analysis."""
        metrics = ManufacturingMetrics()
        
        # Parse automation percentage
        automation_pct = self._extract_percentage(automation_level) if isinstance(automation_level, str) else 0.25
        
        # Adjust metrics based on automation level and questionnaire insights
        if questionnaire_analysis:
            automation_opportunities = questionnaire_analysis.get('automation_opportunities', {})
            
            # Adjust quality metrics based on analysis
            quality_potential = automation_opportunities.get('quality_control', {}).get('potential', 'medium')
            if quality_potential == 'high':
                metrics.first_pass_yield = 0.85  # Lower yield indicates more room for improvement
                metrics.rework_rate = quality_loss_pct * 0.6
                metrics.scrap_rate = quality_loss_pct * 0.4
            elif quality_potential == 'low':
                metrics.first_pass_yield = 0.95  # Already good
                metrics.rework_rate = 0.02
                metrics.scrap_rate = 0.01
            else:
                metrics.first_pass_yield = 0.90
                metrics.rework_rate = quality_loss_pct * 0.7
                metrics.scrap_rate = quality_loss_pct * 0.3
            
            # Adjust labor metrics
            labor_potential = automation_opportunities.get('labor_optimization', {}).get('potential', 'medium')
            if labor_potential == 'high':
                metrics.labor_utilization = 0.75  # Lower utilization means more improvement potential
                metrics.overtime_percentage = 0.15
            elif labor_potential == 'low':
                metrics.labor_utilization = 0.90
                metrics.overtime_percentage = 0.05
            else:
                metrics.labor_utilization = 0.82
                metrics.overtime_percentage = 0.10
                
        else:
            # Fallback to automation percentage estimation
            if automation_pct < 0.20:  # Low automation
                metrics.first_pass_yield = 0.88
                metrics.rework_rate = 0.06
                metrics.labor_utilization = 0.75
            elif automation_pct > 0.60:  # High automation
                metrics.first_pass_yield = 0.96
                metrics.rework_rate = 0.02
                metrics.labor_utilization = 0.88
        
        # Scale metrics based on production volume
        if volume > 1000000:  # High volume
            metrics.units_per_hour = 300
            metrics.setup_time_hours = 0.5
        elif volume < 100000:  # Low volume
            metrics.units_per_hour = 25
            metrics.setup_time_hours = 6.0
        else:
            metrics.units_per_hour = 100
            metrics.setup_time_hours = 2.0
        
        return metrics
    
    def _calculate_ramp_factor(self, month: int, implementation_months: int, ramp_months: int) -> float:
        """Calculate ramp-up factor for gradual benefit realization."""
        if month <= implementation_months:
            # During implementation, linear ramp from 0 to 1
            return month / implementation_months
        elif month <= implementation_months + ramp_months:
            # During ramp-up, continue improving
            ramp_progress = (month - implementation_months) / ramp_months
            return 1.0 + (ramp_progress * 0.2)  # Up to 20% additional benefit
        else:
            # Full benefits after ramp-up
            return 1.2
    
    def generate_smart_recommendations(self, baseline: EnhancedBaselineModel, automation_levels: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Generate smart recommendations with comprehensive financial metrics and filtering.
        
        Args:
            baseline: Current baseline model
            automation_levels: Dict with automation levels for each area
            
        Returns:
            List of recommendations with detailed financial metrics
        """
        try:
            recommendations = []
            
            # Calculate all optimizations
            labor_opt = self.calculate_labor_optimization(baseline, automation_levels.get('labor', 0.5))
            quality_opt = self.calculate_quality_optimization(baseline, automation_levels.get('quality', 0.5))
            inventory_opt = self.calculate_inventory_optimization(baseline, automation_levels.get('inventory', 0.5))
            service_opt = self.calculate_service_automation(baseline, automation_levels.get('service', 0.5))
            
            # Define recommendation templates with realistic descriptions
            rec_templates = [
                {
                    'title': 'Labor Automation & Productivity',
                    'description': 'Implement AI-powered scheduling, automated data entry, and workflow optimization to reduce manual labor and increase productivity',
                    'category': 'labor',
                    'optimization': labor_opt,
                    'base_priority': 1
                },
                {
                    'title': 'Quality Control Automation',
                    'description': 'Deploy automated inspection systems, quality monitoring sensors, and defect tracking to reduce rework and scrap costs',
                    'category': 'quality',
                    'optimization': quality_opt,
                    'base_priority': 2
                },
                {
                    'title': 'Inventory Management System',
                    'description': 'Implement smart inventory tracking, automated reordering, and demand forecasting to optimize stock levels and reduce carrying costs',
                    'category': 'inventory',
                    'optimization': inventory_opt,
                    'base_priority': 3
                },
                {
                    'title': 'Customer Service Automation',
                    'description': 'Deploy AI chatbots, automated order processing, and customer self-service portals to reduce service costs and improve efficiency',
                    'category': 'service',
                    'optimization': service_opt,
                    'base_priority': 4
                }
            ]
            
            # Process each recommendation
            for template in rec_templates:
                opt = template['optimization']
                annual_savings = opt['total_annual_savings']
                total_cost = opt.get('implementation_cost', 0) + opt.get('training_cost', 0) + \
                            opt.get('quality_system_cost', 0) + opt.get('system_cost', 0) + \
                            opt.get('automation_platform_cost', 0) + opt.get('setup_cost', 0)
                
                # Calculate multi-year metrics
                three_year_savings = annual_savings * 3
                five_year_savings = annual_savings * 5
                
                # Calculate ROI
                annual_roi = ((annual_savings - total_cost) / total_cost * 100) if total_cost > 0 else 0
                three_year_roi = ((three_year_savings - total_cost) / total_cost * 100) if total_cost > 0 else 0
                five_year_roi = ((five_year_savings - total_cost) / total_cost * 100) if total_cost > 0 else 0
                
                # Calculate payback period
                payback_months = int((total_cost / annual_savings) * 12) if annual_savings > 0 else 999
                
                # Determine recommendation type
                is_quick_win = payback_months <= 6 and total_cost <= 50000
                
                recommendation = {
                    'title': template['title'],
                    'description': template['description'],
                    'category': template['category'],
                    'type': 'quick_win' if is_quick_win else 'standard',
                    'annual_savings': annual_savings,
                    'three_year_savings': three_year_savings,
                    'five_year_savings': five_year_savings,
                    'implementation_cost': total_cost,
                    'annual_roi': annual_roi,
                    'three_year_roi': three_year_roi,
                    'five_year_roi': five_year_roi,
                    'payback_months': payback_months,
                    'priority': template['base_priority'],
                    'cost_breakdown': self._get_cost_breakdown(template['category'], opt),
                    'confidence': 0.85 if is_quick_win else 0.75
                }
                
                # Filter: Only include recommendations with payback <= 36 months
                if payback_months <= 36:
                    recommendations.append(recommendation)
            
            # Sort by 3-year ROI (descending)
            recommendations.sort(key=lambda x: x['three_year_roi'], reverse=True)
            
            # Re-assign priority based on ROI ranking
            for i, rec in enumerate(recommendations):
                rec['priority'] = i + 1
            
            logger.info(f"Generated {len(recommendations)} smart recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Smart recommendation generation failed: {e}")
            return []
    
    def _get_cost_breakdown(self, category: str, optimization: Dict[str, float]) -> Dict[str, float]:
        """Get detailed cost breakdown for recommendation category."""
        if category == 'labor':
            return {
                'software_automation_tools': optimization.get('implementation_cost', 0) * 0.6,
                'training_and_change_management': optimization.get('training_cost', 0),
                'integration_services': optimization.get('implementation_cost', 0) * 0.4
            }
        elif category == 'quality':
            return {
                'quality_management_software': optimization.get('quality_system_cost', 0) * 0.7,
                'training_and_certification': optimization.get('training_cost', 0),
                'sensors_and_equipment': optimization.get('quality_system_cost', 0) * 0.3
            }
        elif category == 'inventory':
            return {
                'inventory_management_system': optimization.get('system_cost', 0) * 0.8,
                'training_and_setup': optimization.get('training_cost', 0),
                'barcode_rfid_equipment': optimization.get('system_cost', 0) * 0.2
            }
        elif category == 'service':
            return {
                'automation_platform_license': optimization.get('automation_platform_cost', 0),
                'implementation_and_setup': optimization.get('setup_cost', 0) * 0.7,
                'training_and_support': optimization.get('setup_cost', 0) * 0.3
            }
        else:
            return {'implementation': optimization.get('implementation_cost', 0)}