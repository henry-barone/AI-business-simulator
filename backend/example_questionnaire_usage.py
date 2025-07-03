#!/usr/bin/env python3
"""
Example usage of the Intelligent Questionnaire API.
Demonstrates how to integrate the questionnaire system into your application.
"""

import requests
import json
import time

class QuestionnaireClient:
    """Client for interacting with the intelligent questionnaire API."""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session_id = None
    
    def start_questionnaire(self, company_id: str = None):
        """Start a new questionnaire session."""
        url = f"{self.base_url}/api/questionnaire/start"
        data = {"company_id": company_id} if company_id else {}
        
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            self.session_id = result['session_id']
            return result['question']
        else:
            raise Exception(f"Failed to start questionnaire: {response.status_code}")
    
    def submit_answer(self, answer: str):
        """Submit an answer and get the next question."""
        if not self.session_id:
            raise Exception("No active session. Call start_questionnaire() first.")
        
        url = f"{self.base_url}/api/questionnaire/{self.session_id}/answer"
        data = {"answer": answer}
        
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result['completed']:
                return None  # Questionnaire is complete
            else:
                return result['question']
        else:
            raise Exception(f"Failed to submit answer: {response.status_code}")
    
    def get_analysis(self):
        """Get the AI analysis results."""
        if not self.session_id:
            raise Exception("No active session.")
        
        url = f"{self.base_url}/api/questionnaire/{self.session_id}/analysis"
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()['analysis']
        else:
            raise Exception(f"Failed to get analysis: {response.status_code}")
    
    def get_responses(self):
        """Get all responses for the session."""
        if not self.session_id:
            raise Exception("No active session.")
        
        url = f"{self.base_url}/api/questionnaire/{self.session_id}/responses"
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()['responses']
        else:
            raise Exception(f"Failed to get responses: {response.status_code}")

def example_automated_flow():
    """Example: Automated questionnaire completion."""
    print("=== Automated Questionnaire Example ===\n")
    
    client = QuestionnaireClient()
    
    # Pre-defined answers for a metal parts manufacturer
    answers = [
        "Metal Parts",  # Product type
        "CNC Machining",  # Manufacturing process
        "500-5000 units/day",  # Production volume
        "11-50 employees",  # Employee count
        "Our biggest challenges are quality control issues, long setup times for new orders, and difficulty tracking inventory in real-time. We also struggle with manual inspection processes that are slow and error-prone.",  # Pain points
        "Manual inspection",  # Quality control
        "Basic software system",  # Inventory management
        "10-50 inquiries",  # Customer service volume
        "Some automated tools",  # Current automation
        "We would like to automate quality inspection and inventory tracking. These areas cause the most delays and errors. We are also interested in automated scheduling to reduce setup times.",  # Automation interest
        "$50,000 - $200,000",  # Budget
        "Medium-term (3-12 months)"  # Timeline
    ]
    
    try:
        # Start questionnaire
        question = client.start_questionnaire("company-123")
        print(f"Session ID: {client.session_id}")
        print(f"First question: {question['question']}\n")
        
        # Submit answers
        for i, answer in enumerate(answers):
            print(f"Q{i+1}: {question['question']}")
            print(f"A{i+1}: {answer}\n")
            
            next_question = client.submit_answer(answer)
            
            if next_question is None:
                print("✅ Questionnaire completed!")
                break
            else:
                question = next_question
        
        # Wait for AI analysis
        print("⏳ Waiting for AI analysis...")
        time.sleep(3)
        
        # Get analysis results
        try:
            analysis = client.get_analysis()
            print("\n🤖 AI Analysis Results:")
            print("="*50)
            print(f"Company Type: {analysis['company_type']}")
            print(f"Industry: {analysis['industry']}")
            print(f"Size Category: {analysis['size_category']}")
            print(f"Automation Level: {analysis['automation_level']}")
            print(f"Confidence Score: {analysis['confidence_score']:.2f}")
            
            print(f"\n📋 Pain Points ({len(analysis['pain_points'])}):")
            for i, pain_point in enumerate(analysis['pain_points'], 1):
                print(f"  {i}. {pain_point}")
            
            print(f"\n💡 Opportunities ({len(analysis['opportunities'])}):")
            for i, opportunity in enumerate(analysis['opportunities'], 1):
                print(f"  {i}. {opportunity}")
            
            print(f"\n🎯 Priority Areas ({len(analysis['priority_areas'])}):")
            for i, area in enumerate(analysis['priority_areas'], 1):
                print(f"  {i}. {area}")
                
        except Exception as e:
            print(f"⚠️  Analysis not yet ready: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def example_interactive_flow():
    """Example: Interactive questionnaire completion."""
    print("=== Interactive Questionnaire Example ===\n")
    
    client = QuestionnaireClient()
    
    try:
        # Start questionnaire
        question = client.start_questionnaire()
        print(f"Welcome! Session ID: {client.session_id}\n")
        
        while question:
            print(f"Question: {question['question']}")
            
            if question['type'] == 'select':
                print("Options:")
                for i, option in enumerate(question['options'], 1):
                    print(f"  {i}. {option}")
                
                # For demo, just pick the first option
                answer = question['options'][0]
                print(f"Selected: {answer}\n")
            else:
                # For text questions, provide a sample answer
                answer = "Sample answer for demonstration purposes."
                print(f"Answer: {answer}\n")
            
            # Submit answer and get next question
            question = client.submit_answer(answer)
        
        print("✅ Questionnaire completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def example_analysis_retrieval():
    """Example: Retrieving analysis for an existing session."""
    print("=== Analysis Retrieval Example ===\n")
    
    # This would use a real session ID from a completed questionnaire
    session_id = "example-session-id"
    
    try:
        url = f"http://localhost:5000/api/questionnaire/{session_id}/analysis"
        response = requests.get(url)
        
        if response.status_code == 200:
            analysis = response.json()['analysis']
            
            print("📊 Analysis Summary:")
            print(f"Company: {analysis.get('company_type', 'Unknown')}")
            print(f"Pain Points: {len(analysis.get('pain_points', []))}")
            print(f"Opportunities: {len(analysis.get('opportunities', []))}")
            print(f"Confidence: {analysis.get('confidence_score', 0):.2%}")
            
        else:
            print(f"❌ Session not found or analysis not available")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run the examples."""
    print("🧪 INTELLIGENT QUESTIONNAIRE API EXAMPLES\n")
    print("="*60)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:5000/api/questionnaire/flow")
        if response.status_code != 200:
            print("❌ Flask server is not running!")
            print("Start the server with: python app.py")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server!")
        print("Start the server with: python app.py")
        return
    
    print("✅ Server is running\n")
    
    # Run examples
    example_automated_flow()
    print("\n" + "="*60 + "\n")
    
    # Uncomment to run interactive example:
    # example_interactive_flow()

if __name__ == "__main__":
    main()