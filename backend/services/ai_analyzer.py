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
        """Build the analysis prompt for Claude."""
        
        responses_text = "\n".join([
            f"Q: {r['question']}\nA: {r['answer']}\n"
            for r in response_data['responses']
        ])
        
        text_responses_text = "\n".join([
            f"Q: {r['question']}\nA: {r['answer']}\n"
            for r in response_data['text_responses']
        ])
        
        prompt = f"""
You are an expert business analyst specializing in manufacturing operations. Analyze the following questionnaire responses from a manufacturing company and provide insights.

ALL QUESTIONNAIRE RESPONSES:
{responses_text}

DETAILED TEXT RESPONSES:
{text_responses_text}

Please provide a structured analysis in the following JSON format:

{{
    "company_type": "Brief description of the company type based on products/processes",
    "industry": "Manufacturing industry category",
    "size_category": "small/medium/large based on employees and volume",
    "pain_points": [
        "List of specific pain points extracted from responses",
        "Focus on operational challenges mentioned"
    ],
    "opportunities": [
        "List of improvement opportunities based on pain points",
        "Automation and efficiency suggestions"
    ],
    "automation_level": "current/low/medium/high based on responses",
    "priority_areas": [
        "Top 3-5 priority areas for improvement",
        "Based on pain points and business impact"
    ],
    "confidence_score": 0.85
}}

Focus on:
1. Extracting specific operational pain points from free-text responses
2. Identifying automation and efficiency opportunities
3. Prioritizing areas based on business impact and feasibility
4. Providing actionable insights for manufacturing improvement

Respond only with valid JSON.
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
        """Fallback analysis when Claude API is not available."""
        
        # Extract basic company information
        profile = response_data['company_profile']
        
        # Analyze text responses for keywords
        pain_points = []
        opportunities = []
        
        for text_resp in response_data['text_responses']:
            answer = text_resp['answer'].lower()
            
            # Extract pain points using keyword matching
            pain_keywords = [
                'challenge', 'problem', 'issue', 'difficult', 'slow', 'manual',
                'inefficient', 'costly', 'time-consuming', 'error', 'delay',
                'bottleneck', 'shortage', 'quality', 'defect', 'waste'
            ]
            
            for keyword in pain_keywords:
                if keyword in answer:
                    pain_points.append(f"Issues related to {keyword} mentioned in response")
                    break
            
            # Extract opportunities
            if 'automat' in answer:
                opportunities.append("Automation opportunities identified")
            if 'efficienc' in answer:
                opportunities.append("Efficiency improvement potential")
            if 'quality' in answer:
                opportunities.append("Quality control enhancement needed")
        
        # Determine size category
        employee_count = profile.get('employee_count', '')
        if '1-10' in employee_count:
            size_category = 'small'
        elif '200+' in employee_count:
            size_category = 'large'
        else:
            size_category = 'medium'
        
        # Determine automation level
        automation_current = profile.get('automation_level', '').lower()
        if 'fully manual' in automation_current:
            automation_level = 'low'
        elif 'highly automated' in automation_current or 'fully automated' in automation_current:
            automation_level = 'high'
        else:
            automation_level = 'medium'
        
        return {
            'company_type': f"{profile.get('product_type', 'Manufacturing')} manufacturer",
            'industry': 'Manufacturing',
            'size_category': size_category,
            'pain_points': pain_points or ['Manual processes', 'Operational inefficiencies'],
            'opportunities': opportunities or ['Process automation', 'Efficiency improvements'],
            'automation_level': automation_level,
            'priority_areas': ['Process optimization', 'Quality control', 'Cost reduction'],
            'confidence_score': 0.6
        }
    
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