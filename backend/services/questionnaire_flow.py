from typing import Dict, Any, Optional, Callable
import uuid

class QuestionnaireFlow:
    def __init__(self):
        self.question_flow = {
            "START": {
                "question": "What type of products does your company manufacture?",
                "type": "select",
                "options": ["Metal Parts", "Plastic Components", "Electronics", "Textiles", "Food Products", "Other"],
                "next": self._route_from_start
            },
            "METAL_1": {
                "question": "What's your primary manufacturing process?",
                "type": "select",
                "options": ["CNC Machining", "Stamping", "Casting", "Welding/Fabrication"],
                "next": lambda answer: "VOLUME"
            },
            "GENERAL_1": {
                "question": "What's your typical production volume?",
                "type": "select",
                "options": ["< 100 units/day", "100-1000 units/day", "1000-10000 units/day", "> 10000 units/day"],
                "next": lambda answer: "EMPLOYEES"
            },
            "VOLUME": {
                "question": "What's your typical production volume per day?",
                "type": "select",
                "options": ["< 50 units/day", "50-500 units/day", "500-5000 units/day", "> 5000 units/day"],
                "next": lambda answer: "EMPLOYEES"
            },
            "EMPLOYEES": {
                "question": "How many employees work in your manufacturing operations?",
                "type": "select",
                "options": ["1-10 employees", "11-50 employees", "51-200 employees", "200+ employees"],
                "next": lambda answer: "PAIN_POINTS"
            },
            "PAIN_POINTS": {
                "question": "What are the biggest challenges or pain points your company faces in manufacturing operations? (Please describe in detail)",
                "type": "text",
                "next": lambda answer: "QUALITY_CONTROL"
            },
            "QUALITY_CONTROL": {
                "question": "How do you currently handle quality control?",
                "type": "select",
                "options": ["Manual inspection", "Statistical sampling", "Automated testing", "Third-party inspection", "No formal process"],
                "next": lambda answer: "INVENTORY"
            },
            "INVENTORY": {
                "question": "How do you manage inventory and materials?",
                "type": "select",
                "options": ["Manual tracking (spreadsheets/paper)", "Basic software system", "ERP system", "Just-in-time approach", "No formal system"],
                "next": lambda answer: "CUSTOMER_SERVICE"
            },
            "CUSTOMER_SERVICE": {
                "question": "How many customer service inquiries do you handle per week?",
                "type": "select",
                "options": ["< 10 inquiries", "10-50 inquiries", "50-200 inquiries", "> 200 inquiries"],
                "next": lambda answer: "AUTOMATION_CURRENT"
            },
            "AUTOMATION_CURRENT": {
                "question": "What's your current level of automation?",
                "type": "select",
                "options": ["Fully manual operations", "Some automated tools", "Partially automated", "Highly automated", "Fully automated"],
                "next": lambda answer: "AUTOMATION_INTEREST"
            },
            "AUTOMATION_INTEREST": {
                "question": "Which areas would you be most interested in automating? (Describe your priorities and reasons)",
                "type": "text",
                "next": lambda answer: "BUDGET"
            },
            "BUDGET": {
                "question": "What's your typical annual budget for operational improvements?",
                "type": "select",
                "options": ["< $10,000", "$10,000 - $50,000", "$50,000 - $200,000", "$200,000 - $500,000", "> $500,000"],
                "next": lambda answer: "TIMELINE"
            },
            "TIMELINE": {
                "question": "What's your typical timeline for implementing new solutions?",
                "type": "select",
                "options": ["Immediate (< 1 month)", "Short-term (1-3 months)", "Medium-term (3-12 months)", "Long-term (1+ years)"],
                "next": lambda answer: "COMPLETE"
            }
        }
    
    def _route_from_start(self, answer: str) -> str:
        """Route from START question based on product type."""
        if answer == "Metal Parts":
            return "METAL_1"
        else:
            return "GENERAL_1"
    
    def get_question(self, question_id: str) -> Optional[Dict[str, Any]]:
        """Get question data by ID."""
        if question_id not in self.question_flow:
            return None
        
        question_data = self.question_flow[question_id].copy()
        # Remove the next function from the response
        question_data.pop('next', None)
        question_data['id'] = question_id
        return question_data
    
    def get_next_question_id(self, current_question_id: str, answer: str) -> Optional[str]:
        """Get the next question ID based on current question and answer."""
        if current_question_id not in self.question_flow:
            return None
        
        next_func = self.question_flow[current_question_id].get('next')
        if next_func is None:
            return None
        
        try:
            next_id = next_func(answer)
            return next_id if next_id != "COMPLETE" else None
        except Exception as e:
            print(f"Error determining next question: {e}")
            return None
    
    def is_complete(self, current_question_id: str, answer: str) -> bool:
        """Check if questionnaire is complete."""
        next_id = self.get_next_question_id(current_question_id, answer)
        return next_id is None
    
    def get_all_questions(self) -> Dict[str, Dict[str, Any]]:
        """Get all questions for reference (without next functions)."""
        result = {}
        for q_id, q_data in self.question_flow.items():
            clean_data = q_data.copy()
            clean_data.pop('next', None)
            clean_data['id'] = q_id
            result[q_id] = clean_data
        return result
    
    def validate_answer(self, question_id: str, answer: str) -> bool:
        """Validate if an answer is valid for the given question."""
        question = self.get_question(question_id)
        if not question:
            return False
        
        question_type = question.get('type')
        
        if question_type == 'select':
            return answer in question.get('options', [])
        elif question_type == 'text':
            return isinstance(answer, str) and len(answer.strip()) > 0
        elif question_type == 'number':
            try:
                float(answer)
                return True
            except ValueError:
                return False
        
        return False