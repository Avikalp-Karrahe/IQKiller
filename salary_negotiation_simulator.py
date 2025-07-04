"""
Salary Negotiation Simulator for IQKiller
"""
import random
import time
from typing import Dict, List, Any

class SalaryNegotiationSimulator:
    def __init__(self, user_role="Software Engineer", base_salary=75000):
        self.user_role = user_role
        self.base_salary = base_salary
        self.total_score = 0
        
    def get_scenarios(self):
        return [
            {
                "title": "🎯 First Offer Challenge",
                "context": f"Hiring manager offers ${self.base_salary - 10000:,}",
                "choices": [
                    {"id": "accept", "text": "I accept!", "points": -10},
                    {"id": "counter", "text": "Market rate is higher", "points": 20},
                    {"id": "aggressive", "text": "Too low!", "points": -5}
                ]
            }
        ] 