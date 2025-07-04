#!/usr/bin/env python3
"""
IQKiller: AI-Powered Job Analysis Platform
Advanced job posting analysis with comprehensive role previews and interview preparation.
Apple Human Interface Guidelines-aligned design with proper typography, spacing, and semantic colors.
"""

import gradio as gr
import time
import random
from orchestrator import Orchestrator, analyze
from micro.scrape import ScrapeMicroFunction
from micro.enrich import EnrichMicroFunction
from micro.draft import DraftMicroFunction
from micro.critique import CritiqueMicroFunction
from micro.render import RenderMicroFunction
from micro.qa import QAMicroFunction
from metrics import log_metric
from prompt_loader import prompt_loader
from typing import Any, Dict, Tuple, AsyncGenerator
import os
import render_cards
import renderer_nobs
import asyncio
from text_extractor import extract_nobs
from auth import create_login_interface, create_authenticated_wrapper, health_check
import flask
from flask import Flask
from enhanced_interview_orchestrator import EnhancedInterviewOrchestrator
from reddit_client import reddit_client

# Job news headlines for rotating display
JOB_MARKET_NEWS = [
    "🚀 AI and Machine Learning roles see 45% growth this quarter",
    "💼 Remote work opportunities increased 38% across tech companies", 
    "📈 Data Science positions show highest salary growth at 12% YoY",
    "🌟 Startup hiring surge: 67% increase in early-stage opportunities",
    "🎯 Skills gap widening: Python and cloud expertise in high demand",
    "💡 AI-first companies hiring 3x faster than traditional firms",
    "🔥 Frontend developers: React and TypeScript lead demand",
    "📊 Product Manager roles expand 28% in fintech sector",
    "🛡️ Cybersecurity positions offer 15% premium salaries",
    "🌍 Green tech hiring accelerates with climate innovation focus",
    "⚡ DevOps engineers see 22% boost in market demand",
    "🎨 UI/UX designers critical for digital transformation wave",
    "🔗 Blockchain developers command top-tier compensation packages",
    "📱 Mobile development surges with cross-platform expertise valued",
    "🧠 Neurodiversity hiring initiatives reshape tech recruitment"
]

# Salary Negotiation Simulator
class SalaryNegotiationSimulator:
    """Interactive salary negotiation training during analysis wait"""
    
    def __init__(self, user_role="Software Engineer", experience_level="Mid", base_salary=75000):
        self.user_role = user_role
        self.experience_level = experience_level
        self.base_salary = base_salary
        self.total_score = 0
        self.scenarios_completed = 0
        self.salary_gains = []
        self.confidence_score = 50
        
    def get_personalized_scenarios(self):
        """Generate 30 diverse scenarios based on user profile"""
        # Calculate salary ranges
        if self.experience_level.lower() in ["entry", "junior"]:
            salary_range = (self.base_salary - 10000, self.base_salary + 15000)
        elif self.experience_level.lower() in ["senior", "lead"]:
            salary_range = (self.base_salary + 10000, self.base_salary + 40000)
        else:  # Mid-level
            salary_range = (self.base_salary - 5000, self.base_salary + 25000)
        
        low_offer = salary_range[0]
        mid_offer = (salary_range[0] + salary_range[1]) // 2
        high_offer = salary_range[1]
        
        scenarios = [
            # First Offer Scenarios (1-10)
            {
                "title": "🎯 First Offer Challenge",
                "context": f"You're interviewing for a {self.user_role} position. The hiring manager says:",
                "offer_text": f'"We can offer you ${low_offer:,}"',
                "choices": [
                    {"id": "accept_immediately", "text": f"That sounds great! I accept ${low_offer:,}", "points": -10, "salary_impact": 0, "feedback": "❌ Never accept the first offer! You left money on the table.", "outcome": "You accepted immediately and missed potential gains."},
                    {"id": "research_counter", "text": f"I appreciate the offer. Based on my research, the market range is ${mid_offer:,}-${high_offer:,}", "points": 20, "salary_impact": 8000, "feedback": "✅ Excellent! Professional counter with market data.", "outcome": f"They respect your research and offer ${low_offer + 8000:,}!"},
                    {"id": "aggressive_counter", "text": f"That's way too low. I need at least ${high_offer + 10000:,}", "points": -5, "salary_impact": 2000, "feedback": "⚠️ Too aggressive without justification. Build rapport first.", "outcome": "They're taken aback but offer a small increase."},
                    {"id": "time_request", "text": "Thank you for the offer. Could I have a day to review the complete package?", "points": 15, "salary_impact": 5000, "feedback": "✅ Smart move! Buying time shows professionalism.", "outcome": "They appreciate your thoughtfulness and sweeten the deal."}
                ]
            },
            {
                "title": "💼 Lowball Offer Response",
                "context": "They start with an unusually low offer:",
                "offer_text": f'"We can start you at ${low_offer - 5000:,}"',
                "choices": [
                    {"id": "shocked_response", "text": "That seems quite low for this role...", "points": 5, "salary_impact": 3000, "feedback": "⚠️ Honest but could be more strategic.", "outcome": "They sense your disappointment and improve slightly."},
                    {"id": "data_driven", "text": f"Based on industry data, similar roles typically range ${mid_offer:,}-${high_offer:,}", "points": 18, "salary_impact": 12000, "feedback": "✅ Perfect! Data-driven approach commands respect.", "outcome": "They appreciate your preparation and make a competitive offer."},
                    {"id": "walk_away", "text": "I think there might be a misunderstanding about the role level", "points": 15, "salary_impact": 8000, "feedback": "✅ Bold move! Shows you know your worth.", "outcome": "They realize their mistake and present a much better offer."},
                    {"id": "negotiate_up", "text": f"I was expecting something closer to ${mid_offer:,}", "points": 12, "salary_impact": 6000, "feedback": "✅ Good counter! Clear expectation setting.", "outcome": "They meet you halfway with a reasonable increase."}
                ]
            },
            
            # Benefits & Perks Scenarios (11-15)
            {
                "title": "🎁 Beyond Base Salary",
                "context": "The salary is fixed, but the hiring manager says:",
                "offer_text": '"We have some flexibility with the benefits package though."',
                "choices": [
                    {"id": "give_up", "text": "Okay, I understand. The salary offer is fine.", "points": -5, "salary_impact": 0, "feedback": "❌ You missed valuable negotiation opportunities!", "outcome": "You accepted the base package with no improvements."},
                    {"id": "vacation_ask", "text": "Could we discuss additional vacation days? I'd value 5 extra PTO days.", "points": 15, "salary_impact": 3000, "feedback": "✅ Great! PTO has real value and shows work-life balance priorities.", "outcome": "They grant 3 extra vacation days (worth ~$3K value)!"},
                    {"id": "learning_budget", "text": "What about professional development? A $2,000 annual learning budget would be valuable.", "points": 18, "salary_impact": 2000, "feedback": "✅ Excellent! Shows growth mindset and benefits company too.", "outcome": "They approve a $1,500 annual learning budget!"},
                    {"id": "remote_work", "text": "Could we discuss remote work flexibility? 2-3 days remote per week?", "points": 12, "salary_impact": 4000, "feedback": "✅ Smart ask! Remote work has significant lifestyle value.", "outcome": "They agree to 2 remote days per week!"}
                ]
            },
            {
                "title": "🏥 Health Benefits Negotiation",
                "context": "They mention the health benefits package:",
                "offer_text": '"We cover 80% of health insurance premiums"',
                "choices": [
                    {"id": "accept_standard", "text": "That sounds reasonable", "points": 0, "salary_impact": 0, "feedback": "⚠️ You could have explored better options.", "outcome": "You accepted the standard package."},
                    {"id": "full_coverage", "text": "Is there flexibility to get 100% coverage?", "points": 15, "salary_impact": 2400, "feedback": "✅ Great ask! Health benefits are valuable.", "outcome": "They agree to 95% coverage - saving you $200/month!"},
                    {"id": "family_coverage", "text": "What about family coverage options?", "points": 10, "salary_impact": 1800, "feedback": "✅ Smart to think ahead about family needs.", "outcome": "They improve the family plan contribution."},
                    {"id": "wellness_programs", "text": "Are there wellness programs or gym memberships included?", "points": 8, "salary_impact": 600, "feedback": "✅ Good thinking about comprehensive wellness.", "outcome": "They add a $50/month wellness stipend!"}
                ]
            },
            
            # Pressure & Timing Scenarios (16-20)
            {
                "title": "⏰ Under Pressure",
                "context": "After your counter-offer, they respond:",
                "offer_text": '"We need a decision by tomorrow morning or we\'ll move to the next candidate."',
                "choices": [
                    {"id": "panic_accept", "text": "Okay, okay! I'll take the original offer right now!", "points": -15, "salary_impact": -5000, "feedback": "❌ Panic decisions cost money! Never negotiate under pressure.", "outcome": "You accepted a worse deal due to artificial urgency."},
                    {"id": "professional_delay", "text": "I appreciate the timeline. Could I have until Friday to give you a thoughtful response?", "points": 20, "salary_impact": 6000, "feedback": "✅ Perfect! You maintained control and professionalism.", "outcome": "They respect your approach and meet your salary request!"},
                    {"id": "competing_offer", "text": "I'm also considering another opportunity. Could we match their timeline?", "points": 10, "salary_impact": 3000, "feedback": "⚠️ Risky without a real competing offer. Use carefully.", "outcome": "They're concerned about losing you and improve the offer slightly."},
                    {"id": "value_discussion", "text": "I want to make the right decision for both of us. Can we discuss the role's growth potential?", "points": 15, "salary_impact": 4000, "feedback": "✅ Smart redirect! Shows you're thinking long-term.", "outcome": "They appreciate your perspective and offer a signing bonus!"}
                ]
            },
            {
                "title": "🚨 Exploding Offer",
                "context": "They present an offer with unusual urgency:",
                "offer_text": '"This offer expires in 2 hours - we need to fill the position today"',
                "choices": [
                    {"id": "rush_accept", "text": "I'll take it! Don't want to miss out!", "points": -20, "salary_impact": -8000, "feedback": "❌ Major red flag! Legitimate offers don't expire in hours.", "outcome": "You fell for a pressure tactic and accepted poor terms."},
                    {"id": "call_bluff", "text": "I need at least 24 hours to review any offer properly", "points": 25, "salary_impact": 10000, "feedback": "🏆 Excellent! You called their bluff professionally.", "outcome": "They realize their tactic failed and present a much better offer!"},
                    {"id": "question_urgency", "text": "What's driving such an urgent timeline?", "points": 15, "salary_impact": 5000, "feedback": "✅ Great question! Professional skepticism pays off.", "outcome": "They admit they're being overly aggressive and give you proper time."},
                    {"id": "polite_decline", "text": "I'm interested but can't make quality decisions under such pressure", "points": 18, "salary_impact": 7000, "feedback": "✅ Perfect response! Shows professionalism and standards.", "outcome": "They respect your boundaries and extend a better offer."}
                ]
            },
            
            # Advanced Negotiation Scenarios (21-30)
            {
                "title": "🎯 Competing Offers",
                "context": "You mention having another offer:",
                "offer_text": '"How does our offer compare to your other opportunity?"',
                "choices": [
                    {"id": "reveal_everything", "text": f"They offered ${mid_offer + 5000:,} with better benefits", "points": -5, "salary_impact": 2000, "feedback": "⚠️ Showing all your cards reduces leverage.", "outcome": "They barely match the competing offer."},
                    {"id": "strategic_vague", "text": "The other role is attractive, but I prefer your company culture", "points": 20, "salary_impact": 8000, "feedback": "✅ Perfect! Maintains leverage while showing interest.", "outcome": "They significantly improve their offer to secure you!"},
                    {"id": "specific_ask", "text": "If you could match their compensation structure, I'd love to join here", "points": 15, "salary_impact": 6000, "feedback": "✅ Clear and actionable request.", "outcome": "They work to create a competitive package."},
                    {"id": "focus_growth", "text": "I'm more interested in growth potential than just immediate compensation", "points": 12, "salary_impact": 4000, "feedback": "✅ Shows long-term thinking and gets their attention.", "outcome": "They offer accelerated promotion timeline with salary bumps."}
                ]
            },
            {
                "title": "📈 Performance-Based Pay",
                "context": "They propose a performance component:",
                "offer_text": f'"We can offer ${self.base_salary} base plus up to 20% bonus based on performance"',
                "choices": [
                    {"id": "accept_vague", "text": "That sounds great! I'm confident in my performance", "points": -5, "salary_impact": 0, "feedback": "❌ Never accept vague performance metrics!", "outcome": "The bonus criteria turn out to be nearly impossible to achieve."},
                    {"id": "demand_specifics", "text": "Could we define the specific metrics and targets for the bonus?", "points": 20, "salary_impact": 8000, "feedback": "✅ Excellent! Always clarify performance criteria.", "outcome": "They provide clear, achievable metrics and increase the bonus potential!"},
                    {"id": "higher_base", "text": f"I'd prefer ${self.base_salary + 10000:,} base with a smaller bonus component", "points": 15, "salary_impact": 6000, "feedback": "✅ Smart! Base salary is more predictable than bonuses.", "outcome": "They agree to a higher guaranteed base salary."},
                    {"id": "quarterly_reviews", "text": "Can we set up quarterly check-ins to track progress toward bonus goals?", "points": 18, "salary_impact": 7000, "feedback": "✅ Proactive approach! Shows you're serious about performance.", "outcome": "They love your initiative and improve the bonus structure."}
                ]
            },
            {
                "title": "🏢 Startup Equity Discussion",
                "context": "At a startup, they mention equity:",
                "offer_text": '"We can offer 0.1% equity vesting over 4 years"',
                "choices": [
                    {"id": "excited_accept", "text": "Equity sounds exciting! I'm in!", "points": -10, "salary_impact": -3000, "feedback": "❌ Never accept equity without understanding the details!", "outcome": "The equity terms turn out to be unfavorable with high dilution risk."},
                    {"id": "ask_valuation", "text": "What's the current company valuation and expected dilution?", "points": 18, "salary_impact": 5000, "feedback": "✅ Smart questions! Equity value depends on these factors.", "outcome": "They're impressed by your sophistication and improve the equity package."},
                    {"id": "more_equity", "text": "Could we discuss 0.2% given my experience level?", "points": 12, "salary_impact": 4000, "feedback": "✅ Good negotiation! More equity = more upside.", "outcome": "They agree to 0.15% after discussing your contributions."},
                    {"id": "vesting_schedule", "text": "Is there flexibility in the vesting schedule or cliff period?", "points": 15, "salary_impact": 3000, "feedback": "✅ Important details! Vesting terms matter as much as percentage.", "outcome": "They offer a more favorable vesting schedule with shorter cliff."}
                ]
            },
            {
                "title": "🎓 Professional Development",
                "context": "You bring up growth opportunities:",
                "offer_text": '"We believe in promoting from within and supporting growth"',
                "choices": [
                    {"id": "vague_satisfaction", "text": "That's great to hear!", "points": 0, "salary_impact": 0, "feedback": "⚠️ Get specific commitments, not just promises.", "outcome": "No concrete development benefits are added."},
                    {"id": "conference_budget", "text": "Could we include a $3,000 annual conference and training budget?", "points": 15, "salary_impact": 3000, "feedback": "✅ Specific ask for measurable development support.", "outcome": "They approve a $2,500 annual learning budget!"},
                    {"id": "promotion_timeline", "text": "What's the typical timeline for promotion to senior level?", "points": 12, "salary_impact": 2000, "feedback": "✅ Good planning! Shows ambition and goal-setting.", "outcome": "They outline a clear 18-month promotion path."},
                    {"id": "mentorship_program", "text": "Is there a formal mentorship program or could we establish one?", "points": 18, "salary_impact": 4000, "feedback": "✅ Excellent! Shows leadership potential and growth mindset.", "outcome": "They pair you with a senior leader and fast-track development!"}
                ]
            },
            {
                "title": "🏠 Relocation Package",
                "context": "The role requires relocation:",
                "offer_text": '"We can provide some relocation assistance"',
                "choices": [
                    {"id": "assume_covered", "text": "Great! I'm excited to move for this opportunity", "points": -5, "salary_impact": -5000, "feedback": "❌ Never assume - get specific relocation details!", "outcome": "The 'assistance' turns out to be minimal and you pay most costs."},
                    {"id": "full_package", "text": "Could we discuss a comprehensive relocation package including moving costs and temporary housing?", "points": 20, "salary_impact": 12000, "feedback": "✅ Perfect! Relocation is expensive - get proper support.", "outcome": "They provide full moving costs plus 30 days temporary housing!"},
                    {"id": "cost_breakdown", "text": "What specific costs does the relocation assistance cover?", "points": 15, "salary_impact": 8000, "feedback": "✅ Smart to get details upfront.", "outcome": "They clarify and improve the package after your questions."},
                    {"id": "home_buying", "text": "Is there support for home buying or real estate fees?", "points": 12, "salary_impact": 6000, "feedback": "✅ Good thinking about major relocation costs.", "outcome": "They add real estate fee reimbursement up to $5,000."}
                ]
            },
            # Additional scenarios continue with similar structure...
            # Stock Options, Flexible Hours, Title Negotiation, Contract Terms, etc.
            {
                "title": "⏰ Flexible Schedule Request",
                "context": "You ask about work arrangements:",
                "offer_text": '"We typically work standard business hours"',
                "choices": [
                    {"id": "accept_standard", "text": "That works for me", "points": 0, "salary_impact": 0, "feedback": "⚠️ You could have explored flexibility options.", "outcome": "You're locked into standard 9-5 schedule."},
                    {"id": "flexible_hours", "text": "Would there be flexibility for a 7am-4pm or 10am-7pm schedule?", "points": 15, "salary_impact": 3000, "feedback": "✅ Great ask! Flexibility has real lifestyle value.", "outcome": "They agree to flexible core hours with 10am-3pm overlap!"},
                    {"id": "compressed_schedule", "text": "Could we explore a 4-day/10-hour schedule?", "points": 12, "salary_impact": 4000, "feedback": "✅ Bold ask! Shows you're thinking creatively.", "outcome": "They're intrigued and agree to a trial period."},
                    {"id": "hybrid_proposal", "text": "What about a hybrid schedule with flexible hours on remote days?", "points": 18, "salary_impact": 5000, "feedback": "✅ Perfect combination! Shows strategic thinking.", "outcome": "They love the proposal and implement it company-wide!"}
                ]
            },
            {
                "title": "📝 Job Title Negotiation",
                "context": "They offer a title that seems junior:",
                "offer_text": f'"The title would be Associate {self.user_role}"',
                "choices": [
                    {"id": "accept_title", "text": "That title works for me", "points": -5, "salary_impact": 0, "feedback": "❌ Titles matter for career progression!", "outcome": "You're seen as more junior than your experience level."},
                    {"id": "negotiate_senior", "text": f"Given my experience, could we discuss '{self.user_role}' or 'Senior Associate {self.user_role}'?", "points": 18, "salary_impact": 4000, "feedback": "✅ Excellent! Titles impact both perception and future salary.", "outcome": "They agree to the senior title plus salary adjustment!"},
                    {"id": "specialist_title", "text": f"Would '{self.user_role} Specialist' better reflect the role requirements?", "points": 12, "salary_impact": 2000, "feedback": "✅ Good alternative! Specialist titles often carry more weight.", "outcome": "They like the specialist designation and update the offer."},
                    {"id": "future_promotion", "text": "What would be the timeline for promotion to the next title level?", "points": 15, "salary_impact": 3000, "feedback": "✅ Strategic thinking! Plans for growth.", "outcome": "They guarantee review for promotion in 12 months."}
                ]
            },
            {
                "title": "💰 Signing Bonus Discussion",
                "context": "You're leaving a job with unvested benefits:",
                "offer_text": '"We understand transitions can be costly"',
                "choices": [
                    {"id": "no_mention", "text": "I'm excited to make the transition", "points": -5, "salary_impact": 0, "feedback": "❌ You should have mentioned your forfeited benefits!", "outcome": "You lose unvested benefits with no compensation."},
                    {"id": "signing_bonus", "text": "Could we discuss a signing bonus to offset the unvested benefits I'm forfeiting?", "points": 20, "salary_impact": 15000, "feedback": "✅ Perfect! Legitimate reason for signing bonus.", "outcome": "They offer a $15,000 signing bonus to cover your losses!"},
                    {"id": "specific_amount", "text": "I'm forfeiting $10,000 in unvested options - could you help bridge that gap?", "points": 18, "salary_impact": 10000, "feedback": "✅ Specific and reasonable request.", "outcome": "They match your forfeited amount with a signing bonus."},
                    {"id": "gradual_compensation", "text": "Could we structure additional compensation over the first year?", "points": 15, "salary_impact": 8000, "feedback": "✅ Creative solution! Shows flexibility.", "outcome": "They offer quarterly bonuses totaling $8,000 in year one."}
                ]
            },
            {
                "title": "🚀 Commission Structure",
                "context": "For a sales role, they mention commission:",
                "offer_text": '"Base plus commission structure with good earning potential"',
                "choices": [
                    {"id": "trust_potential", "text": "That sounds promising!", "points": -10, "salary_impact": -5000, "feedback": "❌ Never accept vague commission promises!", "outcome": "The commission structure turns out to be nearly impossible to achieve."},
                    {"id": "historical_data", "text": "Could you share what current reps are averaging in total compensation?", "points": 20, "salary_impact": 12000, "feedback": "✅ Brilliant question! Historical data reveals realistic expectations.", "outcome": "The data shows higher potential and they improve the base guarantee!"},
                    {"id": "commission_rates", "text": "What are the specific commission rates and tiers?", "points": 18, "salary_impact": 8000, "feedback": "✅ Essential details! Commission structure matters more than base.", "outcome": "They provide clear rates and add accelerators for high performance."},
                    {"id": "draw_guarantee", "text": "Is there a draw or minimum guarantee while I'm ramping up?", "points": 15, "salary_impact": 6000, "feedback": "✅ Smart protection! New sales roles need ramp-up support.", "outcome": "They offer a 6-month guarantee while you build your pipeline."}
                ]
            },
            {
                "title": "📊 Bonus Clarity",
                "context": "They mention an annual bonus:",
                "offer_text": '"Everyone gets a year-end bonus based on company performance"',
                "choices": [
                    {"id": "sounds_good", "text": "That's a nice additional benefit", "points": -5, "salary_impact": 0, "feedback": "❌ Get specifics on bonus calculations!", "outcome": "The 'bonus' turns out to be a small gift card."},
                    {"id": "target_percentage", "text": "What's the target bonus percentage and how is it calculated?", "points": 18, "salary_impact": 6000, "feedback": "✅ Perfect question! Bonus clarity prevents disappointment.", "outcome": "They clarify it's 10-15% based on specific metrics you can influence!"},
                    {"id": "individual_performance", "text": "Is the bonus based on individual performance or only company results?", "points": 15, "salary_impact": 4000, "feedback": "✅ Important distinction! Individual components give you more control.", "outcome": "They add an individual performance component to the bonus."},
                    {"id": "historical_bonuses", "text": "What have bonuses been in recent years?", "points": 12, "salary_impact": 3000, "feedback": "✅ Historical data helps set realistic expectations.", "outcome": "The track record is strong and they guarantee minimum payout."}
                ]
            },
            # Additional scenarios to reach 30 total
            {
                "title": "🎯 Stock Options Details",
                "context": "They mention stock options as part of the package:",
                "offer_text": '"We also provide stock options to all employees"',
                "choices": [
                    {"id": "sounds_exciting", "text": "That sounds exciting! I love equity compensation", "points": -5, "salary_impact": 0, "feedback": "❌ Get details before getting excited about stock options!", "outcome": "The options turn out to have little value due to high strike price."},
                    {"id": "ask_details", "text": "Could you explain the strike price, vesting schedule, and exercise window?", "points": 20, "salary_impact": 8000, "feedback": "✅ Excellent! These details determine actual value.", "outcome": "They're impressed and offer better terms with lower strike price!"},
                    {"id": "prefer_cash", "text": f"I'd prefer additional ${5000:,} in base salary instead of options", "points": 15, "salary_impact": 5000, "feedback": "✅ Sometimes cash is better than risky options.", "outcome": "They respect your preference and increase base salary."},
                    {"id": "ask_quantity", "text": "How many options would I receive and what's the current fair market value?", "points": 18, "salary_impact": 6000, "feedback": "✅ Smart questions about quantity and current value.", "outcome": "They increase the grant size based on your sophistication."}
                ]
            },
            {
                "title": "🏖️ Unlimited PTO Policy",
                "context": "They proudly announce their policy:",
                "offer_text": '"We have unlimited paid time off!"',
                "choices": [
                    {"id": "sounds_amazing", "text": "That sounds amazing! I love unlimited PTO", "points": -10, "salary_impact": -2000, "feedback": "❌ Unlimited PTO often means less vacation than traditional policies!", "outcome": "You discover people rarely take time off due to culture pressure."},
                    {"id": "ask_reality", "text": "What do employees typically take per year? What's considered reasonable?", "points": 20, "salary_impact": 4000, "feedback": "✅ Perfect! Unlimited policies need cultural context.", "outcome": "They clarify expectations and guarantee minimums in writing!"},
                    {"id": "prefer_accrual", "text": "I'd prefer a traditional accrual system with 25 days annually", "points": 15, "salary_impact": 3000, "feedback": "✅ Bold request! Traditional systems provide more protection.", "outcome": "They accommodate your preference with a special accrual policy."},
                    {"id": "written_guidelines", "text": "Could we establish written guidelines for what unlimited means?", "points": 18, "salary_impact": 3500, "feedback": "✅ Smart protection! Gets policies in writing.", "outcome": "They create clear guidelines and improve the policy for everyone."}
                ]
            },
            {
                "title": "🚗 Company Car Discussion",
                "context": "For a role with travel requirements:",
                "offer_text": '"You\'ll need reliable transportation for client visits"',
                "choices": [
                    {"id": "own_car", "text": "No problem, I have my own car", "points": -5, "salary_impact": -3000, "feedback": "❌ You're missing out on significant benefits!", "outcome": "You pay all vehicle costs yourself including wear and tear."},
                    {"id": "car_allowance", "text": "Could we discuss a monthly car allowance for business use?", "points": 18, "salary_impact": 6000, "feedback": "✅ Smart! Car allowances cover business use costs.", "outcome": "They offer $500/month car allowance plus gas reimbursement!"},
                    {"id": "company_vehicle", "text": "Would a company vehicle be available for the role?", "points": 15, "salary_impact": 8000, "feedback": "✅ Direct approach! Company cars save significant money.", "outcome": "They provide a company vehicle for business and personal use."},
                    {"id": "mileage_plus", "text": "What about mileage reimbursement plus vehicle maintenance support?", "points": 12, "salary_impact": 4000, "feedback": "✅ Comprehensive thinking about vehicle costs.", "outcome": "They agree to full IRS mileage rate plus maintenance allowance."}
                ]
            },
            {
                "title": "🏠 Work From Home Equipment",
                "context": "They mention remote work setup:",
                "offer_text": '"You\'ll need a proper home office setup"',
                "choices": [
                    {"id": "have_setup", "text": "I already have everything I need", "points": -5, "salary_impact": -2000, "feedback": "❌ Companies should provide work equipment!", "outcome": "You end up paying for professional equipment yourself."},
                    {"id": "full_setup", "text": "Could you provide a complete home office setup including desk, chair, monitor, and laptop?", "points": 20, "salary_impact": 4000, "feedback": "✅ Perfect! Comprehensive equipment request.", "outcome": "They provide full ergonomic setup plus annual refresh budget!"},
                    {"id": "equipment_budget", "text": "What's the budget for home office equipment and how often is it refreshed?", "points": 18, "salary_impact": 3000, "feedback": "✅ Great question about ongoing equipment needs.", "outcome": "They increase the budget and add annual refresh cycle."},
                    {"id": "internet_support", "text": "Will you cover internet costs and provide tech support for home office?", "points": 15, "salary_impact": 1800, "feedback": "✅ Smart thinking about ongoing home office costs.", "outcome": "They add internet stipend and priority IT support."}
                ]
            },
            {
                "title": "⚖️ Work-Life Balance Discussion",
                "context": "You ask about work expectations:",
                "offer_text": '"We believe in work-life balance"',
                "choices": [
                    {"id": "trust_statement", "text": "That's great to hear!", "points": -5, "salary_impact": 0, "feedback": "❌ Get specific commitments about work-life balance!", "outcome": "You discover 'balance' means 60+ hour weeks."},
                    {"id": "specific_hours", "text": "What are typical working hours and expectations for after-hours availability?", "points": 18, "salary_impact": 3000, "feedback": "✅ Important clarification! Sets boundaries from start.", "outcome": "They clarify reasonable hours and limit after-hours contact!"},
                    {"id": "email_policy", "text": "What's the policy on emails and calls outside business hours?", "points": 15, "salary_impact": 2000, "feedback": "✅ Smart boundary setting about digital communication.", "outcome": "They implement clear communication boundaries."},
                    {"id": "burnout_prevention", "text": "What measures are in place to prevent burnout and ensure sustainable workload?", "points": 20, "salary_impact": 4000, "feedback": "✅ Excellent question showing long-term thinking!", "outcome": "They establish workload monitoring and mandatory time off periods."}
                ]
            },
            {
                "title": "💼 Contract vs Full-Time",
                "context": "They offer a contractor position:",
                "offer_text": '"We\'re offering this as a 1099 contractor role"',
                "choices": [
                    {"id": "accept_contractor", "text": "That works for me", "points": -10, "salary_impact": -8000, "feedback": "❌ Contractor roles need 25-30% higher pay to offset taxes and benefits!", "outcome": "You lose significant money on taxes and have no benefits."},
                    {"id": "demand_w2", "text": "I'd prefer a W-2 employee position with benefits", "points": 20, "salary_impact": 12000, "feedback": "✅ Smart! Employee status provides much better total compensation.", "outcome": "They convert to employee status with full benefits package!"},
                    {"id": "contractor_premium", "text": f"For contractor work, I'd need ${int(low_offer * 1.3):,} to offset taxes and lack of benefits", "points": 18, "salary_impact": 15000, "feedback": "✅ Perfect calculation! Contractors need significant premium.", "outcome": "They agree to the premium rate recognizing contractor costs."},
                    {"id": "hybrid_arrangement", "text": "Could we explore a hybrid with some employee benefits?", "points": 12, "salary_impact": 6000, "feedback": "✅ Creative solution finding middle ground.", "outcome": "They offer contractor rate with health insurance contribution."}
                ]
            },
            {
                "title": "🔒 Non-Compete Agreement",
                "context": "They mention employment terms:",
                "offer_text": '"Standard employment contract includes non-compete clause"',
                "choices": [
                    {"id": "accept_standard", "text": "Standard terms are fine with me", "points": -15, "salary_impact": -5000, "feedback": "❌ Never accept non-competes without review! They limit your future options.", "outcome": "You're locked out of industry opportunities for 2 years if you leave."},
                    {"id": "negotiate_scope", "text": "Could we limit the non-compete to direct competitors only?", "points": 18, "salary_impact": 4000, "feedback": "✅ Smart! Limiting scope protects your career flexibility.", "outcome": "They narrow the clause to only direct competitors in your city."},
                    {"id": "time_limit", "text": "Would you consider reducing the non-compete period to 6 months?", "points": 15, "salary_impact": 3000, "feedback": "✅ Good negotiation! Shorter periods are more reasonable.", "outcome": "They agree to 6 months instead of 2 years."},
                    {"id": "compensation_requirement", "text": "If there's a non-compete, I'd need 50% salary continuation during the restricted period", "points": 20, "salary_impact": 8000, "feedback": "✅ Brilliant! If they limit your earning, they should compensate.", "outcome": "They remove the non-compete entirely rather than pay continuation!"}
                ]
            },
            {
                "title": "🎖️ Military Leave Policy",
                "context": "As a veteran, you ask about military obligations:",
                "offer_text": '"We support our veteran employees"',
                "choices": [
                    {"id": "general_support", "text": "That's great to hear", "points": 5, "salary_impact": 0, "feedback": "⚠️ Get specific military leave policies in writing.", "outcome": "General support but no specific policies."},
                    {"id": "reserve_leave", "text": "What's the policy for military reserve training and deployment?", "points": 18, "salary_impact": 3000, "feedback": "✅ Important for reserve/guard members! Shows planning.", "outcome": "They establish generous military leave beyond federal minimums!"},
                    {"id": "differential_pay", "text": "Do you provide military pay differential for active duty periods?", "points": 15, "salary_impact": 4000, "feedback": "✅ Great benefit that many companies offer veterans.", "outcome": "They provide full pay differential for military service."},
                    {"id": "va_benefits", "text": "Can we ensure schedule flexibility for VA appointments?", "points": 12, "salary_impact": 1000, "feedback": "✅ Important healthcare consideration for veterans.", "outcome": "They guarantee flexible scheduling for veteran healthcare."}
                ]
            },
            {
                "title": "🏆 Performance Review Cycle",
                "context": "They explain their review process:",
                "offer_text": '"We do annual performance reviews"',
                "choices": [
                    {"id": "sounds_standard", "text": "Annual reviews sound standard", "points": 0, "salary_impact": 0, "feedback": "⚠️ Annual reviews can delay recognition and raises!", "outcome": "You wait a full year for any salary adjustments."},
                    {"id": "quarterly_checkins", "text": "Could we establish quarterly check-ins for more frequent feedback?", "points": 15, "salary_impact": 3000, "feedback": "✅ Smart! More frequent feedback leads to faster growth.", "outcome": "They implement quarterly reviews with faster advancement opportunities!"},
                    {"id": "early_review", "text": "Could I have a 6-month review for early adjustment based on performance?", "points": 18, "salary_impact": 5000, "feedback": "✅ Excellent! Shows confidence and accelerates recognition.", "outcome": "They agree to 6-month review with potential early raise!"},
                    {"id": "objective_metrics", "text": "What are the specific metrics and criteria for performance evaluation?", "points": 12, "salary_impact": 2000, "feedback": "✅ Important to understand how you'll be measured.", "outcome": "They clarify metrics and add achievement bonuses."}
                ]
            },
            {
                "title": "💡 Innovation Time Policy",
                "context": "You ask about creative freedom:",
                "offer_text": '"We encourage innovation and new ideas"',
                "choices": [
                    {"id": "sounds_encouraging", "text": "That's an encouraging culture", "points": 5, "salary_impact": 0, "feedback": "⚠️ Get specific time allocation for innovation projects.", "outcome": "Cultural encouragement but no dedicated innovation time."},
                    {"id": "twenty_percent", "text": "Do you offer '20% time' for personal projects like Google?", "points": 18, "salary_impact": 4000, "feedback": "✅ Great question! Innovation time drives engagement and results.", "outcome": "They implement 20% time policy inspired by your suggestion!"},
                    {"id": "innovation_budget", "text": "Is there a budget for experimenting with new tools and technologies?", "points": 15, "salary_impact": 2000, "feedback": "✅ Smart! Innovation needs resources, not just time.", "outcome": "They allocate innovation budget for your experiments."},
                    {"id": "patent_policy", "text": "What's the policy on intellectual property and patents from employee innovations?", "points": 12, "salary_impact": 3000, "feedback": "✅ Important IP consideration for innovative roles.", "outcome": "They offer inventor bonuses and patent recognition program."}
                ]
            },
            {
                "title": "🌍 International Travel",
                "context": "The role involves global work:",
                "offer_text": '"This position requires some international travel"',
                "choices": [
                    {"id": "love_travel", "text": "I love international travel!", "points": -5, "salary_impact": -2000, "feedback": "❌ International travel has real costs and impacts!", "outcome": "You bear personal costs and travel fatigue without compensation."},
                    {"id": "travel_class", "text": "What's the travel policy for international flights - business class for flights over 6 hours?", "points": 18, "salary_impact": 5000, "feedback": "✅ Smart! Long international flights need proper accommodation.", "outcome": "They agree to business class for international travel plus extended recovery time!"},
                    {"id": "travel_insurance", "text": "Will comprehensive travel insurance and emergency support be provided?", "points": 15, "salary_impact": 2000, "feedback": "✅ Important safety and security consideration.", "outcome": "They provide comprehensive international travel insurance and 24/7 support."},
                    {"id": "family_impact", "text": "How do you support employees with families during extended international assignments?", "points": 12, "salary_impact": 3000, "feedback": "✅ Thoughtful consideration of work-life impact.", "outcome": "They add family support services and spouse travel allowance."}
                ]
            }
        ]
        
        return scenarios
    
    def get_random_scenario(self):
        """Get a random scenario from the full list"""
        scenarios = self.get_personalized_scenarios()
        return random.choice(scenarios) if scenarios else None
    
    def evaluate_choice(self, scenario, choice_id):
        """Evaluate user's choice and return result"""
        choice = next((c for c in scenario["choices"] if c["id"] == choice_id), None)
        if not choice:
            return {"error": "Invalid choice"}
        
        self.total_score += choice["points"]
        self.salary_gains.append(choice["salary_impact"])
        self.confidence_score += choice.get("confidence_impact", 0)
        self.scenarios_completed += 1
        
        return {
            "feedback": choice["feedback"],
            "points": choice["points"],
            "salary_impact": choice["salary_impact"],
            "outcome": choice["outcome"]
        }
    
    def get_final_assessment(self):
        """Generate final assessment after all scenarios"""
        total_salary_gain = sum(self.salary_gains)
        avg_score = self.total_score / max(self.scenarios_completed, 1)
        
        if avg_score >= 15:
            style = "🏆 Elite Negotiator"
            style_desc = "You're a strategic professional who maximizes value"
        elif avg_score >= 10:
            style = "💼 Strategic Professional"
            style_desc = "You balance assertiveness with relationship building"
        elif avg_score >= 5:
            style = "📈 Learning Negotiator"
            style_desc = "You're developing strong negotiation instincts"
        else:
            style = "🎯 Growth Opportunity"
            style_desc = "Focus on preparation and confidence building"
        
        return {
            "style": style,
            "style_description": style_desc,
            "total_score": self.total_score,
            "potential_annual_gain": total_salary_gain,
            "scenarios_completed": self.scenarios_completed,
            "success_rate": (self.total_score / (self.scenarios_completed * 20)) * 100 if self.scenarios_completed > 0 else 0,
            "key_insight": f"🚀 Your negotiation skills could earn you ${total_salary_gain:,} more annually!" if total_salary_gain >= 8000 else "🎯 Focus on preparation and confidence - the potential is there!"
        }

# Random Scenario Cycling Manager
class ScenarioCyclingManager:
    """Manages random scenario cycling during analysis wait time"""
    
    def __init__(self, simulator):
        self.simulator = simulator
        self.shown_scenarios = set()
        self.current_scenario_idx = 0
        
    def get_next_random_scenario(self):
        """Get next random scenario, avoiding repeats until all are shown"""
        scenarios = self.simulator.get_personalized_scenarios()
        
        # If we've shown all scenarios, reset the set
        if len(self.shown_scenarios) >= len(scenarios):
            self.shown_scenarios.clear()
        
        # Get scenarios not yet shown
        available_scenarios = [i for i in range(len(scenarios)) if i not in self.shown_scenarios]
        
        if not available_scenarios:
            # Fallback to random if something goes wrong
            return random.choice(scenarios), random.randint(0, len(scenarios)-1)
        
        # Pick random scenario from available ones
        scenario_idx = random.choice(available_scenarios)
        self.shown_scenarios.add(scenario_idx)
        
        return scenarios[scenario_idx], scenario_idx

def format_negotiation_scenario_for_display(scenario, scenario_num, total_scenarios):
    """Format negotiation scenario for HTML display with timer"""
    return f"""
    <div class="negotiation-scenario">
        <div class="scenario-header">
            <div class="scenario-progress">
                <span class="scenario-counter">Scenario {scenario_num}/{total_scenarios}</span>
                <div class="timer-container">
                    <div class="timer-circle">
                        <span id="timer-text">15</span>
                    </div>
                    <span class="timer-label">seconds</span>
                </div>
            </div>
            <h3 class="scenario-title">{scenario['title']}</h3>
            <p class="scenario-context">{scenario['context']}</p>
            <div class="scenario-offer">
                {scenario['offer_text']}
            </div>
        </div>
        
        <div class="scenario-choices">
            <p class="choice-prompt"><strong>How do you respond?</strong></p>
        </div>
    </div>
    
    <style>
    .negotiation-scenario {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 16px;
        padding: 32px;
        margin: 20px 0;
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    .scenario-header {{
        text-align: center;
        margin-bottom: 24px;
    }}
    
    .scenario-progress {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }}
    
    .scenario-counter {{
        background: rgba(255, 255, 255, 0.2);
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 500;
    }}
    
    .timer-container {{
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    
    .timer-circle {{
        width: 50px;
        height: 50px;
        border: 3px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }}
    
    #timer-text {{
        font-size: 18px;
        font-weight: 700;
    }}
    
    .timer-label {{
        font-size: 12px;
        opacity: 0.8;
    }}
    
    .scenario-title {{
        font-size: 28px;
        font-weight: 600;
        margin-bottom: 16px;
        line-height: 1.2;
    }}
    
    .scenario-context {{
        font-size: 18px;
        margin-bottom: 16px;
        opacity: 0.9;
        line-height: 1.4;
    }}
    
    .scenario-offer {{
        background: rgba(255, 255, 255, 0.15);
        border-radius: 12px;
        padding: 20px;
        font-size: 20px;
        font-weight: 500;
        border-left: 4px solid rgba(255, 255, 255, 0.5);
        font-style: italic;
    }}
    
    .choice-prompt {{
        font-size: 18px;
        font-weight: 500;
        text-align: center;
        margin-top: 20px;
    }}
    </style>
    """

def format_negotiation_result_for_display(result, scenario_num, total_scenarios):
    """Format negotiation result for HTML display"""
    points_color = "#28a745" if result["points"] > 0 else "#dc3545" if result["points"] < 0 else "#6c757d"
    
    return f"""
    <div class="negotiation-result">
        <div class="result-header">
            <span class="scenario-progress">Scenario {scenario_num}/{total_scenarios} Complete</span>
            <span class="points-earned" style="color: {points_color}">
                {'+' if result["points"] > 0 else ''}{result["points"]} points
            </span>
        </div>
        
        <div class="result-feedback">
            {result["feedback"]}
        </div>
        
        <div class="result-outcome">
            <strong>Outcome:</strong> {result["outcome"]}
        </div>
        
        {f'<div class="salary-impact">💰 Potential value: ${result["salary_impact"]:,}</div>' if result["salary_impact"] > 0 else ''}
    </div>
    
    <style>
    .negotiation-result {{
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        border-radius: 16px;
        padding: 24px;
        margin: 20px 0;
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    
    .result-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }}
    
    .points-earned {{
        font-size: 20px;
        font-weight: 700;
        background: rgba(255, 255, 255, 0.2);
        padding: 8px 16px;
        border-radius: 20px;
    }}
    
    .result-feedback {{
        font-size: 18px;
        font-weight: 500;
        margin-bottom: 12px;
        line-height: 1.4;
    }}
    
    .result-outcome {{
        font-size: 16px;
        margin-bottom: 12px;
        opacity: 0.9;
        line-height: 1.4;
    }}
    
    .salary-impact {{
        background: rgba(255, 255, 255, 0.15);
        border-radius: 8px;
        padding: 12px;
        font-size: 16px;
        font-weight: 500;
        text-align: center;
    }}
    </style>
    """

def format_final_negotiation_assessment(assessment):
    """Format final negotiation assessment for HTML display"""
    return f"""
    <div class="final-assessment">
        <div class="assessment-header">
            <h2>🎉 Your Negotiation Profile</h2>
        </div>
        
        <div class="negotiation-style">
            <h3>{assessment['style']}</h3>
            <p>{assessment['style_description']}</p>
        </div>
        
        <div class="assessment-stats">
            <div class="stat-box">
                <span class="stat-value">${assessment['potential_annual_gain']:,}</span>
                <span class="stat-label">Potential Annual Gain</span>
            </div>
            <div class="stat-box">
                <span class="stat-value">{assessment['success_rate']:.0f}%</span>
                <span class="stat-label">Success Rate</span>
            </div>
            <div class="stat-box">
                <span class="stat-value">{assessment['total_score']}</span>
                <span class="stat-label">Total Points</span>
            </div>
        </div>
        
        <div class="key-insight">
            <h4>💡 Key Insight</h4>
            <p>{assessment['key_insight']}</p>
        </div>
    </div>
    
    <style>
    .final-assessment {{
        background: linear-gradient(135deg, #6f42c1 0%, #e83e8c 100%);
        color: white;
        border-radius: 20px;
        padding: 40px;
        margin: 24px 0;
        font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
        text-align: center;
    }}
    
    .assessment-header h2 {{
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 32px;
        line-height: 1.2;
    }}
    
    .negotiation-style {{
        margin-bottom: 32px;
    }}
    
    .negotiation-style h3 {{
        font-size: 28px;
        font-weight: 600;
        margin-bottom: 12px;
    }}
    
    .negotiation-style p {{
        font-size: 18px;
        opacity: 0.9;
        line-height: 1.4;
    }}
    
    .assessment-stats {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 24px;
        margin-bottom: 32px;
    }}
    
    .stat-box {{
        background: rgba(255, 255, 255, 0.15);
        border-radius: 12px;
        padding: 20px;
        backdrop-filter: blur(10px);
    }}
    
    .stat-value {{
        display: block;
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 8px;
    }}
    
    .stat-label {{
        font-size: 14px;
        opacity: 0.8;
        font-weight: 500;
    }}
    
    .key-insight {{
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 24px;
    }}
    
    .key-insight h4 {{
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 12px;
    }}
    
    .key-insight p {{
        font-size: 18px;
        line-height: 1.4;
    }}
    </style>
    """

def get_rotating_news():
    """Get a random job market news headline"""
    return random.choice(JOB_MARKET_NEWS)

def get_glassmorphism_css():
    """Get Apple-style CSS that replicates Apple website design"""
    return """
    <style>
        /* Apple Design System - Reset & Base */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            color: #1d1d1f;
            background-color: #fff;
            line-height: 1.47059;
            font-weight: 400;
            letter-spacing: -0.022em;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }
        
        .gradio-container {
            max-width: none !important;
            margin: 0 !important;
            padding: 0 !important;
            background: #fff !important;
        }
        
        /* Apple Navigation */
        .apple-nav {
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: saturate(180%) blur(20px);
            border-bottom: 1px solid rgba(0, 0, 0, 0.1);
            position: sticky;
            top: 0;
            z-index: 1000;
            padding: 12px 0;
        }
        
        .nav-container {
            max-width: 980px;
            margin: 0 auto;
            padding: 0 22px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .nav-logo {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .logo-icon {
            font-size: 20px;
        }
        
        .logo-text {
            font-size: 21px;
            font-weight: 600;
            color: #1d1d1f;
            letter-spacing: -0.022em;
        }
        
        .nav-links {
            display: flex;
            gap: 44px;
        }
        
        .nav-links a {
            color: #1d1d1f;
            text-decoration: none;
            font-size: 17px;
            font-weight: 400;
            letter-spacing: -0.022em;
            transition: color 0.2s ease;
        }
        
        .nav-links a:hover {
            color: #0071e3;
        }
        
        .nav-cta, .nav-back {
            background: #0071e3;
            color: white;
            border: none;
            border-radius: 20px;
            padding: 8px 16px;
            font-size: 17px;
            font-weight: 400;
            letter-spacing: -0.022em;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .nav-back {
            background: transparent;
            color: #0071e3;
            border: 1px solid #0071e3;
        }
        
        .nav-cta:hover {
            background: #0077ed;
        }
        
        .nav-back:hover {
            background: #0071e3;
            color: white;
        }
        
        /* Apple Hero Section */
        .apple-hero {
            background: #fff;
            padding: 80px 0 120px 0;
            text-align: center;
        }
        
        .hero-container {
            max-width: 980px;
            margin: 0 auto;
            padding: 0 22px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 80px;
            align-items: center;
        }
        
        .hero-content {
            text-align: left;
        }
        
        .hero-headline {
            font-size: 56px;
            line-height: 1.07143;
            font-weight: 600;
            letter-spacing: -0.005em;
            color: #1d1d1f;
            margin-bottom: 28px;
        }
        
        .hero-highlight {
            color: #0071e3;
        }
        
        .hero-subheading {
            font-size: 28px;
            line-height: 1.14286;
            font-weight: 400;
            letter-spacing: 0.007em;
            color: #86868b;
            margin-bottom: 28px;
        }
        
        .hero-ctas {
            display: flex;
            gap: 24px;
            margin-bottom: 16px;
            align-items: center;
        }
        
        .btn-primary {
            background: #0071e3;
            color: white;
            border: none;
            border-radius: 20px;
            padding: 12px 24px;
            font-size: 17px;
            font-weight: 400;
            letter-spacing: -0.022em;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn-primary.large {
            padding: 16px 32px;
            font-size: 21px;
        }
        
        .btn-primary.xlarge {
            padding: 20px 40px;
            font-size: 24px;
            font-weight: 500;
        }
        
        .btn-primary:hover {
            background: #0077ed;
        }
        
        .btn-secondary {
            color: #0071e3;
            text-decoration: none;
            font-size: 21px;
            font-weight: 400;
            letter-spacing: -0.022em;
            transition: color 0.2s ease;
        }
        
        .btn-secondary:hover {
            color: #0077ed;
            text-decoration: underline;
        }
        
        .hero-note {
            font-size: 14px;
            color: #86868b;
            font-weight: 400;
            letter-spacing: -0.016em;
        }
        
        /* Hero Visual */
        .hero-visual {
            display: flex;
            justify-content: center;
        }
        
        .mockup-container {
            width: 320px;
            height: 400px;
            position: relative;
        }
        
        .mockup-screen {
            width: 100%;
            height: 100%;
            background: #f5f5f7;
            border-radius: 20px;
            border: 1px solid #d2d2d7;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        
        .mockup-header {
            background: #fff;
            padding: 16px;
            border-bottom: 1px solid #d2d2d7;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .mockup-dots {
            display: flex;
            gap: 6px;
        }
        
        .mockup-dots span {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #d2d2d7;
        }
        
        .mockup-dots span:first-child { background: #ff5f57; }
        .mockup-dots span:nth-child(2) { background: #ffbd2e; }
        .mockup-dots span:last-child { background: #28ca42; }
        
        .mockup-title {
            font-size: 14px;
            font-weight: 600;
            color: #1d1d1f;
        }
        
        .mockup-content {
            padding: 24px 16px;
        }
        
        .analysis-card {
            background: #fff;
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            margin-bottom: 16px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
        }
        
        .match-score {
            font-size: 48px;
            font-weight: 700;
            color: #0071e3;
            line-height: 1;
        }
        
        .match-label {
            font-size: 14px;
            color: #86868b;
            margin-top: 4px;
        }
        
        .skills-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .skill-item {
            background: #fff;
            border-radius: 8px;
            padding: 12px;
            font-size: 14px;
            font-weight: 500;
            box-shadow: 0 1px 5px rgba(0, 0, 0, 0.05);
        }
        
        /* Apple Features Section */
        .apple-features {
            background: #f5f5f7;
            padding: 120px 0;
        }
        
        .section-container {
            max-width: 980px;
            margin: 0 auto;
            padding: 0 22px;
        }
        
        .section-header {
            text-align: center;
            margin-bottom: 80px;
        }
        
        .section-title {
            font-size: 48px;
            line-height: 1.08349;
            font-weight: 600;
            letter-spacing: -0.003em;
            color: #1d1d1f;
            margin-bottom: 20px;
        }
        
        .section-subtitle {
            font-size: 21px;
            line-height: 1.381;
            font-weight: 400;
            letter-spacing: 0.011em;
            color: #86868b;
        }
        
        .features-grid {
            display: grid;
            grid-template-columns: 2fr 1fr 1fr;
            grid-template-rows: 1fr 1fr;
            gap: 20px;
            height: 600px;
        }
        
        .feature-card {
            background: #fff;
            border-radius: 18px;
            padding: 40px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
        }
        
        .feature-card.large {
            grid-row: 1 / 3;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            align-items: center;
        }
        
        .feature-content h3 {
            font-size: 32px;
            line-height: 1.125;
            font-weight: 600;
            letter-spacing: 0.004em;
            color: #1d1d1f;
            margin-bottom: 16px;
        }
        
        .feature-content p {
            font-size: 19px;
            line-height: 1.42105;
            font-weight: 400;
            letter-spacing: 0.012em;
            color: #86868b;
            margin-bottom: 20px;
        }
        
        .feature-stat {
            font-size: 21px;
            font-weight: 600;
            color: #0071e3;
        }
        
        .feature-card h3 {
            font-size: 24px;
            line-height: 1.16667;
            font-weight: 600;
            color: #1d1d1f;
            margin-bottom: 12px;
        }
        
        .feature-card p {
            font-size: 17px;
            line-height: 1.47059;
            font-weight: 400;
            color: #86868b;
        }
        
        .feature-icon {
            font-size: 40px;
            margin-bottom: 20px;
        }
        
        .feature-visual {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .chart-container {
            width: 120px;
            height: 120px;
        }
        
        .progress-ring {
            position: relative;
            width: 100%;
            height: 100%;
        }
        
        .progress-ring svg {
            width: 100%;
            height: 100%;
        }
        
        .ring-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 24px;
            font-weight: 700;
            color: #0071e3;
        }
        
        /* How It Works Section */
        .how-it-works {
            background: #fff;
            padding: 120px 0;
        }
        
        .section-header.center {
            text-align: center;
            margin-bottom: 80px;
        }
        
        .steps-container {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 60px;
        }
        
        .step-item {
            text-align: center;
        }
        
        .step-number {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 40px;
            height: 40px;
            background: #0071e3;
            color: white;
            border-radius: 50%;
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 24px;
        }
        
        .step-visual {
            margin-bottom: 24px;
        }
        
        .document-icon, .target-icon, .magic-icon {
            font-size: 80px;
            opacity: 0.8;
        }
        
        .step-item h3 {
            font-size: 24px;
            line-height: 1.16667;
            font-weight: 600;
            color: #1d1d1f;
            margin-bottom: 12px;
        }
        
        .step-item p {
            font-size: 17px;
            line-height: 1.47059;
            color: #86868b;
        }
        
        /* Apple CTA Section */
        .apple-cta {
            background: #f5f5f7;
            padding: 120px 0;
            text-align: center;
        }
        
        .cta-title {
            font-size: 48px;
            line-height: 1.08349;
            font-weight: 600;
            letter-spacing: -0.003em;
            color: #1d1d1f;
            margin-bottom: 20px;
        }
        
        .cta-subtitle {
            font-size: 21px;
            line-height: 1.381;
            color: #86868b;
            margin-bottom: 40px;
        }
        
        .cta-note {
            font-size: 14px;
            color: #86868b;
            margin-top: 16px;
        }
        
        /* Apple Footer */
        .apple-footer {
            background: #f5f5f7;
            padding: 40px 0;
            border-top: 1px solid #d2d2d7;
        }
        
        .footer-container {
            max-width: 980px;
            margin: 0 auto;
            padding: 0 22px;
        }
        
        .footer-content {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 40px;
            margin-bottom: 40px;
        }
        
        .footer-section h4 {
            font-size: 17px;
            font-weight: 600;
            color: #1d1d1f;
            margin-bottom: 16px;
        }
        
        .footer-section ul {
            list-style: none;
        }
        
        .footer-section li {
            margin-bottom: 8px;
        }
        
        .footer-section a {
            color: #86868b;
            text-decoration: none;
            font-size: 14px;
            transition: color 0.2s ease;
        }
        
        .footer-section a:hover {
            color: #0071e3;
        }
        
        .footer-bottom {
            text-align: center;
            padding-top: 20px;
            border-top: 1px solid #d2d2d7;
        }
        
        .footer-bottom p {
            font-size: 12px;
            color: #86868b;
        }
        
        /* App Page Styles */
        .app-hero {
            background: #fff;
            padding: 60px 0;
            text-align: center;
        }
        
        .app-title {
            font-size: 48px;
            line-height: 1.08349;
            font-weight: 600;
            letter-spacing: -0.003em;
            color: #1d1d1f;
            margin-bottom: 20px;
        }
        
        .app-subtitle {
            font-size: 21px;
            line-height: 1.381;
            color: #86868b;
        }
        
        /* Form Styles */
        .input-section {
            background: #f5f5f7;
            padding: 60px 0;
        }
        
        .form-container {
            max-width: 980px;
            margin: 0 auto;
            padding: 0 22px;
        }
        
        .form-header {
            text-align: center;
            margin-bottom: 60px;
        }
        
        .form-header h2 {
            font-size: 40px;
            font-weight: 600;
            color: #1d1d1f;
            margin-bottom: 16px;
        }
        
        .form-header p {
            font-size: 19px;
            color: #86868b;
        }
        
        .apple-form-grid {
            max-width: 980px;
            margin: 0 auto;
            padding: 0 22px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 60px;
        }
        
        .form-column {
            background: #fff;
            border-radius: 18px;
            padding: 40px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        }
        
        .form-section {
            margin-bottom: 24px;
        }
        
        .form-title {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 24px;
            font-weight: 600;
            color: #1d1d1f;
            margin-bottom: 8px;
        }
        
        .form-icon {
            font-size: 24px;
        }
        
        .form-description {
            font-size: 17px;
            color: #86868b;
        }
        
        .form-divider {
            text-align: center;
            font-size: 14px;
            color: #86868b;
            margin: 20px 0;
        }
        
        /* Apple Form Controls */
        .apple-textarea, .apple-input {
            width: 100% !important;
            border: 1px solid #d2d2d7 !important;
            border-radius: 12px !important;
            padding: 16px !important;
            font-size: 17px !important;
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif !important;
            background: #fff !important;
            color: #1d1d1f !important;
            transition: border-color 0.2s ease !important;
            resize: vertical !important;
        }
        
        .apple-textarea:focus, .apple-input:focus {
            outline: none !important;
            border-color: #0071e3 !important;
            box-shadow: 0 0 0 4px rgba(0, 113, 227, 0.1) !important;
        }
        
        .apple-file-input {
            border: 2px dashed #d2d2d7 !important;
            border-radius: 12px !important;
            padding: 40px 20px !important;
            text-align: center !important;
            background: #f5f5f7 !important;
            transition: all 0.2s ease !important;
        }
        
        .apple-file-input:hover {
            border-color: #0071e3 !important;
            background: rgba(0, 113, 227, 0.05) !important;
        }
        
        /* Action Section */
        .action-section {
            padding: 60px 0;
            text-align: center;
        }
        
        .button-container h3 {
            font-size: 32px;
            font-weight: 600;
            color: #1d1d1f;
            margin-bottom: 40px;
        }
        
        .action-buttons {
            max-width: 600px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        
        .apple-button {
            border-radius: 12px !important;
            padding: 20px 24px !important;
            font-size: 17px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
            border: none !important;
            cursor: pointer !important;
        }
        
        .apple-button.primary {
            background: #0071e3 !important;
            color: white !important;
        }
        
        .apple-button.primary:hover {
            background: #0077ed !important;
            transform: translateY(-2px);
        }
        
        .apple-button.secondary {
            background: #fff !important;
            color: #0071e3 !important;
            border: 1px solid #0071e3 !important;
        }
        
        .apple-button.secondary:hover {
            background: #0071e3 !important;
            color: white !important;
            transform: translateY(-2px);
        }
        
        /* Results Section */
        .results-section {
            max-width: 980px;
            margin: 0 auto;
            padding: 40px 22px;
        }
        
        .error-message, .success-message {
            background: #fff;
            border-radius: 18px;
            padding: 40px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            margin-top: 40px;
        }
        
        .error-message {
            border-left: 4px solid #ff3b30;
        }
        
        .success-message {
            border-left: 4px solid #30d158;
        }
        
        .error-message h3, .success-message h3 {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 12px;
        }
        
        .error-message h3 {
            color: #ff3b30;
        }
        
        .success-message h3 {
            color: #30d158;
        }
        
        .error-message p, .success-message p {
            font-size: 17px;
            color: #86868b;
        }
        
        .analysis-content {
            text-align: left;
            margin-top: 20px;
            font-size: 17px;
            line-height: 1.47059;
            color: #1d1d1f;
        }
        
        /* Progress Tracking Styles */
        .progress-container {
            background: #fff;
            border-radius: 18px;
            padding: 40px;
            margin: 40px auto;
            max-width: 800px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        }
        
        .progress-header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .progress-title {
            font-size: 28px;
            font-weight: 600;
            color: #1d1d1f;
            margin-bottom: 12px;
        }
        
        .progress-subtitle {
            font-size: 17px;
            color: #86868b;
        }
        
        .progress-bar-container {
            margin-bottom: 40px;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #f0f0f0;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 16px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #0071e3, #5856d6);
            border-radius: 4px;
            transition: width 0.5s ease;
        }
        
        .progress-steps {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 16px;
            margin-bottom: 40px;
        }
        
        .progress-step {
            text-align: center;
            position: relative;
        }
        
        .step-circle {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #f0f0f0;
            color: #86868b;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 16px;
            margin: 0 auto 12px auto;
            transition: all 0.3s ease;
        }
        
        .progress-step.active .step-circle {
            background: #0071e3;
            color: white;
            transform: scale(1.1);
        }
        
        .progress-step.completed .step-circle {
            background: #30d158;
            color: white;
        }
        
        .step-label {
            font-size: 14px;
            color: #86868b;
            font-weight: 500;
        }
        
        .progress-step.active .step-label {
            color: #0071e3;
            font-weight: 600;
        }
        
        .progress-step.completed .step-label {
            color: #30d158;
        }
        
        .current-status {
            text-align: center;
            padding: 20px;
            background: #f5f5f7;
            border-radius: 12px;
            margin-bottom: 40px;
        }
        
        .status-text {
            font-size: 18px;
            font-weight: 500;
            color: #1d1d1f;
            margin-bottom: 8px;
        }
        
        .status-subtext {
            font-size: 15px;
            color: #86868b;
        }
        
        /* Reddit Posts Styles */
        .reddit-section {
            margin-top: 40px;
        }
        
        .reddit-header {
            text-align: center;
            margin-bottom: 24px;
        }
        
        .reddit-title {
            font-size: 20px;
            font-weight: 600;
            color: #1d1d1f;
            margin-bottom: 8px;
        }
        
        .reddit-subtitle {
            font-size: 15px;
            color: #86868b;
        }
        
        .reddit-posts {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        
        .reddit-post {
            background: #fff;
            border: 1px solid #e5e5ea;
            border-radius: 12px;
            padding: 20px;
            transition: all 0.2s ease;
        }
        
        .reddit-post:hover {
            border-color: #0071e3;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        
        .post-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        
        .subreddit {
            background: #0071e3;
            color: white;
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
        }
        
        .post-time {
            font-size: 13px;
            color: #86868b;
        }
        
        .post-title {
            font-size: 16px;
            font-weight: 600;
            color: #1d1d1f;
            margin-bottom: 12px;
            line-height: 1.4;
        }
        
        .post-stats {
            display: flex;
            gap: 16px;
            font-size: 14px;
            color: #86868b;
        }
        
        .upvotes, .comments {
            display: flex;
            align-items: center;
            gap: 4px;
        }
        
        /* Formatted Output Styles */
        .interview-guide-output {
            background: #fff;
            border-radius: 18px;
            padding: 40px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            line-height: 1.6;
        }
        
        .interview-guide-output h1, .interview-guide-output h2, .interview-guide-output h3 {
            color: #1d1d1f;
            font-weight: 600;
            margin-top: 32px;
            margin-bottom: 16px;
        }
        
        .interview-guide-output h1 {
            font-size: 32px;
            border-bottom: 2px solid #0071e3;
            padding-bottom: 16px;
            margin-top: 0;
        }
        
        .interview-guide-output h2 {
            font-size: 24px;
            color: #0071e3;
        }
        
        .interview-guide-output h3 {
            font-size: 20px;
        }
        
        .interview-guide-output ul, .interview-guide-output ol {
            margin: 16px 0;
            padding-left: 24px;
        }
        
        .interview-guide-output li {
            margin-bottom: 8px;
        }
        
        .interview-guide-output strong {
            color: #1d1d1f;
            font-weight: 600;
        }
        
        .interview-guide-output .match-score {
            background: linear-gradient(135deg, #30d158, #0071e3);
            color: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            margin: 24px 0;
        }
        
        .interview-guide-output .score-number {
            font-size: 48px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        
        .interview-guide-output .score-label {
            font-size: 18px;
            opacity: 0.9;
        }
        
        /* Responsive Design */
        @media (max-width: 1068px) {
            .hero-container, .features-grid, .steps-container, .apple-form-grid {
                grid-template-columns: 1fr;
                gap: 40px;
            }
            
            .hero-content {
                text-align: center;
            }
            
            .hero-headline {
                font-size: 40px;
            }
            
            .section-title, .cta-title, .app-title {
                font-size: 32px;
            }
            
            .nav-links {
                display: none;
            }
            
            .progress-steps {
                grid-template-columns: 1fr;
                gap: 12px;
            }
            
            .progress-step {
                display: flex;
                align-items: center;
                text-align: left;
                gap: 16px;
            }
            
            .step-circle {
                margin: 0;
            }
        }
        
        @media (max-width: 734px) {
            .nav-container, .section-container, .form-container {
                padding: 0 16px;
            }
            
            .hero-headline {
                font-size: 32px;
            }
            
            .hero-subheading {
                font-size: 21px;
            }
            
            .section-title {
                font-size: 28px;
            }
        }
        
        /* Enhanced Reddit Posts Styling */
        .reddit-posts-enhanced {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            max-height: 600px;
            overflow-y: auto;
        }
        
        .reddit-post-enhanced {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1rem;
            transition: all 0.3s ease;
        }
        
        .reddit-post-enhanced:hover {
            background: rgba(255, 255, 255, 0.08);
            border-color: rgba(255, 255, 255, 0.2);
            transform: translateY(-1px);
        }
        
        .post-header-enhanced {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
        }
        
        .subreddit-info {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .subreddit-name {
            font-weight: 600;
            color: #007AFF;
            font-size: 0.9rem;
        }
        
        .post-flair {
            background: rgba(0, 122, 255, 0.2);
            color: #007AFF;
            padding: 0.2rem 0.5rem;
            border-radius: 6px;
            font-size: 0.7rem;
            font-weight: 500;
        }
        
        .post-meta {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .post-time {
            color: rgba(255, 255, 255, 0.6);
            font-size: 0.8rem;
        }
        
        .refresh-post-btn {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 6px;
            padding: 0.3rem 0.5rem;
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .refresh-post-btn:hover {
            background: rgba(255, 255, 255, 0.15);
            border-color: rgba(255, 255, 255, 0.3);
            transform: rotate(180deg);
        }
        
        .post-title-enhanced {
            margin: 0 0 0.75rem 0;
            font-size: 1rem;
            font-weight: 600;
            line-height: 1.3;
        }
        
        .post-title-enhanced a {
            color: rgba(255, 255, 255, 0.9);
            text-decoration: none;
            transition: color 0.2s ease;
        }
        
        .post-title-enhanced a:hover {
            color: #007AFF;
        }
        
        .post-content-enhanced {
            color: rgba(255, 255, 255, 0.7);
            font-size: 0.9rem;
            line-height: 1.5;
            margin-bottom: 0.75rem;
            background: rgba(0, 0, 0, 0.2);
            padding: 0.75rem;
            border-radius: 8px;
            border-left: 3px solid rgba(0, 122, 255, 0.3);
        }
        
        .post-stats-enhanced {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 0.5rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .stats-left {
            display: flex;
            gap: 1rem;
            align-items: center;
        }
        
        .stats-left span {
            color: rgba(255, 255, 255, 0.6);
            font-size: 0.8rem;
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }
        
        .view-full-btn {
            color: #007AFF;
            text-decoration: none;
            font-size: 0.8rem;
            font-weight: 500;
            padding: 0.4rem 0.8rem;
            border: 1px solid rgba(0, 122, 255, 0.3);
            border-radius: 6px;
            transition: all 0.2s ease;
        }
        
        .view-full-btn:hover {
            background: rgba(0, 122, 255, 0.1);
            border-color: rgba(0, 122, 255, 0.5);
        }
        
        /* Reddit Widget Cards - Top Display */
        .reddit-widgets-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .reddit-widget-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 1rem;
            transition: all 0.2s ease;
            min-height: 140px;
            display: flex;
            flex-direction: column;
        }
        
        .reddit-widget-card:hover {
            background: rgba(255, 255, 255, 0.08);
            border-color: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        
        .widget-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }
        
        .widget-subreddit {
            font-weight: 600;
            color: #007AFF;
            font-size: 0.8rem;
        }
        
        .widget-actions {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .widget-time {
            color: rgba(255, 255, 255, 0.5);
            font-size: 0.7rem;
        }
        
        .widget-refresh-btn {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 4px;
            padding: 0.2rem 0.4rem;
            color: rgba(255, 255, 255, 0.7);
            font-size: 0.7rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .widget-refresh-btn:hover {
            background: rgba(255, 255, 255, 0.15);
            transform: rotate(180deg);
        }
        
        .widget-title {
            margin: 0 0 0.5rem 0;
            font-size: 0.9rem;
            font-weight: 600;
            line-height: 1.2;
            flex-grow: 1;
        }
        
        .widget-title a {
            color: rgba(255, 255, 255, 0.9);
            text-decoration: none;
            transition: color 0.2s ease;
        }
        
        .widget-title a:hover {
            color: #007AFF;
        }
        
        .widget-content {
            color: rgba(255, 255, 255, 0.7);
            font-size: 0.8rem;
            line-height: 1.3;
            margin: 0 0 0.75rem 0;
            flex-grow: 1;
        }
        
        .widget-stats {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 0.5rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            margin-top: auto;
        }
        
        .widget-stats span {
            color: rgba(255, 255, 255, 0.6);
            font-size: 0.7rem;
        }
        
        .widget-link {
            color: #007AFF;
            text-decoration: none;
            font-size: 0.7rem;
            font-weight: 500;
            padding: 0.2rem 0.4rem;
            border: 1px solid rgba(0, 122, 255, 0.3);
            border-radius: 4px;
            transition: all 0.2s ease;
        }
        
        .widget-link:hover {
            background: rgba(0, 122, 255, 0.1);
            border-color: rgba(0, 122, 255, 0.5);
        }
        
        .reddit-widgets-loading {
            text-align: center;
            padding: 2rem;
            color: rgba(255, 255, 255, 0.6);
            font-style: italic;
        }
        
        /* Salary Negotiation Simulator Additional Styles */
        .negotiation-section {
            margin: 24px 0;
        }
        
        .scenario-choices-container {
            display: grid;
            gap: 12px;
            margin-top: 20px;
        }
        
        .choice-button {
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 16px;
            color: white;
            font-size: 16px;
            text-align: left;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .choice-button:hover {
            background: rgba(255, 255, 255, 0.2);
            border-color: rgba(255, 255, 255, 0.4);
            transform: translateY(-2px);
        }
        
        .choice-button.selected {
            background: rgba(0, 71, 227, 0.3);
            border-color: #0071e3;
        }
        
        /* AI Typing Simulator Enhanced Styles */
        .typing-section {
            margin: 20px 0;
            animation: fadeInUp 0.5s ease;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .typing-container {
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 16px;
            padding: 24px;
            margin: 16px 0;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            position: relative;
            overflow: hidden;
        }
        
        .typing-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, #0071e3, #5856d6);
            animation: typing-progress 3s ease-in-out infinite;
        }
        
        @keyframes typing-progress {
            0%, 100% { transform: translateX(-100%); }
            50% { transform: translateX(100%); }
        }
        
        .typing-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 20px;
        }
        
        .ai-avatar {
            width: 45px;
            height: 45px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            font-size: 16px;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        
        .typing-status {
            color: #0071e3;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 18px;
        }
        
        .typing-dots {
            display: inline-flex;
            gap: 4px;
        }
        
        .typing-dots span {
            width: 6px;
            height: 6px;
            background: #0071e3;
            border-radius: 50%;
            animation: typing-pulse 1.4s infinite ease-in-out;
        }
        
        .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
        .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
        .typing-dots span:nth-child(3) { animation-delay: 0s; }
        
        @keyframes typing-pulse {
            0%, 80%, 100% { 
                opacity: 0.3;
                transform: scale(0.8);
            }
            40% { 
                opacity: 1;
                transform: scale(1.2);
            }
        }
        
        .question-being-typed {
            background: white;
            border-radius: 12px;
            padding: 20px;
            border-left: 4px solid #0071e3;
            font-size: 16px;
            line-height: 1.6;
            min-height: 60px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
            position: relative;
        }
        
        .typed-cursor {
            display: inline-block;
            width: 3px;
            height: 22px;
            background: #0071e3;
            animation: cursor-blink 1s infinite;
            margin-left: 2px;
            border-radius: 1px;
        }
        
        @keyframes cursor-blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }
        
        .question-complete {
            background: white;
            border-radius: 12px;
            padding: 20px;
            border-left: 4px solid #28a745;
            margin-bottom: 12px;
            font-size: 16px;
            line-height: 1.6;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
            animation: slideInLeft 0.5s ease;
        }
        
        @keyframes slideInLeft {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .question-category {
            font-size: 14px;
            color: #6c757d;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 16px;
            padding: 8px 12px;
            background: rgba(108, 117, 125, 0.1);
            border-radius: 6px;
            display: inline-block;
        }
        
        /* Progress indicators for typing simulation */
        .typing-progress {
            display: flex;
            justify-content: center;
            gap: 8px;
            margin: 20px 0;
        }
        
        .progress-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: rgba(0, 71, 227, 0.3);
            animation: progress-pulse 2s ease-in-out infinite;
        }
        
        .progress-dot.active {
            background: #0071e3;
            animation: progress-pulse-active 1s ease-in-out infinite;
        }
        
        @keyframes progress-pulse {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 0.7; }
        }
        
        @keyframes progress-pulse-active {
            0%, 100% { 
                opacity: 1;
                transform: scale(1);
            }
            50% { 
                opacity: 0.8;
                transform: scale(1.2);
            }
        }
        
        /* Mobile responsiveness for simulators */
        @media (max-width: 768px) {
            .negotiation-scenario, .negotiation-result, .final-assessment {
                padding: 20px;
                margin: 16px 0;
            }
            
            .scenario-title {
                font-size: 22px;
            }
            
            .assessment-stats {
                grid-template-columns: 1fr;
                gap: 16px;
            }
            
            .typing-container {
                padding: 16px;
            }
            
            .ai-avatar {
                width: 35px;
                height: 35px;
                font-size: 14px;
            }
            
            .typing-status {
                font-size: 16px;
            }
        }
    </style>
    """

def create_progress_display(current_step: int = 0, total_steps: int = 6):
    """Create a modern progress display with steps"""
    steps = [
        "🔍 Processing Job Description",
        "🎯 Analyzing Requirements", 
        "📋 Parsing Resume",
        "⚖️ Gap Analysis",
        "✨ Generating Guide",
        "🎨 Finalizing Results"
    ]
    
    progress_html = f"""
    <div class="progress-container">
        <div style="text-align: center; margin-bottom: 1rem;">
            <h3 style="color: #e2e8f0; margin: 0;">Processing Your Interview Guide</h3>
            <p style="color: #94a3b8; margin: 0.5rem 0;">Step {min(current_step + 1, total_steps)} of {total_steps}</p>
        </div>
        <div style="background: rgba(255,255,255,0.1); height: 4px; border-radius: 2px; margin: 1rem 0;">
            <div style="background: linear-gradient(90deg, #667eea, #764ba2); height: 100%; width: {(current_step + 1)/total_steps * 100}%; border-radius: 2px; transition: width 0.5s ease;"></div>
        </div>
    """
    
    for i, step in enumerate(steps):
        if i < current_step:
            status_class = "step-completed"
            icon = "✓"
        elif i == current_step:
            status_class = "step-active"
            icon = str(i + 1)
        else:
            status_class = ""
            icon = str(i + 1)
            
        progress_html += f"""
        <div class="{status_class}">
            <div class="step-circle">{icon}</div>
            <div class="step-label">{step}</div>
        </div>
        """
    
    progress_html += "</div>"
    return progress_html

def create_news_ticker():
    """Create a rotating news ticker with JavaScript cycling"""
    news_items = JOB_MARKET_NEWS
    # Properly escape quotes for JavaScript
    news_js = ", ".join([f'"{item.replace('"', '\\"')}"' for item in news_items])
    
    return f"""
    <div class="news-ticker" id="news-ticker">
        <div class="news-text" id="news-text"></div>
    </div>
    <script>
        (function() {{
            const newsItems = [{news_js}];
            let currentIndex = 0;
            const newsElement = document.getElementById('news-text');
            
            function updateNews() {{
                if (newsElement) {{
                    // Set the current news item
                    newsElement.textContent = newsItems[currentIndex];
                    
                    // Reset animation
                    newsElement.style.animation = 'none';
                    
                    // Force reflow to restart animation
                    newsElement.offsetHeight;
                    
                    // Start animation
                    newsElement.style.animation = 'scroll-left 25s linear infinite';
                    
                    // Move to next item
                    currentIndex = (currentIndex + 1) % newsItems.length;
                }}
            }}
            
            // Initialize with first news item
            if (newsElement) {{
                updateNews();
                
                // Update news every 25 seconds to match animation duration
                setInterval(updateNews, 25000);
            }}
        }})();
    </script>
    """

async def fetch_raw(raw_text: str, raw_url: str) -> str:
    """Fetch raw job description from text input or URL."""
    # Priority: URL first, then text
    input_source = raw_url.strip() if raw_url.strip() else raw_text.strip()
    
    if not input_source:
        raise ValueError("No input provided")
    
    # If it's a URL, fetch content
    if input_source.startswith(('http://', 'https://')):
        # Check for LinkedIn detection
        if "linkedin.com/jobs" in input_source:
            import requests
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
                response = requests.get(input_source, headers=headers, timeout=10)
                if len(response.text) < 1000 or "authwall" in response.text.lower():
                    return f"⚠️ LinkedIn requires login. Please copy-paste the job description text instead.\n\nURL attempted: {input_source}"
                return response.text
            except Exception as e:
                return f"❌ Failed to fetch URL: {str(e)}\n\nPlease copy-paste the job description text instead."
        
        # For other URLs, try to fetch
        try:
            import requests
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
            response = requests.get(input_source, headers=headers, timeout=10)
            return response.text
        except Exception as e:
            return f"❌ Failed to fetch URL: {str(e)}\n\nPlease copy-paste the job description text instead."
    
    # Return raw text
    return input_source

async def run_job(raw_text: str, raw_url: str):
    """No-BS job analysis with streaming."""
    try:
        # Show skeleton immediately
        yield renderer_nobs.skeleton()
        
        # Fetch raw content
        raw = await fetch_raw(raw_text, raw_url)
        
        # Check for error messages
        if raw.startswith(('❌', '⚠️')):
            yield f"<div class='p-4 text-red-600'>{raw}</div>"
            return
        
        # Extract using No-BS format
        data = await extract_nobs(raw)
        
        # Generate final HTML
        final_html = renderer_nobs.to_html(data)
        yield final_html
        
    except Exception as e:
        yield f"<div class='p-4 text-red-600'>❌ Analysis failed: {str(e)}</div>"

def get_pipeline():
    """Create the analysis pipeline with all micro-functions"""
    from micro.scrape import ScrapeMicroFunction
    from micro.enrich import EnrichMicroFunction
    from micro.draft import DraftMicroFunction
    from micro.qa import QAMicroFunction
    from micro.critique import CritiqueMicroFunction
    from micro.bucket_enrich import BucketEnrichMicroFunction
    from micro.render import RenderMicroFunction
    
    return [
        ScrapeMicroFunction(),
        EnrichMicroFunction(),
        DraftMicroFunction(),
        QAMicroFunction(),
        CritiqueMicroFunction(),
        BucketEnrichMicroFunction(),
        RenderMicroFunction(),
    ]

def run_job_wrapper(raw_text: str, raw_url: str):
    """Sync wrapper for async job analysis"""
    
    async def run_analysis():
        final_result = None
        async for result in run_job(raw_text, raw_url):
            final_result = result
        return final_result
    
    return asyncio.run(run_analysis())

async def generate_interview_guide_wrapper(resume_text: str, resume_file, job_url: str, job_text: str, progress=gr.Progress()):
    """Enhanced interview guide generation with modern progress tracking"""
    
    try:
        # Input validation
        if not resume_text and not resume_file:
            error_html = """
            <div class="glass-container" style="background: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.3);">
                <h3 style="color: #fca5a5;">❌ Resume Required</h3>
                <p style="color: #fecaca;">Please provide your resume text or upload a resume file.</p>
    </div>
    """
            yield error_html, "❌ Resume required"
            return
        
        if not job_url and not job_text:
            error_html = """
            <div class="glass-container" style="background: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.3);">
                <h3 style="color: #fca5a5;">❌ Job Description Required</h3>
                <p style="color: #fecaca;">Please provide a job URL or paste the job description.</p>
            </div>
            """
            yield error_html, "❌ Job description required"
            return
        
        # Initialize progress with modern display
        current_step = 0
        total_steps = 6
        
        # Step 1: Process inputs
        progress_html = get_glassmorphism_css() + create_progress_display(current_step, total_steps) + create_news_ticker()
        yield progress_html, "🔍 Processing inputs..."
        
        # Get resume text
        if resume_file and not resume_text:
            with open(resume_file, 'r', encoding='utf-8') as f:
                resume_text = f.read()
        
        # Get job description
        if job_url and not job_text:
            job_text = await fetch_raw("", job_url)
        
        current_step = 1
        progress_html = get_glassmorphism_css() + create_progress_display(current_step, total_steps) + create_news_ticker()
        yield progress_html, "🎯 Analyzing job requirements..."
        
        # Create orchestrator
        orchestrator = EnhancedInterviewOrchestrator()
        
        # Step 2-6: Run enhanced pipeline with progress updates
        for step in range(2, total_steps):
            current_step = step
            progress_html = get_glassmorphism_css() + create_progress_display(current_step, total_steps) + create_news_ticker()
            
            status_messages = [
                "📋 Parsing your resume...",
                "⚖️ Conducting gap analysis...", 
                "✨ Generating personalized guide...",
                "🎨 Finalizing your interview strategy..."
            ]
            
            yield progress_html, status_messages[step - 2]
            await asyncio.sleep(0.5)  # Brief pause for UX
        
        # Generate the actual guide
        result = await orchestrator.create_enhanced_interview_guide(resume_text, job_text)
        
        if result.success:
            # Create final result with glass styling
            final_html = f"""
            {get_glassmorphism_css()}
            <div class="gradient-border">
                <div class="inner-glass">
                    <div style="text-align: center; margin-bottom: 2rem;">
                        <h2 style="color: #e2e8f0; margin: 0;">✅ Interview Guide Complete</h2>
                        <p style="color: #94a3b8;">Match Score: <span style="color: #10b981; font-weight: bold;">{result.match_score:.1f}%</span></p>
                    </div>
                    <div class="glass-container">
                        {result.interview_guide}
                    </div>
                </div>
        </div>
        """
    
            yield final_html, f"✅ Complete! {result.match_score:.1f}% match"
        else:
            error_html = f"""
            {get_glassmorphism_css()}
            <div class="glass-container" style="background: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.3);">
                <h3 style="color: #fca5a5;">❌ Generation Failed</h3>
                <p style="color: #fecaca;">{result.error_message or 'Unknown error occurred'}</p>
            </div>
            """
            yield error_html, f"❌ Failed: {result.error_message or 'Unknown error'}"
            
    except Exception as e:
        error_html = f"""
        {get_glassmorphism_css()}
        <div class="glass-container" style="background: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.3);">
            <h3 style="color: #fca5a5;">❌ Unexpected Error</h3>
            <p style="color: #fecaca;">{str(e)}</p>
        </div>
        """
        yield error_html, f"❌ Error: {str(e)}"

def generate_interview_guide_sync_wrapper(resume_text: str, resume_file, job_url: str, job_text: str, progress=gr.Progress()):
    """Sync wrapper for the async interview guide generation"""
    
    async def run_generation():
        final_result = None, None
        async for result in generate_interview_guide_wrapper(resume_text, resume_file, job_url, job_text, progress):
            final_result = result
        return final_result
    
    return asyncio.run(run_generation())

def create_interface():
    """Create the main interface"""
    
    # Get the custom CSS
    css = get_glassmorphism_css()
    
    with gr.Blocks(css=css, title="IQKiller - Interview Prep") as demo:
        # State management
        current_page = gr.State("landing")
        
        # Landing Page
        with gr.Column(visible=True, elem_id="landing-page") as landing_page:
            # Apple Navigation
            gr.HTML("""
                <nav class="apple-nav">
                    <div class="nav-container">
                        <div class="nav-logo">
                            <span class="logo-icon">🧠</span>
                            <span class="logo-text">IQKiller</span>
                        </div>
                        <div class="nav-links">
                            <a href="#features">Features</a>
                            <a href="#how-it-works">How it works</a>
                            <a href="#pricing">Pricing</a>
                            <a href="#support">Support</a>
                        </div>
                        <button class="nav-cta" onclick="document.getElementById('cta-button').click()">Get Started</button>
                    </div>
                </nav>
            """)
            
            # Hero Section
            gr.HTML("""
                <section class="apple-hero">
                    <div class="hero-container">
                        <div class="hero-content">
                            <h1 class="hero-headline">The interview prep that <span class="hero-highlight">changes everything.</span></h1>
                            <p class="hero-subheading">Get real AI analysis of your resume against any job posting. Know exactly what to prepare for.</p>
                            <div class="hero-ctas">
                                <button class="btn-primary xlarge" onclick="document.getElementById('cta-button').click()">Try it free</button>
                                <a href="#how-it-works" class="btn-secondary">Learn more ></a>
                            </div>
                            <p class="hero-note">No sign-up required. Get results in 30 seconds.</p>
                        </div>
                        <div class="hero-visual">
                            <div class="mockup-container">
                                <div class="mockup-screen">
                                    <div class="mockup-header">
                                        <div class="mockup-dots">
                                            <span></span>
                                            <span></span>
                                            <span></span>
                                        </div>
                                        <div class="mockup-title">Interview Analysis</div>
                                        <div></div>
                                    </div>
                                    <div class="mockup-content">
                                        <div class="analysis-card">
                                            <div class="match-score">93%</div>
                                            <div class="match-label">Match Score</div>
                                        </div>
                                        <div class="skills-list">
                                            <div class="skill-item">Python Development</div>
                                            <div class="skill-item">Machine Learning</div>
                                            <div class="skill-item">Data Analysis</div>
                                            <div class="skill-item">API Development</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
            """)
            
            # Features Section
            gr.HTML("""
                <section class="apple-features" id="features">
                    <div class="section-container">
                        <div class="section-header">
                            <h2 class="section-title">Designed for job seekers. Built for success.</h2>
                            <p class="section-subtitle">Real AI analysis that shows you exactly where you stand.</p>
                        </div>
                        <div class="features-grid">
                            <div class="feature-card large">
                                <div class="feature-content">
                                    <h3>95% accuracy in skill matching</h3>
                                    <p>Our AI analyzes your resume against job requirements with unprecedented precision, identifying strengths and gaps that matter.</p>
                                    <div class="feature-stat">30-second analysis</div>
                                </div>
                                <div class="feature-visual">
                                    <div class="chart-container">
                                        <div class="progress-ring">
                                            <svg>
                                                <circle cx="60" cy="60" r="54" fill="none" stroke="#f0f0f0" stroke-width="6"/>
                                                <circle cx="60" cy="60" r="54" fill="none" stroke="#0071e3" stroke-width="6" 
                                                        stroke-dasharray="339.3" stroke-dashoffset="33.9" transform="rotate(-90 60 60)"/>
                                            </svg>
                                            <div class="ring-text">95%</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="feature-card">
                                <div class="feature-icon">⚡</div>
                                <h3>Lightning fast</h3>
                                <p>Get comprehensive analysis in under 30 seconds. No waiting, no delays.</p>
                            </div>
                            <div class="feature-card">
                                <div class="feature-icon">🎯</div>
                                <h3>Personalized insights</h3>
                                <p>Tailored recommendations based on your actual experience and the specific role.</p>
                            </div>
                            <div class="feature-card">
                                <div class="feature-icon">🔒</div>
                                <h3>Privacy first</h3>
                                <p>Your data is processed securely and never stored or shared.</p>
                            </div>
                            <div class="feature-card">
                                <div class="feature-icon">📊</div>
                                <h3>Real metrics</h3>
                                <p>Get actual match percentages and skill confidence scores, not vague feedback.</p>
                            </div>
                        </div>
                    </div>
                </section>
            """)
            
            # How It Works Section
            gr.HTML("""
                <section class="how-it-works" id="how-it-works">
                    <div class="section-container">
                        <div class="section-header center">
                            <h2 class="section-title">How it works</h2>
                            <p class="section-subtitle">Three simple steps to interview readiness.</p>
                        </div>
                        <div class="steps-container">
                            <div class="step-item">
                                <div class="step-number">1</div>
                                <div class="step-visual">
                                    <div class="document-icon">📄</div>
                                </div>
                                <h3>Upload your resume</h3>
                                <p>Paste your resume text or upload a PDF. Our AI extracts and analyzes your skills and experience.</p>
                            </div>
                            <div class="step-item">
                                <div class="step-number">2</div>
                                <div class="step-visual">
                                    <div class="target-icon">🎯</div>
                                </div>
                                <h3>Add the job posting</h3>
                                <p>Paste the job URL or description. We'll analyze the requirements and expectations.</p>
                            </div>
                            <div class="step-item">
                                <div class="step-number">3</div>
                                <div class="step-visual">
                                    <div class="magic-icon">✨</div>
                                </div>
                                <h3>Get your guide</h3>
                                <p>Receive a personalized interview guide with your match score, strengths, and areas to focus on.</p>
                            </div>
                        </div>
                    </div>
                </section>
            """)
            
            # CTA Section
            gr.HTML("""
                <section class="apple-cta">
                    <div class="section-container">
                        <h2 class="cta-title">Ready to ace your next interview?</h2>
                        <p class="cta-subtitle">Join thousands of job seekers who've gained the unfair advantage.</p>
                        <button class="btn-primary large" onclick="document.getElementById('cta-button').click()">Start your analysis</button>
                        <p class="cta-note">Free to use. No account required.</p>
                    </div>
                </section>
            """)
            
            # Footer
            gr.HTML("""
                <footer class="apple-footer">
                    <div class="footer-container">
                        <div class="footer-content">
                            <div class="footer-section">
                                <h4>Product</h4>
                                <ul>
                                    <li><a href="#features">Features</a></li>
                                    <li><a href="#how-it-works">How it works</a></li>
                                    <li><a href="#pricing">Pricing</a></li>
                                    <li><a href="#support">Support</a></li>
                                </ul>
                            </div>
                            <div class="footer-section">
                                <h4>Company</h4>
                                <ul>
                                    <li><a href="#about">About</a></li>
                                    <li><a href="#careers">Careers</a></li>
                                    <li><a href="#contact">Contact</a></li>
                                    <li><a href="#press">Press</a></li>
                                </ul>
                            </div>
                            <div class="footer-section">
                                <h4>Legal</h4>
                                <ul>
                                    <li><a href="#privacy">Privacy</a></li>
                                    <li><a href="#terms">Terms</a></li>
                                    <li><a href="#security">Security</a></li>
                                    <li><a href="#cookies">Cookies</a></li>
                                </ul>
                            </div>
                        </div>
                        <div class="footer-bottom">
                            <p>© 2024 IQKiller. All rights reserved.</p>
                        </div>
                    </div>
                </footer>
            """)
            
            # Hidden CTA button
            cta_button = gr.Button("Get Started", elem_id="cta-button", visible=False)
        
        # App Page
        with gr.Column(visible=False, elem_id="app-page") as app_page:
            # App Navigation
            gr.HTML("""
                <nav class="apple-nav">
                    <div class="nav-container">
                        <div class="nav-logo">
                            <span class="logo-icon">🧠</span>
                            <span class="logo-text">IQKiller</span>
                        </div>
                        <div style="flex: 1;"></div>
                        <button class="nav-back" onclick="document.getElementById('back-button').click()">← Back to home</button>
                    </div>
                </nav>
            """)
            
            back_button = gr.Button("Back", elem_id="back-button", visible=False)
            
            # App Hero
            gr.HTML("""
                <section class="app-hero">
                    <div class="section-container">
                        <h1 class="app-title">Analyze your fit</h1>
                        <p class="app-subtitle">Upload your resume and job posting to get started.</p>
                    </div>
                </section>
            """)
            
            # Input Section
            gr.HTML("""
                <section class="input-section">
                    <div class="form-container">
                        <div class="form-header">
                            <h2>Tell us about yourself and the role</h2>
                            <p>We'll analyze how well you match and create your personalized interview guide.</p>
                        </div>
                    </div>
                </section>
            """)
            
            # Form Grid
            with gr.Row(elem_classes=["apple-form-grid"]):
                # Resume Column
                with gr.Column(elem_classes=["form-column"]):
                    gr.HTML("""
                        <div class="form-section">
                            <div class="form-title">
                                <span class="form-icon">👤</span>
                                Your Resume
                            </div>
                            <p class="form-description">Share your background and experience</p>
                        </div>
                    """)
                    
                    resume_text = gr.Textbox(
                        placeholder="Paste your resume text here...",
                        lines=8,
                        elem_classes=["apple-textarea"]
                    )
                    
                    gr.HTML('<div class="form-divider">or</div>')
                    
                    resume_file = gr.File(
                        file_types=[".pdf"],
                        label="Upload PDF resume",
                        elem_classes=["apple-file-input"]
                    )
                
                # Job Column  
                with gr.Column(elem_classes=["form-column"]):
                    gr.HTML("""
                        <div class="form-section">
                            <div class="form-title">
                                <span class="form-icon">💼</span>
                                Job Posting
                            </div>
                            <p class="form-description">The role you're applying for</p>
                        </div>
                    """)
                    
                    job_url = gr.Textbox(
                        placeholder="Paste job URL (LinkedIn, Indeed, etc.)",
                        elem_classes=["apple-input"]
                    )
                    
                    gr.HTML('<div class="form-divider">or</div>')
                    
                    job_text = gr.Textbox(
                        placeholder="Paste job description text...",
                        lines=8,
                        elem_classes=["apple-textarea"]
                    )
            
            # Action Section
            gr.HTML("""
                <section class="action-section">
                    <div class="section-container">
                        <div class="button-container">
                            <h3>Choose your analysis type</h3>
                            <div class="action-buttons">
                                <button class="apple-button primary" onclick="document.getElementById('analyze-full').click()">
                                    Full Interview Guide
                                </button>
                                <button class="apple-button secondary" onclick="document.getElementById('analyze-quick').click()">
                                    Quick Brief
                                </button>
                            </div>
                        </div>
                    </div>
                </section>
            """)
            
            # Hidden action buttons
            analyze_full = gr.Button("Full Analysis", elem_id="analyze-full", visible=False)
            analyze_quick = gr.Button("Quick Analysis", elem_id="analyze-quick", visible=False)
        
        # Analysis Page
        with gr.Column(visible=False, elem_id="analysis-page") as analysis_page:
            # Analysis Navigation
            gr.HTML("""
                <nav class="apple-nav">
                    <div class="nav-container">
                        <div class="nav-logo">
                            <span class="logo-icon">🧠</span>
                            <span class="logo-text">IQKiller</span>
                        </div>
                        <div style="flex: 1;"></div>
                        <button class="nav-back" onclick="document.getElementById('back-to-app-button').click()">← Start over</button>
                    </div>
                </nav>
            """)
            
            back_to_app_button = gr.Button("Back to App", elem_id="back-to-app-button", visible=False)
            
            # Analysis header
            gr.HTML("""
                <div class="section-container">
                    <h2 style="color: #e2e8f0; margin-bottom: 1rem; text-align: center;">
                        🚀 Analyzing Your Profile
                    </h2>
                    <p style="color: rgba(255,255,255,0.6); text-align: center; font-size: 1rem;">
                        While we analyze your resume and job fit, let's prepare you for success!
                    </p>
                </div>
            """)
            
            # WORKING SALARY NEGOTIATION MCQ - MULTI-SCENARIO
            with gr.Group():
                # Current scenario display
                scenario_display = gr.HTML()
                
                # Choice selection
                negotiation_choice = gr.Radio(
                    choices=[],
                    label="Choose your negotiation strategy:",
                    value=None,
                    elem_classes=["negotiation-radio"],
                    interactive=True
                )
                
                # Control buttons
                with gr.Row():
                    submit_negotiation = gr.Button("Submit Choice", variant="primary", size="lg")
                    clear_choice = gr.Button("Clear", variant="secondary")
                
                # Next button appears only after answering
                next_scenario_btn = gr.Button("Next Scenario", variant="secondary", size="lg", visible=False)
                
                # Feedback and results
                negotiation_feedback = gr.HTML()
                final_assessment_display = gr.HTML()
                
                # Hidden state variables to track progress
                current_scenario_num = gr.State(0)
                negotiation_scores = gr.State([])
                salary_impacts = gr.State([])
                simulator_state = gr.State(None)
            
            # Results section
            results_display = gr.HTML(visible=True, elem_classes=["results-section"])
            
            # Hidden components for triggering analysis
            analysis_trigger = gr.Button("Start Analysis", visible=False)
            analysis_inputs = gr.State()
            
            # Hidden refresh buttons for each subreddit and state for Reddit posts
            reddit_posts_state = gr.State()
            refresh_jobs = gr.Button("Refresh r/jobs", elem_id="refresh-jobs", visible=False)
            refresh_careerguidance = gr.Button("Refresh r/careerguidance", elem_id="refresh-careerguidance", visible=False)
            refresh_cscareerquestions = gr.Button("Refresh r/cscareerquestions", elem_id="refresh-cscareerquestions", visible=False)
            refresh_careeradvice = gr.Button("Refresh r/careeradvice", elem_id="refresh-careeradvice", visible=False)
            refresh_itcareerquestions = gr.Button("Refresh r/ITCareerQuestions", elem_id="refresh-ITCareerQuestions", visible=False)
        
        # Event handlers
        def show_app():
            return {
                landing_page: gr.update(visible=False),
                app_page: gr.update(visible=True),
                analysis_page: gr.update(visible=False),
                current_page: "app"
            }
        
        def show_landing():
            return {
                landing_page: gr.update(visible=True),
                app_page: gr.update(visible=False),
                analysis_page: gr.update(visible=False),
                current_page: "landing"
            }
        
        def show_analysis():
            return {
                landing_page: gr.update(visible=False),
                app_page: gr.update(visible=False),
                analysis_page: gr.update(visible=True),
                current_page: "analysis"
            }
        
        def run_analysis_stream(resume_text, resume_file, job_url, job_text, analysis_type):
            """Run analysis with interactive salary negotiation and AI typing simulators"""
            import time
            import random
            
            # Handle inputs validation
            resume_input = resume_text
            if resume_file and not resume_text:
                resume_input = resume_file.name if hasattr(resume_file, 'name') else str(resume_file)
            
            job_input = job_text if job_text else job_url
            
            if not resume_input:
                yield """
                    <div class="error-message">
                        <h3>❌ Resume Required</h3>
                        <p>Please provide your resume text or upload a resume file.</p>
                    </div>
                """
                return
            
            if not job_input:
                yield """
                    <div class="error-message">
                        <h3>❌ Job Information Required</h3>
                        <p>Please provide a job URL or paste the job description.</p>
                    </div>
                """
                return
            
            try:
                # Step 1: Initialize
                yield create_simple_progress_display(0, "🚀 Initializing analysis...", "Setting up AI components")
                time.sleep(1)
                
                # Step 2: Parse Resume
                yield create_simple_progress_display(1, "📄 Parsing your resume...", "Extracting skills, experience, and achievements")
                time.sleep(2)
                
                # Skip the old static salary negotiation display since we now have working Gradio components
                # The interactive MCQ is handled by the Gradio Radio component above
                time.sleep(3)  # Brief pause to simulate processing
                
                # *** SALARY NEGOTIATION CYCLING STARTS HERE ***
                # Random salary negotiation scenarios during wait time
                simulator = SalaryNegotiationSimulator(user_role="Software Engineer", experience_level="Mid", base_salary=75000)
                cycling_manager = ScenarioCyclingManager(simulator)
                # Show engaging content during analysis wait time
                yield create_simple_progress_display(3, "🚀 Running deep analysis...", "This will take 30-60 seconds - enjoy the salary negotiation practice!")
                
                # Brief pause before starting actual analysis
                time.sleep(2)
                
                # Run actual analysis
                import asyncio
                
                orchestrator = EnhancedInterviewOrchestrator()
                
                async def run_async():
                    input_type = "pdf_path" if resume_file and not resume_text else "text"
                    return await orchestrator.create_enhanced_interview_guide(
                        resume_input=resume_input,
                        job_input=job_input,
                        input_type=input_type
                    )
                
                # Run async function
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                result = loop.run_until_complete(run_async())
                
                # Format final result
                if result.success and result.interview_guide:
                    final_result = format_interview_guide(result.interview_guide, result.match_score, result.processing_time)
                    yield final_result
                else:
                    yield f"""
                        <div class="error-message">
                            <h3>❌ Analysis Failed</h3>
                            <p>We encountered an issue processing your request. Please try again.</p>
                            <div class="analysis-content">{result.error_message if hasattr(result, 'error_message') else 'Unknown error'}</div>
                    </div>
                    """
                
            except Exception as e:
                yield f"""
                    <div class="error-message">
                        <h3>❌ Something went wrong</h3>
                        <p>An unexpected error occurred: {str(e)}</p>
                    </div>
                """
        
        def refresh_single_post(subreddit: str, current_posts):
            """Refresh a single subreddit post"""
            if current_posts:
                # Get fresh post for this subreddit
                fresh_post = reddit_client.get_single_subreddit_post(subreddit)
                if fresh_post:
                    current_posts[subreddit] = fresh_post
                    # Update the widget display
                    updated_widgets = reddit_client.format_posts_as_widget_cards(current_posts)
                    return gr.update(), updated_widgets, current_posts
                else:
                    # Reddit API failed, remove this subreddit from posts
                    if subreddit in current_posts:
                        del current_posts[subreddit]
                    updated_widgets = reddit_client.format_posts_as_widget_cards(current_posts)
                    return gr.update(), updated_widgets, current_posts
            return gr.update(), "", {}
        
        def create_simple_progress_display(step: int, status: str, substatus: str = ""):
            """Create progress display without Reddit posts (they're now separate widgets)"""
            steps = [
                "Starting",
                "Parsing Resume", 
                "Analyzing Job",
                "Gap Analysis",
                "Generating Guide"
            ]
            
            progress_percent = (step / len(steps)) * 100
            
            # Create step indicators
            step_html = ""
            for i, step_name in enumerate(steps):
                if i < step:
                    class_name = "progress-step completed"
                    icon = "✓"
                elif i == step:
                    class_name = "progress-step active"
                    icon = str(i + 1)
                else:
                    class_name = "progress-step"
                    icon = str(i + 1)
                
                step_html += f'''
                    <div class="{class_name}">
                        <div class="step-circle">{icon}</div>
                        <div class="step-label">{step_name}</div>
                    </div>
                '''
            
            return f'''
                <div class="progress-container">
                    <div class="progress-header">
                        <div class="progress-title">Analyzing Your Fit</div>
                        <div class="progress-subtitle">AI-powered analysis in progress...</div>
                    </div>
                    
                    <div class="progress-bar-container">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {progress_percent}%"></div>
                        </div>
                    </div>
                    
                    <div class="progress-steps">
                        {step_html}
                    </div>
                    
                    <div class="current-status">
                        <div class="status-text">{status}</div>
                        {f'<div class="status-subtext">{substatus}</div>' if substatus else ''}
                    </div>
                </div>
            '''
        
        def trigger_analysis(inputs):
            """Trigger analysis with stored inputs"""
            if inputs:
                for update in run_analysis_stream(*inputs):
                    yield update
        
        def format_interview_guide(guide_text: str, match_score: float, processing_time: float) -> str:
            """Format the interview guide with proper HTML styling"""
            import re
            
            # Simple markdown-to-HTML conversion
            html_text = guide_text
            
            # Convert headers
            html_text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_text, flags=re.MULTILINE)
            html_text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_text, flags=re.MULTILINE)
            html_text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_text, flags=re.MULTILINE)
            
            # Convert bold text
            html_text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_text)
            
            # Convert bullet points
            lines = html_text.split('\n')
            html_lines = []
            in_list = False
            
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('- ') or stripped.startswith('* '):
                    if not in_list:
                        html_lines.append('<ul>')
                        in_list = True
                    html_lines.append(f'<li>{stripped[2:]}</li>')
                elif stripped.startswith(('1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8. ', '9. ')):
                    if not in_list:
                        html_lines.append('<ol>')
                        in_list = True
                    html_lines.append(f'<li>{stripped[3:]}</li>')
                else:
                    if in_list:
                        html_lines.append('</ul>')
                        in_list = False
                    if stripped:
                        html_lines.append(f'<p>{stripped}</p>')
                    else:
                        html_lines.append('<br>')
            
            if in_list:
                html_lines.append('</ul>')
            
            formatted_text = '\n'.join(html_lines)
            
            # Add match score display
            score_display = f'''
                <div class="match-score">
                    <div class="score-number">{match_score:.1f}%</div>
                    <div class="score-label">Compatibility Score</div>
                </div>
            '''
            
            return f'''
                <div class="success-message">
                    <h3>✅ Analysis Complete</h3>
                    <p>Processing Time: {processing_time:.1f}s • Generated personalized interview guide</p>
                    <div class="interview-guide-output">
                        {score_display}
                        {formatted_text}
                    </div>
                </div>
            '''
        
        def run_full_analysis(resume_text, resume_file, job_url, job_text):
            """Start full analysis and navigate to analysis page"""
            return (
                gr.update(visible=False),  # landing_page
                gr.update(visible=False),  # app_page  
                gr.update(visible=True),   # analysis_page
                "analysis"                 # current_page
            )
        
        def run_quick_analysis(resume_text, resume_file, job_url, job_text):
            """Start quick analysis and navigate to analysis page"""
            return (
                gr.update(visible=False),  # landing_page
                gr.update(visible=False),  # app_page
                gr.update(visible=True),   # analysis_page
                "analysis"                 # current_page
            )
        
        # Salary Negotiation Multi-Scenario Handlers
        def initialize_negotiation():
            """Initialize the salary negotiation simulator and load first random scenario"""
            simulator = SalaryNegotiationSimulator(user_role="Software Engineer", experience_level="Mid", base_salary=75000)
            cycling_manager = ScenarioCyclingManager(simulator)
            
            # Get random first scenario
            scenario, scenario_idx = cycling_manager.get_next_random_scenario()
            if not scenario:
                return "", [], 0, [], [], simulator, cycling_manager, None
            
            # Format scenario with random counter
            scenario_html = f"""
                <div style="max-width: 800px; margin: 2rem auto; padding: 2rem; background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%); border-radius: 16px; color: white;">
                    <div style="text-align: center; margin-bottom: 1.5rem;">
                        <span style="background: rgba(255, 255, 255, 0.2); padding: 8px 16px; border-radius: 20px; font-size: 14px;">💰 Salary Negotiation Practice</span>
                    </div>
                    <h3 style="color: white; text-align: center; margin-bottom: 1.5rem;">{scenario['title']}</h3>
                    <p style="color: white; text-align: center; margin-bottom: 1rem;">{scenario['context']}</p>
                    <div style="background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; text-align: center;">
                        <h4 style="color: #1f2937; margin: 0; font-weight: 700;">{scenario['offer_text']}</h4>
                    </div>
                    <p style="color: white; text-align: center; margin-bottom: 1.5rem;">How would you respond?</p>
                </div>
            """
            
            # Format choices for radio buttons (without emoji numbers)
            choices = []
            for choice in scenario['choices']:
                choices.append(choice['text'])
            
            return scenario_html, gr.update(choices=choices, value=None), 0, [], [], simulator, cycling_manager, scenario
        
        def handle_negotiation_choice(choice, current_scenario, scores, impacts, simulator, cycling_manager, current_scenario_data):
            """Handle choice submission and show feedback"""
            if choice is None or simulator is None or current_scenario_data is None:
                return "", gr.update(visible=False), current_scenario, scores, impacts, "", current_scenario_data
            
            # Find selected choice by matching the choice text directly
            choice_idx = None
            for i, scenario_choice in enumerate(current_scenario_data['choices']):
                if scenario_choice['text'] == choice:
                    choice_idx = i
                    break
            
            if choice_idx is None:
                return "", gr.update(visible=False), current_scenario, scores, impacts, "", current_scenario_data
            
            selected_choice = current_scenario_data['choices'][choice_idx]
            
            # Update scores and impacts
            new_scores = scores + [selected_choice['points']]
            new_impacts = impacts + [selected_choice['salary_impact']]
            
            # Generate feedback with emoji number showing which choice was selected
            feedback_html = f"""
                <div style="padding: 1.5rem; background: linear-gradient(135deg, {'#10b981' if selected_choice['points'] > 0 else '#ef4444' if selected_choice['points'] < 0 else '#6b7280'} 0%, {'#059669' if selected_choice['points'] > 0 else '#dc2626' if selected_choice['points'] < 0 else '#4b5563'} 100%); border-radius: 12px; color: white; margin-top: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <h4 style="color: white; margin: 0;">Your Choice: {choice_idx + 1}️⃣</h4>
                        <span style="color: white; font-size: 18px; font-weight: 700; background: rgba(255, 255, 255, 0.2); padding: 8px 16px; border-radius: 20px;">
                            {'+' if selected_choice['points'] > 0 else ''}{selected_choice['points']} points
                        </span>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <strong>"{selected_choice['text']}"</strong>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <strong>{selected_choice['feedback']}</strong>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <strong>Outcome:</strong> {selected_choice['outcome']}
                    </div>
                    {f'<div style="background: rgba(255, 255, 255, 0.15); border-radius: 8px; padding: 12px; text-align: center;">💰 Potential value: ${selected_choice["salary_impact"]:,}</div>' if selected_choice['salary_impact'] > 0 else ''}
                </div>
            """
            
            # Show next button only after answering
            show_next = gr.update(visible=True)
            
            return feedback_html, show_next, current_scenario, new_scores, new_impacts, "", current_scenario_data
        
        def load_next_scenario(current_scenario, cycling_manager):
            """Load the next random scenario"""
            if cycling_manager is None:
                return "", [], current_scenario + 1, gr.update(visible=False), "", None
            
            # Get next random scenario
            scenario, scenario_idx = cycling_manager.get_next_random_scenario()
            if not scenario:
                return "", [], current_scenario + 1, gr.update(visible=False), "", None
            
            # Load random scenario
            scenario_html = f"""
                <div style="max-width: 800px; margin: 2rem auto; padding: 2rem; background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%); border-radius: 16px; color: white;">
                    <div style="text-align: center; margin-bottom: 1.5rem;">
                        <span style="background: rgba(255, 255, 255, 0.2); padding: 8px 16px; border-radius: 20px; font-size: 14px;">💰 Salary Negotiation Practice</span>
                    </div>
                    <h3 style="color: white; text-align: center; margin-bottom: 1.5rem;">{scenario['title']}</h3>
                    <p style="color: white; text-align: center; margin-bottom: 1rem;">{scenario['context']}</p>
                    <div style="background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; text-align: center;">
                        <h4 style="color: #1f2937; margin: 0; font-weight: 700;">{scenario['offer_text']}</h4>
                    </div>
                    <p style="color: white; text-align: center; margin-bottom: 1.5rem;">How would you respond?</p>
                </div>
            """
            
            # Format choices for radio buttons (without emoji numbers)
            choices = []
            for choice in scenario['choices']:
                choices.append(choice['text'])
            
            return scenario_html, gr.update(choices=choices, value=None), current_scenario + 1, gr.update(visible=False), "", scenario
        
        def clear_negotiation():
            """Clear current choice and feedback"""
            return None, "", False
        
        # Bind events
        cta_button.click(show_app, outputs=[landing_page, app_page, analysis_page, current_page])
        back_button.click(show_landing, outputs=[landing_page, app_page, analysis_page, current_page])
        back_to_app_button.click(show_app, outputs=[landing_page, app_page, analysis_page, current_page])
        
        # Negotiation Multi-Scenario Events
        
        # Initialize negotiation when page loads
        def init_salary_negotiation():
            return initialize_negotiation()
        
        # Add cycling manager state and current scenario state
        cycling_manager_state = gr.State(None)
        current_scenario_state = gr.State(None)
        
        # Submit choice event
        submit_negotiation.click(
            handle_negotiation_choice,
            inputs=[negotiation_choice, current_scenario_num, negotiation_scores, salary_impacts, simulator_state, cycling_manager_state, current_scenario_state],
            outputs=[negotiation_feedback, next_scenario_btn, current_scenario_num, negotiation_scores, salary_impacts, final_assessment_display, current_scenario_state]
        )
        
        # Next scenario event
        next_scenario_btn.click(
            load_next_scenario,
            inputs=[current_scenario_num, cycling_manager_state],
            outputs=[scenario_display, negotiation_choice, current_scenario_num, next_scenario_btn, negotiation_feedback, current_scenario_state]
        )
        
        # Clear choice event
        clear_choice.click(
            clear_negotiation,
            outputs=[negotiation_choice, negotiation_feedback, next_scenario_btn]
        )
        
        # Initialize the first scenario when the interface loads
        demo.load(
            init_salary_negotiation,
            outputs=[scenario_display, negotiation_choice, current_scenario_num, negotiation_scores, salary_impacts, simulator_state, cycling_manager_state, current_scenario_state]
        )
        
        # Store inputs and trigger analysis when switching to analysis page
        def start_full_analysis(resume_text, resume_file, job_url, job_text):
            navigation_result = run_full_analysis(resume_text, resume_file, job_url, job_text)
            inputs = (resume_text, resume_file, job_url, job_text, "full")
            return navigation_result + (inputs,)
        
        def start_quick_analysis(resume_text, resume_file, job_url, job_text):
            navigation_result = run_quick_analysis(resume_text, resume_file, job_url, job_text)
            inputs = (resume_text, resume_file, job_url, job_text, "quick")
            return navigation_result + (inputs,)
        
        analyze_full.click(
            start_full_analysis,
            inputs=[resume_text, resume_file, job_url, job_text],
            outputs=[landing_page, app_page, analysis_page, current_page, analysis_inputs]
        )
        
        analyze_quick.click(
            start_quick_analysis,
            inputs=[resume_text, resume_file, job_url, job_text],
            outputs=[landing_page, app_page, analysis_page, current_page, analysis_inputs]
        )
        
        # Trigger analysis when analysis page becomes visible
        analysis_inputs.change(
            trigger_analysis,
            inputs=[analysis_inputs],
            outputs=[results_display]
        )
        
        # Reddit functionality has been removed in favor of interactive salary negotiation
        # and AI typing simulators that provide better user engagement during analysis
    
    return demo

def create_health_check_server():
    """Create Flask server for health checks"""
    app = Flask(__name__)
    
    @app.route('/health')
    def health():
        return health_check()
    
    @app.route('/login')
    def login_page():
        return "Please use the Gradio login interface at /login"
    
    return app

def main():
    """Main function to launch the app with authentication"""
    print("🚀 Starting IQKiller No-BS Job Brief Generator...")
    
    # Environment setup
    auth_mode = os.getenv("AUTH_ENABLED", "true").lower() == "true"
    dev_mode = os.getenv("DEVELOPMENT_MODE", "false").lower() == "true"
    
    # Port configuration - let Gradio auto-detect if needed
    port = int(os.getenv("GRADIO_SERVER_PORT", "7862"))
    
    # Load prompts
    prompts = prompt_loader.prompts
    if not prompts:
        print("⚠️  Warning: No prompts loaded, using defaults")
    
    if dev_mode:
        # Development mode - no auth
        print("⚠️  Development mode - authentication disabled")
        demo = create_interface()
        # Let Gradio handle port conflicts automatically
        demo.launch(
            server_name="0.0.0.0", 
            server_port=None,  # Auto-detect available port
            show_error=True,
            share=False
        )
    else:
        # Production mode - with auth
        print("🔒 Launching authenticated app...")
        auth_wrapper = create_authenticated_wrapper(create_interface)
        demo = auth_wrapper()
        # Let Gradio handle port conflicts automatically
        demo.launch(
            server_name="0.0.0.0", 
            server_port=None,  # Auto-detect available port
            show_error=True,
            share=False
        )

if __name__ == "__main__":
    main() 