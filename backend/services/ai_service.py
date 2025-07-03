import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import re

logger = logging.getLogger(__name__)

@dataclass
class PainPoint:
    """Structured pain point data."""
    category: str
    description: str
    severity: str  # low, medium, high, critical
    frequency: str  # rare, occasional, frequent, constant
    impact_areas: List[str]
    confidence: float

@dataclass
class Recommendation:
    """AI-generated recommendation."""
    title: str
    description: str
    category: str  # automation, process, quality, inventory, etc.
    priority: str  # low, medium, high, critical
    implementation_effort: str  # low, medium, high
    technology_type: str  # software, hardware, training, process
    target_pain_points: List[str]
    estimated_timeline: str
    confidence: float

@dataclass
class FinancialImpact:
    """Financial impact estimation."""
    cost_savings_annual: float
    implementation_cost: float
    roi_percentage: float
    payback_months: int
    revenue_impact: float
    cost_breakdown: Dict[str, float]
    assumptions: List[str]
    confidence: float

class AIService:
    """
    AI Service for manufacturing SME analysis and recommendations.
    Supports both OpenAI and Anthropic APIs with intelligent fallbacks.
    """
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self._initialize_clients()
        
        # Manufacturing-specific knowledge base
        self.manufacturing_categories = {
            'quality_control': ['defects', 'inspection', 'testing', 'standards', 'compliance'],
            'production_efficiency': ['throughput', 'cycle_time', 'bottlenecks', 'scheduling'],
            'inventory_management': ['stock', 'materials', 'storage', 'tracking', 'waste'],
            'maintenance': ['downtime', 'repairs', 'preventive', 'equipment'],
            'labor_productivity': ['training', 'skills', 'efficiency', 'workload'],
            'cost_control': ['overhead', 'expenses', 'budgets', 'margins'],
            'automation': ['manual', 'repetitive', 'robotics', 'digitization'],
            'supply_chain': ['suppliers', 'delivery', 'sourcing', 'logistics']
        }
        
        self.severity_indicators = {
            'critical': ['shutdown', 'stopped', 'failure', 'crisis', 'emergency'],
            'high': ['significant', 'major', 'serious', 'urgent', 'critical'],
            'medium': ['moderate', 'noticeable', 'concerning', 'regular'],
            'low': ['minor', 'occasional', 'slight', 'small']
        }
    
    def _initialize_clients(self):
        """Initialize AI API clients."""
        try:
            # Initialize OpenAI
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                import openai
                self.openai_client = openai.OpenAI(api_key=openai_key)
                logger.info("OpenAI client initialized")
        except ImportError:
            logger.warning("OpenAI package not installed")
        except Exception as e:
            logger.error(f"OpenAI initialization failed: {e}")
        
        try:
            # Initialize Anthropic
            anthropic_key = os.getenv('ANTHROPIC_API_KEY')
            if anthropic_key:
                import anthropic
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
                logger.info("Anthropic client initialized")
        except ImportError:
            logger.warning("Anthropic package not installed")
        except Exception as e:
            logger.error(f"Anthropic initialization failed: {e}")
        
        if not self.openai_client and not self.anthropic_client:
            logger.warning("No AI clients available - using fallback analysis")
    
    def analyze_pain_points(self, text_response: str, context: Dict[str, Any] = None) -> List[PainPoint]:
        """
        Analyze text responses to extract and categorize manufacturing pain points.
        
        Args:
            text_response: Free-text response from questionnaire
            context: Additional context (company size, industry, etc.)
            
        Returns:
            List of structured PainPoint objects
        """
        try:
            if self.anthropic_client:
                return self._analyze_pain_points_anthropic(text_response, context)
            elif self.openai_client:
                return self._analyze_pain_points_openai(text_response, context)
            else:
                return self._analyze_pain_points_fallback(text_response, context)
        except Exception as e:
            logger.error(f"Pain point analysis failed: {e}")
            return self._analyze_pain_points_fallback(text_response, context)
    
    def _analyze_pain_points_anthropic(self, text_response: str, context: Dict[str, Any]) -> List[PainPoint]:
        """Analyze pain points using Anthropic Claude."""
        prompt = self._build_pain_point_prompt(text_response, context)
        
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1500,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            analysis_text = response.content[0].text
            return self._parse_pain_points_response(analysis_text)
            
        except Exception as e:
            logger.error(f"Anthropic pain point analysis failed: {e}")
            return self._analyze_pain_points_fallback(text_response, context)
    
    def _analyze_pain_points_openai(self, text_response: str, context: Dict[str, Any]) -> List[PainPoint]:
        """Analyze pain points using OpenAI GPT."""
        prompt = self._build_pain_point_prompt(text_response, context)
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content
            return self._parse_pain_points_response(analysis_text)
            
        except Exception as e:
            logger.error(f"OpenAI pain point analysis failed: {e}")
            return self._analyze_pain_points_fallback(text_response, context)
    
    def _build_pain_point_prompt(self, text_response: str, context: Dict[str, Any]) -> str:
        """Build optimized prompt for manufacturing pain point analysis."""
        context_str = ""
        if context:
            context_str = f"""
COMPANY CONTEXT:
- Industry: {context.get('industry', 'Manufacturing')}
- Size: {context.get('employee_count', 'Unknown')} employees
- Product Type: {context.get('product_type', 'Unknown')}
- Production Volume: {context.get('production_volume', 'Unknown')}
- Current Automation: {context.get('automation_level', 'Unknown')}
"""
        
        return f"""
You are an expert manufacturing consultant analyzing operational challenges for small to medium manufacturing enterprises (SMEs).

{context_str}

MANUFACTURING RESPONSE TO ANALYZE:
"{text_response}"

Extract and categorize ALL pain points mentioned. For each pain point, provide:

1. CATEGORY (one of: quality_control, production_efficiency, inventory_management, maintenance, labor_productivity, cost_control, automation, supply_chain)
2. DESCRIPTION (clear, specific description)
3. SEVERITY (critical, high, medium, low)
4. FREQUENCY (constant, frequent, occasional, rare)
5. IMPACT_AREAS (list of business areas affected)
6. CONFIDENCE (0.0-1.0 score)

Manufacturing-specific focus areas:
- Quality control issues (defects, inspection, compliance)
- Production bottlenecks and efficiency
- Inventory and material management
- Equipment maintenance and downtime
- Labor and skill challenges
- Cost control and margins
- Manual processes ripe for automation
- Supply chain and vendor issues

Respond in this JSON format:
{
  "pain_points": [
    {
      "category": "quality_control",
      "description": "Inconsistent product quality due to manual inspection",
      "severity": "high",
      "frequency": "frequent",
      "impact_areas": ["customer satisfaction", "rework costs", "delivery delays"],
      "confidence": 0.9
    }
  ]
}

Focus on actionable, specific pain points that manufacturing SMEs commonly face.
"""
    
    def _parse_pain_points_response(self, response_text: str) -> List[PainPoint]:
        """Parse AI response into PainPoint objects."""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                pain_points = []
                
                for pp_data in data.get('pain_points', []):
                    pain_point = PainPoint(
                        category=pp_data.get('category', 'unknown'),
                        description=pp_data.get('description', ''),
                        severity=pp_data.get('severity', 'medium'),
                        frequency=pp_data.get('frequency', 'occasional'),
                        impact_areas=pp_data.get('impact_areas', []),
                        confidence=float(pp_data.get('confidence', 0.5))
                    )
                    pain_points.append(pain_point)
                
                return pain_points
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            logger.error(f"Failed to parse pain points response: {e}")
            return []
    
    def _analyze_pain_points_fallback(self, text_response: str, context: Dict[str, Any]) -> List[PainPoint]:
        """Fallback pain point analysis using keyword matching."""
        pain_points = []
        text_lower = text_response.lower()
        
        # Analyze each manufacturing category
        for category, keywords in self.manufacturing_categories.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Determine severity based on indicators
                    severity = 'medium'
                    for sev_level, indicators in self.severity_indicators.items():
                        if any(indicator in text_lower for indicator in indicators):
                            severity = sev_level
                            break
                    
                    # Extract surrounding context
                    sentences = text_response.split('.')
                    relevant_sentences = [s for s in sentences if keyword in s.lower()]
                    description = relevant_sentences[0].strip() if relevant_sentences else f"Issues related to {keyword}"
                    
                    pain_point = PainPoint(
                        category=category,
                        description=description,
                        severity=severity,
                        frequency='frequent' if severity in ['high', 'critical'] else 'occasional',
                        impact_areas=[category.replace('_', ' ')],
                        confidence=0.6
                    )
                    pain_points.append(pain_point)
                    break  # Only one pain point per category in fallback
        
        return pain_points
    
    def generate_recommendations(self, company_data: Dict[str, Any]) -> List[Recommendation]:
        """
        Generate manufacturing-specific AI automation recommendations.
        
        Args:
            company_data: Combined P&L and questionnaire data
            
        Returns:
            List of prioritized Recommendation objects
        """
        try:
            if self.anthropic_client:
                return self._generate_recommendations_anthropic(company_data)
            elif self.openai_client:
                return self._generate_recommendations_openai(company_data)
            else:
                return self._generate_recommendations_fallback(company_data)
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return self._generate_recommendations_fallback(company_data)
    
    def _generate_recommendations_anthropic(self, company_data: Dict[str, Any]) -> List[Recommendation]:
        """Generate recommendations using Anthropic Claude."""
        prompt = self._build_recommendation_prompt(company_data)
        
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                temperature=0.4,
                messages=[{"role": "user", "content": prompt}]
            )
            
            recommendations_text = response.content[0].text
            return self._parse_recommendations_response(recommendations_text)
            
        except Exception as e:
            logger.error(f"Anthropic recommendations failed: {e}")
            return self._generate_recommendations_fallback(company_data)
    
    def _generate_recommendations_openai(self, company_data: Dict[str, Any]) -> List[Recommendation]:
        """Generate recommendations using OpenAI GPT."""
        prompt = self._build_recommendation_prompt(company_data)
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.4
            )
            
            recommendations_text = response.choices[0].message.content
            return self._parse_recommendations_response(recommendations_text)
            
        except Exception as e:
            logger.error(f"OpenAI recommendations failed: {e}")
            return self._generate_recommendations_fallback(company_data)
    
    def _build_recommendation_prompt(self, company_data: Dict[str, Any]) -> str:
        """Build optimized prompt for manufacturing recommendations."""
        
        # Extract key financial metrics
        financials = company_data.get('financial_data', {})
        revenue = financials.get('revenue', 0)
        labor_costs = financials.get('labor_costs', 0)
        overhead = financials.get('overhead_costs', 0)
        
        # Extract pain points
        pain_points = company_data.get('pain_points', [])
        pain_points_str = "\n".join([f"- {pp.description} (Category: {pp.category}, Severity: {pp.severity})" 
                                   for pp in pain_points]) if pain_points else "No specific pain points identified"
        
        # Extract company profile
        profile = company_data.get('company_profile', {})
        
        return f"""
You are an expert manufacturing automation consultant specializing in SME digital transformation.

COMPANY PROFILE:
- Industry: {profile.get('industry', 'Manufacturing')}
- Product Type: {profile.get('product_type', 'Unknown')}
- Size: {profile.get('employee_count', 'Unknown')} employees
- Production Volume: {profile.get('production_volume', 'Unknown')}
- Current Automation Level: {profile.get('automation_level', 'Unknown')}

FINANCIAL DATA:
- Annual Revenue: ${revenue:,.2f}
- Labor Costs: ${labor_costs:,.2f} ({labor_costs/revenue*100:.1f}% of revenue)
- Overhead Costs: ${overhead:,.2f} ({overhead/revenue*100:.1f}% of revenue)

IDENTIFIED PAIN POINTS:
{pain_points_str}

Generate 3-5 specific, actionable AI/automation recommendations tailored to this manufacturing SME. Each recommendation should:

1. Address specific pain points identified
2. Be appropriate for company size and budget
3. Focus on proven manufacturing technologies
4. Provide clear implementation pathway
5. Consider SME resource constraints

For each recommendation, provide:
- TITLE: Clear, specific recommendation name
- DESCRIPTION: Detailed explanation of solution
- CATEGORY: automation/process/quality/inventory/maintenance/cost_control
- PRIORITY: critical/high/medium/low
- IMPLEMENTATION_EFFORT: low/medium/high
- TECHNOLOGY_TYPE: software/hardware/training/process
- TARGET_PAIN_POINTS: Which pain points this addresses
- ESTIMATED_TIMELINE: Implementation timeframe
- CONFIDENCE: 0.0-1.0 confidence score

Focus on:
- Manufacturing Execution Systems (MES)
- Quality management software
- Inventory optimization tools
- Predictive maintenance
- Process automation
- Digital workflows
- IoT sensors and monitoring
- Data analytics and reporting

Respond in JSON format:
{
  "recommendations": [
    {
      "title": "Implement Digital Quality Management System",
      "description": "Deploy cloud-based QMS with real-time defect tracking...",
      "category": "quality",
      "priority": "high",
      "implementation_effort": "medium",
      "technology_type": "software",
      "target_pain_points": ["quality_control", "manual_inspection"],
      "estimated_timeline": "3-6 months",
      "confidence": 0.85
    }
  ]
}
"""
    
    def _parse_recommendations_response(self, response_text: str) -> List[Recommendation]:
        """Parse AI response into Recommendation objects."""
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                recommendations = []
                
                for rec_data in data.get('recommendations', []):
                    recommendation = Recommendation(
                        title=rec_data.get('title', ''),
                        description=rec_data.get('description', ''),
                        category=rec_data.get('category', 'automation'),
                        priority=rec_data.get('priority', 'medium'),
                        implementation_effort=rec_data.get('implementation_effort', 'medium'),
                        technology_type=rec_data.get('technology_type', 'software'),
                        target_pain_points=rec_data.get('target_pain_points', []),
                        estimated_timeline=rec_data.get('estimated_timeline', '6-12 months'),
                        confidence=float(rec_data.get('confidence', 0.7))
                    )
                    recommendations.append(recommendation)
                
                return recommendations
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            logger.error(f"Failed to parse recommendations response: {e}")
            return []
    
    def _generate_recommendations_fallback(self, company_data: Dict[str, Any]) -> List[Recommendation]:
        """Fallback recommendation generation using templates."""
        recommendations = []
        
        # Extract key info
        pain_points = company_data.get('pain_points', [])
        financials = company_data.get('financial_data', {})
        revenue = financials.get('revenue', 0)
        
        # Template recommendations based on common SME needs
        if any(pp.category == 'quality_control' for pp in pain_points):
            recommendations.append(Recommendation(
                title="Digital Quality Management System",
                description="Implement cloud-based quality management software to automate inspections and track defects in real-time.",
                category="quality",
                priority="high",
                implementation_effort="medium",
                technology_type="software",
                target_pain_points=["quality_control"],
                estimated_timeline="3-6 months",
                confidence=0.7
            ))
        
        if any(pp.category == 'inventory_management' for pp in pain_points):
            recommendations.append(Recommendation(
                title="Inventory Optimization Software",
                description="Deploy automated inventory tracking with barcode/RFID scanning and real-time stock level monitoring.",
                category="inventory",
                priority="high",
                implementation_effort="medium",
                technology_type="software",
                target_pain_points=["inventory_management"],
                estimated_timeline="2-4 months",
                confidence=0.7
            ))
        
        if any(pp.category == 'production_efficiency' for pp in pain_points):
            recommendations.append(Recommendation(
                title="Production Scheduling Software",
                description="Implement digital production scheduling to optimize workflow and reduce bottlenecks.",
                category="automation",
                priority="medium",
                implementation_effort="medium",
                technology_type="software",
                target_pain_points=["production_efficiency"],
                estimated_timeline="4-8 months",
                confidence=0.6
            ))
        
        return recommendations[:3]  # Return top 3
    
    def estimate_impact(self, recommendation: Recommendation, company_data: Dict[str, Any]) -> FinancialImpact:
        """
        Calculate potential cost savings and ROI for a recommendation.
        
        Args:
            recommendation: The recommendation to analyze
            company_data: Company financial and operational data
            
        Returns:
            FinancialImpact with detailed financial projections
        """
        try:
            if self.anthropic_client:
                return self._estimate_impact_anthropic(recommendation, company_data)
            elif self.openai_client:
                return self._estimate_impact_openai(recommendation, company_data)
            else:
                return self._estimate_impact_fallback(recommendation, company_data)
        except Exception as e:
            logger.error(f"Impact estimation failed: {e}")
            return self._estimate_impact_fallback(recommendation, company_data)
    
    def _estimate_impact_anthropic(self, recommendation: Recommendation, company_data: Dict[str, Any]) -> FinancialImpact:
        """Estimate financial impact using Anthropic Claude."""
        prompt = self._build_impact_prompt(recommendation, company_data)
        
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}]
            )
            
            impact_text = response.content[0].text
            return self._parse_impact_response(impact_text)
            
        except Exception as e:
            logger.error(f"Anthropic impact estimation failed: {e}")
            return self._estimate_impact_fallback(recommendation, company_data)
    
    def _estimate_impact_openai(self, recommendation: Recommendation, company_data: Dict[str, Any]) -> FinancialImpact:
        """Estimate financial impact using OpenAI GPT."""
        prompt = self._build_impact_prompt(recommendation, company_data)
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.2
            )
            
            impact_text = response.choices[0].message.content
            return self._parse_impact_response(impact_text)
            
        except Exception as e:
            logger.error(f"OpenAI impact estimation failed: {e}")
            return self._estimate_impact_fallback(recommendation, company_data)
    
    def _build_impact_prompt(self, recommendation: Recommendation, company_data: Dict[str, Any]) -> str:
        """Build prompt for financial impact estimation."""
        financials = company_data.get('financial_data', {})
        revenue = financials.get('revenue', 0)
        labor_costs = financials.get('labor_costs', 0)
        overhead = financials.get('overhead_costs', 0)
        
        return f"""
You are a manufacturing finance expert calculating ROI for automation investments.

RECOMMENDATION TO ANALYZE:
Title: {recommendation.title}
Description: {recommendation.description}
Category: {recommendation.category}
Implementation Effort: {recommendation.implementation_effort}

COMPANY FINANCIAL DATA:
- Annual Revenue: ${revenue:,.2f}
- Annual Labor Costs: ${labor_costs:,.2f}
- Annual Overhead Costs: ${overhead:,.2f}

Calculate realistic financial impact for this SME manufacturing company:

1. COST_SAVINGS_ANNUAL: Annual cost reductions
2. IMPLEMENTATION_COST: One-time implementation cost
3. ROI_PERCENTAGE: Return on investment percentage
4. PAYBACK_MONTHS: Months to recover investment
5. REVENUE_IMPACT: Potential revenue increase
6. COST_BREAKDOWN: Detailed cost categories
7. ASSUMPTIONS: Key assumptions made
8. CONFIDENCE: 0.0-1.0 confidence in estimates

Focus on realistic SME manufacturing scenarios:
- Quality improvements reducing rework/scrap
- Labor efficiency gains
- Inventory optimization
- Reduced downtime
- Process automation savings

Respond in JSON format:
{
  "cost_savings_annual": 45000,
  "implementation_cost": 25000,
  "roi_percentage": 80,
  "payback_months": 18,
  "revenue_impact": 15000,
  "cost_breakdown": {
    "software_license": 8000,
    "implementation_services": 12000,
    "training": 3000,
    "hardware": 2000
  },
  "assumptions": [
    "20% reduction in quality-related rework",
    "10% improvement in labor efficiency"
  ],
  "confidence": 0.75
}
"""
    
    def _parse_impact_response(self, response_text: str) -> FinancialImpact:
        """Parse AI response into FinancialImpact object."""
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                
                return FinancialImpact(
                    cost_savings_annual=float(data.get('cost_savings_annual', 0)),
                    implementation_cost=float(data.get('implementation_cost', 0)),
                    roi_percentage=float(data.get('roi_percentage', 0)),
                    payback_months=int(data.get('payback_months', 12)),
                    revenue_impact=float(data.get('revenue_impact', 0)),
                    cost_breakdown=data.get('cost_breakdown', {}),
                    assumptions=data.get('assumptions', []),
                    confidence=float(data.get('confidence', 0.5))
                )
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            logger.error(f"Failed to parse impact response: {e}")
            return self._get_default_impact()
    
    def _estimate_impact_fallback(self, recommendation: Recommendation, company_data: Dict[str, Any]) -> FinancialImpact:
        """Fallback impact estimation using industry averages."""
        financials = company_data.get('financial_data', {})
        revenue = financials.get('revenue', 100000)
        labor_costs = financials.get('labor_costs', 50000)
        
        # Conservative estimates based on category
        impact_multipliers = {
            'quality': {'savings_pct': 0.05, 'impl_cost_ratio': 0.15},
            'automation': {'savings_pct': 0.08, 'impl_cost_ratio': 0.25},
            'inventory': {'savings_pct': 0.03, 'impl_cost_ratio': 0.10},
            'process': {'savings_pct': 0.06, 'impl_cost_ratio': 0.20}
        }
        
        multiplier = impact_multipliers.get(recommendation.category, impact_multipliers['automation'])
        
        savings = revenue * multiplier['savings_pct']
        impl_cost = revenue * multiplier['impl_cost_ratio']
        roi = (savings / impl_cost) * 100 if impl_cost > 0 else 0
        payback = int((impl_cost / savings) * 12) if savings > 0 else 24
        
        return FinancialImpact(
            cost_savings_annual=savings,
            implementation_cost=impl_cost,
            roi_percentage=roi,
            payback_months=payback,
            revenue_impact=savings * 0.3,  # 30% revenue impact
            cost_breakdown={
                'software_license': impl_cost * 0.4,
                'implementation_services': impl_cost * 0.4,
                'training': impl_cost * 0.2
            },
            assumptions=[
                f"{multiplier['savings_pct']*100:.1f}% cost reduction from {recommendation.category} improvements",
                "Based on industry averages for similar implementations"
            ],
            confidence=0.6
        )
    
    def _get_default_impact(self) -> FinancialImpact:
        """Get default financial impact when parsing fails."""
        return FinancialImpact(
            cost_savings_annual=25000,
            implementation_cost=15000,
            roi_percentage=67,
            payback_months=18,
            revenue_impact=10000,
            cost_breakdown={'software': 10000, 'services': 5000},
            assumptions=["Conservative industry estimates"],
            confidence=0.5
        )
    
    def analyze_comprehensive(self, questionnaire_data: Dict[str, Any], financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive analysis combining pain points, recommendations, and financial impact.
        
        Args:
            questionnaire_data: Responses from intelligent questionnaire
            financial_data: P&L data from file upload
            
        Returns:
            Complete analysis with pain points, recommendations, and ROI estimates
        """
        try:
            # Combine data
            company_data = {
                'company_profile': questionnaire_data.get('company_profile', {}),
                'financial_data': financial_data,
                'questionnaire_responses': questionnaire_data.get('responses', [])
            }
            
            # Extract pain points from text responses
            pain_points = []
            for response in questionnaire_data.get('responses', []):
                if response.get('answer_type') == 'text':
                    pain_points.extend(self.analyze_pain_points(
                        response['answer'], 
                        company_data['company_profile']
                    ))
            
            company_data['pain_points'] = pain_points
            
            # Generate recommendations
            recommendations = self.generate_recommendations(company_data)
            
            # Calculate financial impact for each recommendation
            recommendations_with_impact = []
            for rec in recommendations:
                impact = self.estimate_impact(rec, company_data)
                recommendations_with_impact.append({
                    'recommendation': rec,
                    'financial_impact': impact
                })
            
            # Sort by ROI
            recommendations_with_impact.sort(
                key=lambda x: x['financial_impact'].roi_percentage, 
                reverse=True
            )
            
            return {
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'company_profile': company_data['company_profile'],
                'pain_points': [self._pain_point_to_dict(pp) for pp in pain_points],
                'recommendations': [self._recommendation_with_impact_to_dict(rec_impact) 
                                 for rec_impact in recommendations_with_impact],
                'summary': {
                    'total_pain_points': len(pain_points),
                    'total_recommendations': len(recommendations),
                    'best_roi': recommendations_with_impact[0]['financial_impact'].roi_percentage if recommendations_with_impact else 0,
                    'total_potential_savings': sum(rec['financial_impact'].cost_savings_annual 
                                                 for rec in recommendations_with_impact)
                }
            }
            
        except Exception as e:
            logger.error(f"Comprehensive analysis failed: {e}")
            return {
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'error': str(e),
                'company_profile': {},
                'pain_points': [],
                'recommendations': [],
                'summary': {}
            }
    
    def _pain_point_to_dict(self, pain_point: PainPoint) -> Dict[str, Any]:
        """Convert PainPoint to dictionary."""
        return {
            'category': pain_point.category,
            'description': pain_point.description,
            'severity': pain_point.severity,
            'frequency': pain_point.frequency,
            'impact_areas': pain_point.impact_areas,
            'confidence': pain_point.confidence
        }
    
    def _recommendation_to_dict(self, recommendation: Recommendation) -> Dict[str, Any]:
        """Convert Recommendation to dictionary."""
        return {
            'title': recommendation.title,
            'description': recommendation.description,
            'category': recommendation.category,
            'priority': recommendation.priority,
            'implementation_effort': recommendation.implementation_effort,
            'technology_type': recommendation.technology_type,
            'target_pain_points': recommendation.target_pain_points,
            'estimated_timeline': recommendation.estimated_timeline,
            'confidence': recommendation.confidence
        }
    
    def _financial_impact_to_dict(self, impact: FinancialImpact) -> Dict[str, Any]:
        """Convert FinancialImpact to dictionary."""
        return {
            'cost_savings_annual': impact.cost_savings_annual,
            'implementation_cost': impact.implementation_cost,
            'roi_percentage': impact.roi_percentage,
            'payback_months': impact.payback_months,
            'revenue_impact': impact.revenue_impact,
            'cost_breakdown': impact.cost_breakdown,
            'assumptions': impact.assumptions,
            'confidence': impact.confidence
        }
    
    def _recommendation_with_impact_to_dict(self, rec_impact: Dict[str, Any]) -> Dict[str, Any]:
        """Convert recommendation with impact to dictionary."""
        return {
            'recommendation': self._recommendation_to_dict(rec_impact['recommendation']),
            'financial_impact': self._financial_impact_to_dict(rec_impact['financial_impact'])
        }