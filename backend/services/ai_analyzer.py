import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

from models.questionnaire import db, QuestionnaireSession, QuestionnaireResponse, QuestionnaireAnalysis

class AIAnalyzer:
    """AI-powered analyzer for questionnaire responses using Claude Sonnet 4."""
    
    def __init__(self):
        self.anthropic_client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Anthropic client if available."""
        try:
            import anthropic
            import os
            
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                self.anthropic_client = anthropic.Anthropic(api_key=api_key)
            else:
                print("Warning: ANTHROPIC_API_KEY not found. AI analysis will use fallback method.")
        except ImportError:
            print("Warning: anthropic package not installed. AI analysis will use fallback method.")
    
    def analyze_session(self, session_id: str) -> Optional[QuestionnaireAnalysis]:
        """Analyze a completed questionnaire session."""
        try:
            # Get session and responses
            session = QuestionnaireSession.query.filter_by(id=session_id).first()
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            responses = QuestionnaireResponse.query.filter_by(session_id=session_id).order_by(QuestionnaireResponse.answered_at).all()
            if not responses:
                raise ValueError(f"No responses found for session {session_id}")
            
            # Prepare response data for analysis
            response_data = self._prepare_response_data(responses)
            
            # Perform AI analysis
            if self.anthropic_client:
                analysis_results = self._analyze_with_claude(response_data)
            else:
                analysis_results = self._analyze_with_fallback(response_data)
            
            # Store analysis results
            analysis = self._store_analysis(session_id, analysis_results)
            
            # Mark text responses as analyzed
            self._mark_text_responses_analyzed(responses, analysis_results)
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing session {session_id}: {e}")
            return None
    
    def _prepare_response_data(self, responses: List[QuestionnaireResponse]) -> Dict[str, Any]:
        """Prepare response data for AI analysis."""
        data = {
            'responses': [],
            'company_profile': {},
            'text_responses': []
        }
        
        for resp in responses:
            response_info = {
                'question_id': resp.question_id,
                'question': resp.question_text,
                'answer': resp.answer,
                'type': resp.answer_type
            }
            data['responses'].append(response_info)
            
            # Extract key profile information
            if resp.question_id == 'START':
                data['company_profile']['product_type'] = resp.answer
            elif resp.question_id in ['VOLUME', 'GENERAL_1']:
                data['company_profile']['production_volume'] = resp.answer
            elif resp.question_id == 'EMPLOYEES':
                data['company_profile']['employee_count'] = resp.answer
            elif resp.question_id == 'AUTOMATION_CURRENT':
                data['company_profile']['automation_level'] = resp.answer
            
            # Collect text responses for detailed analysis
            if resp.answer_type == 'text':
                data['text_responses'].append({
                    'question_id': resp.question_id,
                    'question': resp.question_text,
                    'answer': resp.answer
                })
        
        return data
    
    def _analyze_with_claude(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze responses using Claude Sonnet 4."""
        
        # Prepare the prompt
        prompt = self._build_analysis_prompt(response_data)
        
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse the response
            analysis_text = response.content[0].text
            return self._parse_claude_response(analysis_text)
            
        except Exception as e:
            print(f"Claude API error: {e}")
            return self._analyze_with_fallback(response_data)
    
    def _build_analysis_prompt(self, response_data: Dict[str, Any]) -> str:
        """Build the enhanced analysis prompt for Claude."""
        
        responses_text = "\n".join([
            f"Q: {r['question']}\nA: {r['answer']}\n"
            for r in response_data['responses']
        ])
        
        text_responses_text = "\n".join([
            f"Q: {r['question']}\nA: {r['answer']}\n"
            for r in response_data['text_responses']
        ])
        
        prompt = f"""
You are an expert manufacturing operations consultant and AI implementation specialist. Analyze this comprehensive 12-question business assessment from a manufacturing company to provide detailed, actionable insights for AI and automation implementation.

ALL QUESTIONNAIRE RESPONSES:
{responses_text}

DETAILED TEXT RESPONSES:
{text_responses_text}

Please provide a comprehensive analysis in the following JSON format:

{{
    "company_profile": {{
        "company_type": "Detailed description of company type and products",
        "industry_category": "Specific manufacturing industry (Metal Fabrication, Electronics, etc.)",
        "size_category": "small/medium/large with reasoning",
        "production_complexity": "low/medium/high based on volume and processes",
        "current_maturity": "Manual/Basic/Intermediate/Advanced/Cutting-edge"
    }},
    "operational_assessment": {{
        "production_volume_annual": "Estimated annual units based on daily volume",
        "quality_loss_percentage": "Extracted from defects/rework question",
        "automation_percentage": "Current automation level (0-100%)",
        "customer_service_volume": "Weekly inquiries volume category",
        "improvement_budget_range": "Budget category for investments"
    }},
    "pain_points": [
        "Specific operational challenges extracted from responses",
        "Quality control issues identified",
        "Production efficiency bottlenecks",
        "Labor-related challenges",
        "Supply chain/inventory issues",
        "Customer service pain points"
    ],
    "automation_opportunities": {{
        "labor_optimization": {{
            "potential": "high/medium/low",
            "specific_areas": ["List specific labor automation opportunities"],
            "estimated_savings_percentage": "0-30% range"
        }},
        "quality_control": {{
            "potential": "high/medium/low", 
            "specific_areas": ["List quality automation opportunities"],
            "estimated_defect_reduction": "0-80% range"
        }},
        "inventory_management": {{
            "potential": "high/medium/low",
            "specific_areas": ["List inventory optimization opportunities"],
            "estimated_efficiency_gain": "0-50% range"
        }},
        "customer_service": {{
            "potential": "high/medium/low",
            "specific_areas": ["List service automation opportunities"],
            "estimated_response_improvement": "0-70% range"
        }}
    }},
    "implementation_strategy": {{
        "priority_order": [
            "Ranked list of automation areas by impact and feasibility",
            "Consider budget, current maturity, and pain points"
        ],
        "quick_wins": ["Immediate improvements possible within 3 months"],
        "medium_term": ["Improvements requiring 3-12 months"],
        "long_term": ["Strategic improvements requiring 1+ years"],
        "budget_allocation": {{
            "percentage_for_labor": "0-40%",
            "percentage_for_quality": "0-40%", 
            "percentage_for_inventory": "0-30%",
            "percentage_for_service": "0-20%"
        }}
    }},
    "roi_projections": {{
        "expected_payback_months": "6-36 months based on investments and savings",
        "year_1_roi_percentage": "Estimated first year ROI",
        "total_annual_savings_potential": "Dollar range or percentage of revenue",
        "implementation_risk": "low/medium/high"
    }},
    "confidence_score": 0.90
}}

Focus on:
1. Extracting specific, quantifiable insights from each question
2. Providing detailed automation potential assessments for each area
3. Creating realistic implementation timelines based on budget and complexity
4. Calculating evidence-based ROI projections
5. Prioritizing recommendations based on business impact, feasibility, and budget

Analyze the responses comprehensively and provide actionable, data-driven recommendations. Respond only with valid JSON.
"""
        return prompt
    
    def _parse_claude_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Claude's JSON response."""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                raise ValueError("No JSON found in Claude response")
        except Exception as e:
            print(f"Error parsing Claude response: {e}")
            return self._get_default_analysis()
    
    def _analyze_with_fallback(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced fallback analysis when Claude API is not available."""
        
        # Extract detailed information from all 12 questions
        responses = {r['question_id']: r['answer'] for r in response_data['responses']}
        
        # Analyze company profile
        product_type = responses.get('q1', 'Other Manufacturing')
        production_volume = responses.get('q2', 'Unknown')
        employee_count = responses.get('q3', 'Unknown')
        revenue_range = responses.get('q4', 'Unknown')
        quality_control = responses.get('q6', 'Unknown')
        quality_loss = responses.get('q7', 'Unknown')
        inventory_mgmt = responses.get('q8', 'Unknown')
        automation_level = responses.get('q9', 'Unknown')
        service_volume = responses.get('q10', 'Unknown')
        budget_range = responses.get('q11', 'Unknown')
        
        # Analyze text responses for pain points
        pain_points = []
        opportunities = {}
        
        for text_resp in response_data['text_responses']:
            answer = text_resp['answer'].lower()
            
            # Enhanced pain point extraction
            pain_keywords = {
                'quality': ['defect', 'quality', 'rework', 'scrap', 'inspection'],
                'efficiency': ['slow', 'bottleneck', 'inefficient', 'delay', 'waste'],
                'labor': ['manual', 'labor', 'worker', 'training', 'skill'],
                'cost': ['expensive', 'cost', 'budget', 'profit', 'margin'],
                'inventory': ['inventory', 'stock', 'material', 'supply']
            }
            
            for category, keywords in pain_keywords.items():
                for keyword in keywords:
                    if keyword in answer:
                        pain_points.append(f"{category.title()} challenges: {keyword} issues mentioned")
                        break
        
        # Determine size and complexity
        if any(x in employee_count for x in ['1-10', '11-25']):
            size_category = 'small'
        elif any(x in employee_count for x in ['251-500', 'Over 500']):
            size_category = 'large'
        else:
            size_category = 'medium'
            
        # Determine production complexity
        if 'Over 50,000' in production_volume or 'Over 500' in employee_count:
            complexity = 'high'
        elif any(x in production_volume for x in ['Under 100', '100-500']):
            complexity = 'low'
        else:
            complexity = 'medium'
            
        # Analyze automation opportunities
        labor_potential = 'high' if 'manual' in automation_level.lower() else 'medium'
        quality_potential = 'high' if 'manual' in quality_control.lower() else 'medium'
        inventory_potential = 'high' if 'manual' in inventory_mgmt.lower() else 'medium'
        service_potential = 'medium' if any(x in service_volume for x in ['100-250', 'More than 250']) else 'low'
        
        # Estimate budget allocation
        budget_amounts = {
            'Under $25,000': 25000,
            '$25,000 - $75,000': 50000,
            '$75,000 - $200,000': 137500,
            '$200,000 - $500,000': 350000,
            '$500,000 - $1M': 750000,
            '$1M - $5M': 3000000,
            'Over $5M': 7500000
        }
        
        estimated_budget = budget_amounts.get(budget_range, 200000)
        
        return {
            'company_profile': {
                'company_type': f"{product_type} manufacturer",
                'industry_category': product_type,
                'size_category': size_category,
                'production_complexity': complexity,
                'current_maturity': 'Basic' if 'manual' in automation_level.lower() else 'Intermediate'
            },
            'operational_assessment': {
                'production_volume_annual': self._estimate_annual_volume(production_volume),
                'quality_loss_percentage': self._extract_quality_loss(quality_loss),
                'automation_percentage': self._estimate_automation_percentage(automation_level),
                'customer_service_volume': service_volume,
                'improvement_budget_range': budget_range
            },
            'pain_points': pain_points or ['Manual processes requiring optimization', 'Operational efficiency improvements needed'],
            'automation_opportunities': {
                'labor_optimization': {
                    'potential': labor_potential,
                    'specific_areas': ['Manual task automation', 'Process optimization'],
                    'estimated_savings_percentage': '15-25%'
                },
                'quality_control': {
                    'potential': quality_potential,
                    'specific_areas': ['Automated inspection', 'Quality monitoring'],
                    'estimated_defect_reduction': '30-50%'
                },
                'inventory_management': {
                    'potential': inventory_potential,
                    'specific_areas': ['Inventory tracking', 'Demand forecasting'],
                    'estimated_efficiency_gain': '20-35%'
                },
                'customer_service': {
                    'potential': service_potential,
                    'specific_areas': ['Customer inquiry automation', 'Response optimization'],
                    'estimated_response_improvement': '40-60%'
                }
            },
            'implementation_strategy': {
                'priority_order': ['Labor optimization', 'Quality control', 'Inventory management', 'Customer service'],
                'quick_wins': ['Basic automation tools', 'Process standardization'],
                'medium_term': ['Automated quality systems', 'Inventory optimization'],
                'long_term': ['Advanced AI integration', 'Full process automation'],
                'budget_allocation': {
                    'percentage_for_labor': '35%',
                    'percentage_for_quality': '30%',
                    'percentage_for_inventory': '25%',
                    'percentage_for_service': '10%'
                }
            },
            'roi_projections': {
                'expected_payback_months': '12-18',
                'year_1_roi_percentage': '150-200%',
                'total_annual_savings_potential': f"${int(estimated_budget * 1.5):,} - ${int(estimated_budget * 2.5):,}",
                'implementation_risk': 'medium'
            },
            'confidence_score': 0.75
        }
    
    def _estimate_annual_volume(self, daily_volume: str) -> str:
        """Estimate annual production volume from daily volume."""
        volume_map = {
            'Under 100 units/day': '25,000 units/year',
            '100-500 units/day': '75,000 units/year', 
            '500-2,000 units/day': '375,000 units/year',
            '2,000-10,000 units/day': '1.5M units/year',
            '10,000-50,000 units/day': '7.5M units/year',
            'Over 50,000 units/day': '15M+ units/year'
        }
        return volume_map.get(daily_volume, '250,000 units/year')
    
    def _extract_quality_loss(self, quality_loss: str) -> str:
        """Extract quality loss percentage."""
        return quality_loss if quality_loss != 'Unknown' else '10-20%'
    
    def _estimate_automation_percentage(self, automation_level: str) -> str:
        """Estimate current automation percentage."""
        automation_map = {
            'Fully manual operations': '5%',
            'Basic tools and equipment only': '15%',
            'Some automated machinery': '30%',
            'Moderate automation (30-50% of processes)': '40%',
            'Highly automated (50-80% of processes)': '65%',
            'Nearly fully automated (80%+ of processes)': '85%'
        }
        return automation_map.get(automation_level, '25%')
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """Get default analysis structure."""
        return {
            'company_type': 'Manufacturing company',
            'industry': 'Manufacturing',
            'size_category': 'medium',
            'pain_points': ['Operational challenges identified'],
            'opportunities': ['Improvement opportunities available'],
            'automation_level': 'medium',
            'priority_areas': ['Process optimization'],
            'confidence_score': 0.5
        }
    
    def _store_analysis(self, session_id: str, analysis_results: Dict[str, Any]) -> QuestionnaireAnalysis:
        """Store analysis results in database."""
        
        # Delete existing analysis if any
        QuestionnaireAnalysis.query.filter_by(session_id=session_id).delete()
        
        # Create new analysis record
        analysis = QuestionnaireAnalysis(
            session_id=session_id,
            company_type=analysis_results.get('company_type'),
            industry=analysis_results.get('industry'),
            size_category=analysis_results.get('size_category'),
            automation_level=analysis_results.get('automation_level'),
            confidence_score=analysis_results.get('confidence_score', 0.5)
        )
        
        # Set JSON fields
        analysis.set_pain_points(analysis_results.get('pain_points', []))
        analysis.set_opportunities(analysis_results.get('opportunities', []))
        analysis.set_priority_areas(analysis_results.get('priority_areas', []))
        
        db.session.add(analysis)
        db.session.commit()
        
        return analysis
    
    def _mark_text_responses_analyzed(self, responses: List[QuestionnaireResponse], analysis_results: Dict[str, Any]):
        """Mark text responses as analyzed and store insights."""
        
        for resp in responses:
            if resp.answer_type == 'text':
                resp.ai_analyzed = True
                
                # Store relevant insights for this response
                insights = {
                    'pain_points_mentioned': [],
                    'opportunities_identified': [],
                    'key_themes': []
                }
                
                answer_lower = resp.answer.lower()
                
                # Map pain points to this response
                for pain_point in analysis_results.get('pain_points', []):
                    if any(word in answer_lower for word in pain_point.lower().split()):
                        insights['pain_points_mentioned'].append(pain_point)
                
                # Map opportunities
                for opportunity in analysis_results.get('opportunities', []):
                    if any(word in answer_lower for word in opportunity.lower().split()):
                        insights['opportunities_identified'].append(opportunity)
                
                resp.extracted_insights = json.dumps(insights)
        
        db.session.commit()