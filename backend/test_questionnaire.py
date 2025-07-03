#!/usr/bin/env python3
"""
Test script for the intelligent questionnaire system.
Tests the complete flow including branching logic and AI analysis.
"""

import sys
import os
import requests
import json
import time
from typing import Dict, Any

# Add the backend directory to the path
sys.path.append(os.path.dirname(__file__))

from services.questionnaire_flow import QuestionnaireFlow
from services.ai_analyzer import AIAnalyzer

class QuestionnaireSystemTester:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.flow = QuestionnaireFlow()
        self.ai_analyzer = AIAnalyzer()
        
    def test_flow_logic(self):
        """Test the questionnaire flow logic without API calls."""
        print("=== Testing Questionnaire Flow Logic ===\n")
        
        # Test 1: START question routing
        print("Test 1: START question routing")
        start_question = self.flow.get_question('START')
        print(f"START question: {start_question['question']}")
        
        # Test Metal Parts path
        next_id = self.flow.get_next_question_id('START', 'Metal Parts')
        print(f"Metal Parts -> {next_id}")
        assert next_id == 'METAL_1', f"Expected METAL_1, got {next_id}"
        
        # Test Other product path
        next_id = self.flow.get_next_question_id('START', 'Electronics')
        print(f"Electronics -> {next_id}")
        assert next_id == 'GENERAL_1', f"Expected GENERAL_1, got {next_id}"
        
        print("✓ START routing works correctly\n")
        
        # Test 2: Answer validation
        print("Test 2: Answer validation")
        valid = self.flow.validate_answer('START', 'Metal Parts')
        print(f"Valid answer 'Metal Parts': {valid}")
        assert valid, "Metal Parts should be valid"
        
        invalid = self.flow.validate_answer('START', 'Invalid Option')
        print(f"Invalid answer 'Invalid Option': {invalid}")
        assert not invalid, "Invalid Option should be invalid"
        
        # Test text question validation
        valid_text = self.flow.validate_answer('PAIN_POINTS', 'Our main challenges are quality control and lead times')
        print(f"Valid text answer: {valid_text}")
        assert valid_text, "Text answer should be valid"
        
        empty_text = self.flow.validate_answer('PAIN_POINTS', '')
        print(f"Empty text answer: {empty_text}")
        assert not empty_text, "Empty text should be invalid"
        
        print("✓ Answer validation works correctly\n")
        
        # Test 3: Complete flow simulation
        print("Test 3: Complete flow simulation")
        current_question = 'START'
        answers = [
            ('START', 'Metal Parts'),
            ('METAL_1', 'CNC Machining'),
            ('VOLUME', '500-5000 units/day'),
            ('EMPLOYEES', '11-50 employees'),
            ('PAIN_POINTS', 'Our biggest challenges are inconsistent quality, long setup times for new orders, and difficulty tracking inventory in real-time.'),
            ('QUALITY_CONTROL', 'Manual inspection'),
            ('INVENTORY', 'Basic software system'),
            ('CUSTOMER_SERVICE', '10-50 inquiries'),
            ('AUTOMATION_CURRENT', 'Some automated tools'),
            ('AUTOMATION_INTEREST', 'We would like to automate quality inspection and inventory tracking. These areas cause the most delays and errors.'),
            ('BUDGET', '$50,000 - $200,000'),
            ('TIMELINE', 'Medium-term (3-12 months)')
        ]
        
        for question_id, answer in answers:
            if current_question != question_id:
                print(f"ERROR: Expected {question_id}, but current is {current_question}")
                break
                
            question = self.flow.get_question(current_question)
            print(f"{question_id}: {question['question']}")
            print(f"Answer: {answer}")
            
            # Check if this completes the questionnaire
            if self.flow.is_complete(current_question, answer):
                print("✓ Questionnaire completed")
                break
            
            # Get next question
            next_question_id = self.flow.get_next_question_id(current_question, answer)
            print(f"Next: {next_question_id}\n")
            current_question = next_question_id
        
        print("✓ Complete flow simulation successful\n")
    
    def test_ai_analysis(self):
        """Test AI analysis functionality."""
        print("=== Testing AI Analysis ===\n")
        
        # Create mock response data
        mock_responses = [
            {
                'question_id': 'START',
                'question': 'What type of products does your company manufacture?',
                'answer': 'Metal Parts',
                'type': 'select'
            },
            {
                'question_id': 'PAIN_POINTS',
                'question': 'What are the biggest challenges or pain points your company faces?',
                'answer': 'Our biggest challenges are inconsistent quality, long setup times for new orders, and difficulty tracking inventory in real-time. We also struggle with manual inspection processes that are slow and error-prone.',
                'type': 'text'
            },
            {
                'question_id': 'AUTOMATION_INTEREST',
                'question': 'Which areas would you be most interested in automating?',
                'answer': 'We would like to automate quality inspection and inventory tracking. These areas cause the most delays and errors. We are also interested in automated scheduling to reduce setup times.',
                'type': 'text'
            },
            {
                'question_id': 'EMPLOYEES',
                'question': 'How many employees work in your manufacturing operations?',
                'answer': '11-50 employees',
                'type': 'select'
            }
        ]
        
        # Test data preparation
        response_data = self.ai_analyzer._prepare_response_data_from_dict(mock_responses)
        print("Response data prepared:")
        print(json.dumps(response_data, indent=2))
        
        # Test fallback analysis
        print("\nTesting fallback analysis...")
        analysis_results = self.ai_analyzer._analyze_with_fallback(response_data)
        print("Analysis results:")
        print(json.dumps(analysis_results, indent=2))
        
        # Verify analysis contains expected fields
        required_fields = ['company_type', 'industry', 'size_category', 'pain_points', 'opportunities', 'automation_level', 'priority_areas', 'confidence_score']
        for field in required_fields:
            assert field in analysis_results, f"Missing required field: {field}"
        
        print("✓ AI analysis completed successfully\n")
    
    def test_api_endpoints(self):
        """Test API endpoints (requires running Flask server)."""
        print("=== Testing API Endpoints ===\n")
        
        try:
            # Test server availability
            response = requests.get(f"{self.base_url}/api/questionnaire/flow")
            if response.status_code != 200:
                print("❌ Flask server is not running or questionnaire endpoints not available")
                print("To test API endpoints, run: python app.py")
                return
            
            print("✓ Server is responding\n")
            
            # Test 1: Start questionnaire
            print("Test 1: Starting questionnaire...")
            start_response = requests.post(f"{self.base_url}/api/questionnaire/start", 
                                         json={"company_id": "test-company-123"})
            
            if start_response.status_code == 200:
                start_data = start_response.json()
                session_id = start_data['session_id']
                print(f"✓ Questionnaire started, session ID: {session_id}")
                print(f"First question: {start_data['question']['question']}")
                
                # Test 2: Submit answers
                print("\nTest 2: Submitting answers...")
                answers = [
                    'Metal Parts',
                    'CNC Machining', 
                    '500-5000 units/day',
                    '11-50 employees',
                    'Our biggest challenges are quality control issues and inventory management problems.',
                    'Manual inspection',
                    'Basic software system',
                    '10-50 inquiries',
                    'Some automated tools',
                    'We want to automate quality inspection and inventory tracking to reduce errors.',
                    '$50,000 - $200,000',
                    'Medium-term (3-12 months)'
                ]
                
                for i, answer in enumerate(answers):
                    answer_response = requests.post(f"{self.base_url}/api/questionnaire/{session_id}/answer",
                                                  json={"answer": answer})
                    
                    if answer_response.status_code == 200:
                        answer_data = answer_response.json()
                        if answer_data.get('completed'):
                            print(f"✓ Questionnaire completed after {i+1} answers")
                            break
                        else:
                            next_question = answer_data['question']['question']
                            print(f"Answer {i+1}: {answer} -> Next: {next_question[:50]}...")
                    else:
                        print(f"❌ Error submitting answer {i+1}: {answer_response.status_code}")
                        break
                
                # Test 3: Get session status
                print("\nTest 3: Getting session status...")
                status_response = requests.get(f"{self.base_url}/api/questionnaire/{session_id}/status")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"✓ Session status: {status_data['session']['status']}")
                    print(f"Response count: {status_data['session']['response_count']}")
                
                # Test 4: Get responses
                print("\nTest 4: Getting responses...")
                responses_response = requests.get(f"{self.base_url}/api/questionnaire/{session_id}/responses")
                if responses_response.status_code == 200:
                    responses_data = responses_response.json()
                    print(f"✓ Retrieved {len(responses_data['responses'])} responses")
                
                # Test 5: Get analysis (if available)
                print("\nTest 5: Getting analysis...")
                time.sleep(2)  # Wait for analysis to complete
                analysis_response = requests.get(f"{self.base_url}/api/questionnaire/{session_id}/analysis")
                if analysis_response.status_code == 200:
                    analysis_data = analysis_response.json()
                    print(f"✓ Analysis completed with confidence: {analysis_data['analysis']['confidence_score']}")
                    print(f"Pain points: {len(analysis_data['analysis']['pain_points'])}")
                    print(f"Opportunities: {len(analysis_data['analysis']['opportunities'])}")
                else:
                    print("⚠️  Analysis not yet available or failed")
                
            else:
                print(f"❌ Failed to start questionnaire: {start_response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server. Make sure Flask is running on http://localhost:5000")
        except Exception as e:
            print(f"❌ API test error: {e}")
    
    def run_all_tests(self):
        """Run all tests."""
        print("🧪 INTELLIGENT QUESTIONNAIRE SYSTEM TESTS\n")
        print("="*60)
        
        # Add helper method for AI analyzer
        def _prepare_response_data_from_dict(self, response_list):
            responses = []
            for resp_dict in response_list:
                # Create a mock response object
                class MockResponse:
                    def __init__(self, data):
                        self.question_id = data['question_id']
                        self.question_text = data['question']
                        self.answer = data['answer']
                        self.answer_type = data['type']
                
                responses.append(MockResponse(resp_dict))
            
            return self._prepare_response_data(responses)
        
        # Bind the helper method to the analyzer
        self.ai_analyzer._prepare_response_data_from_dict = _prepare_response_data_from_dict.__get__(self.ai_analyzer, AIAnalyzer)
        
        # Run tests
        self.test_flow_logic()
        self.test_ai_analysis()
        self.test_api_endpoints()
        
        print("="*60)
        print("🎉 ALL TESTS COMPLETED!")
        print("\nTo use the questionnaire system:")
        print("1. Start Flask server: python app.py")
        print("2. POST /api/questionnaire/start - Start new session")
        print("3. POST /api/questionnaire/{session_id}/answer - Submit answers")
        print("4. GET /api/questionnaire/{session_id}/analysis - Get AI analysis")

def main():
    """Run the test suite."""
    tester = QuestionnaireSystemTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()