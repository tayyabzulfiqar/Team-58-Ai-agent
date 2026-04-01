"""
Lead Strategy Engine - Converts scored leads into revenue-generating strategies
"""
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LeadStrategyEngine:
    """
    Converts scored leads into real revenue-generating strategies
    """
    
    def __init__(self):
        self.channel_map = {
            "RED": ["linkedin", "email", "phone"],
            "ORANGE": ["email", "linkedin"],
            "YELLOW": ["email"],
            "BLACK": []
        }
        
        self.hook_templates = {
            "low ROAS": [
                "Your ad spend is leaking money. Here's the fix.",
                "I noticed your ROAS dropped - we just helped a similar company 3x it in 30 days.",
                "You're burning budget on underperforming ads. Want to see how we fixed this for {similar_company}?"
            ],
            "high CAC": [
                "Your customer acquisition cost is killing margins. We cut CAC by 40% for agencies like yours.",
                "Paying too much per lead? Here's a proven system to slash acquisition costs.",
                "Your CAC is 2x industry average. Here's exactly how to fix it."
            ],
            "scaling": [
                "Scaling is hard when your funnel leaks. We fix that.",
                "Ready to scale but conversion is the bottleneck?",
                "You're hiring but leads aren't flowing. Let's solve both."
            ],
            "ads not working": [
                "Your ads stopped performing. Here's why (and the fix).",
                "Facebook/Google changes broke your funnel. We adapt fast.",
                "Ad costs up 50% but conversions flat? Reverse this today."
            ],
            "hiring": [
                "Hiring marketers while leads dry up? Let's fix the flow first.",
                "Building a team is smart. But you need leads to feed them.",
                "New hires + better systems = 10x growth. Let's talk."
            ],
            "default": [
                "I saw you're in {industry} — we just helped a similar company hit $50k MRR.",
                "Your company caught my eye. Quick question about your growth...",
                "Noticed you're {activity}. Have you considered {opportunity}?"
            ]
        }
        
        self.offer_templates = {
            "RED": {
                "name": "Emergency Revenue Recovery",
                "description": "14-day intensive audit + immediate fixes",
                "price": "$2,500 setup + $3,000/month",
                "guarantee": "20% ROAS improvement or money back"
            },
            "ORANGE": {
                "name": "Growth Acceleration System",
                "description": "Full funnel rebuild + ongoing optimization",
                "price": "$1,500 setup + $2,500/month",
                "guarantee": "2x leads in 60 days"
            },
            "YELLOW": {
                "name": "Lead Generation Starter",
                "description": "Basic funnel + monthly optimization",
                "price": "$1,000/month",
                "guarantee": "50% more qualified leads"
            }
        }
        
        self.cta_templates = {
            "RED": [
                "Reply YES and I'll send over the audit details today.",
                "Can we jump on a 15-min call this week? Pick a time: {calendar_link}",
                "Worth a 10-minute conversation? I'm free Tuesday or Wednesday."
            ],
            "ORANGE": [
                "Interested in seeing how this works for {company_type}? I can send a case study.",
                "Want to explore this? No pitch, just value. Reply and I'll share the framework.",
                "Does this resonate? Happy to share our process - just reply."
            ],
            "YELLOW": [
                "I'll add you to my weekly growth tips. Unsubscribe anytime.",
                "Want the full breakdown? It's in my newsletter (link in bio).",
                "Follow for more. I'll DM you the case study."
            ]
        }
    
    def generate_strategy(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate complete strategy for a scored lead
        """
        try:
            color = self._extract_color(lead.get("color", ""))
            score = lead.get("score", 0)
            company = lead.get("company_name", "Unknown")
            reasons = lead.get("reason", [])
            
            # Extract pain dynamically
            pain = self._extract_pain(reasons)
            
            # Determine priority level
            priority = self._get_priority(color)
            
            # Skip BLACK leads
            if color == "BLACK" or score < 40:
                return self._generate_ignore_strategy(company, score)
            
            # Build strategy components
            channel = self._select_channels(color)
            hook = self._generate_hook(pain, reasons, company)
            offer = self._generate_offer(color)
            cta = self._generate_cta(color, company)
            message = self._build_message(company, pain, hook, offer, cta)
            execution_plan = self._build_execution(color, channel, company)
            angle = self._determine_angle(pain)
            
            return {
                "company": company,
                "score": score,
                "color": color,
                "priority": priority,
                "channel": channel,
                "angle": angle,
                "hook": hook,
                "offer": offer,
                "cta": cta,
                "message": message,
                "execution_plan": execution_plan,
                "pain_identified": pain,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Strategy generation failed: {str(e)}")
            return {
                "company": lead.get("company_name", "Unknown"),
                "error": str(e),
                "priority": "ERROR",
                "channel": [],
                "message": "Strategy generation failed"
            }
    
    def _extract_color(self, color_str: str) -> str:
        """Extract color code from color string"""
        color_map = {
            "🔴 RED": "RED",
            "🟠 ORANGE": "ORANGE",
            "🟡 YELLOW": "YELLOW",
            "⚫ BLACK": "BLACK",
            "RED": "RED",
            "ORANGE": "ORANGE",
            "YELLOW": "YELLOW",
            "BLACK": "BLACK"
        }
        return color_map.get(color_str, "BLACK")
    
    def _extract_pain(self, reasons: List[str]) -> str:
        """Extract primary pain point from reasons"""
        pain_keywords = {
            "low ROAS": "low ROAS",
            "high CAC": "high CAC",
            "losing money": "losing money on ads",
            "ads not working": "ads not working",
            "scaling": "scaling problems",
            "hiring": "hiring challenges",
            "conversion": "low conversion",
            "leads": "need more leads"
        }
        
        reasons_text = " ".join(reasons).lower()
        
        for keyword, pain_label in pain_keywords.items():
            if keyword in reasons_text:
                return pain_label
        
        return "growth challenges"
    
    def _get_priority(self, color: str) -> str:
        """Get priority level from color"""
        priority_map = {
            "RED": "IMMEDIATE",
            "ORANGE": "HIGH",
            "YELLOW": "MEDIUM",
            "BLACK": "IGNORE"
        }
        return priority_map.get(color, "LOW")
    
    def _select_channels(self, color: str) -> List[str]:
        """Select outreach channels based on lead color"""
        return self.channel_map.get(color, ["email"])
    
    def _generate_hook(self, pain: str, reasons: List[str], company: str) -> str:
        """Generate personalized hook based on pain"""
        # Match pain to hook templates
        for pain_key, hooks in self.hook_templates.items():
            if pain_key in pain.lower() or pain_key in " ".join(reasons).lower():
                return random.choice(hooks)
        
        # Default hook
        return f"I noticed {company} is scaling. Quick question about your lead flow..."
    
    def _generate_offer(self, color: str) -> Dict[str, str]:
        """Generate offer based on lead color"""
        if color == "RED":
            return self.offer_templates["RED"]
        elif color == "ORANGE":
            return self.offer_templates["ORANGE"]
        elif color == "YELLOW":
            return self.offer_templates["YELLOW"]
        else:
            return {"name": "None", "description": "No offer for low-priority leads", "price": "N/A"}
    
    def _generate_cta(self, color: str, company: str) -> str:
        """Generate CTA based on lead color"""
        templates = self.cta_templates.get(color, self.cta_templates["YELLOW"])
        cta = random.choice(templates)
        
        # Personalize
        cta = cta.replace("{company_type}", company.split()[0] if company else "similar companies")
        
        return cta
    
    def _build_message(self, company: str, pain: str, hook: str, 
                      offer: Dict, cta: str) -> str:
        """Build complete outreach message"""
        
        # RED leads get aggressive, direct messages
        if offer["name"] == "Emergency Revenue Recovery":
            return f"""Hey {company.split()[0] if company else "there"},

{hook}

I work with agencies dealing with {pain}. In the last 30 days, we:
• Cut CAC by 40% for a SaaS company
• 3x'd ROAS for a marketing agency  
• Generated 200+ qualified leads for a B2B firm

Our {offer['name']} is designed for exactly this:
{offer['description']}
Investment: {offer['price']}
Guarantee: {offer['guarantee']}

{cta}

Best,
[Your Name]"""
        
        # ORANGE leads get value-first, consultative messages
        elif offer["name"] == "Growth Acceleration System":
            return f"""Hi {company.split()[0] if company else "there"},

{hook}

I help {company.split()[0] if company else "companies"} like yours solve {pain} without the usual agency headaches.

Recently helped a similar company:
→ From 50 leads/month to 300+ in 60 days
→ Reduced cost per acquisition by 35%
→ Built automated follow-up that converts 24% better

Our approach: {offer['description']}

{cta}

Talk soon,
[Your Name]

P.S. Here's a case study from a {company.split()[0] if company else "similar"} client: [link]"""
        
        # YELLOW leads get soft nurture messages
        else:
            return f"""Hey {company.split()[0] if company else "there"},

Came across {company} and noticed you're working on growth. 

Quick thought: Most companies struggle with {pain} because they focus on traffic instead of conversion.

I wrote a short guide on fixing this - want me to send it over?

{cta}

[Your Name]"""
    
    def _build_execution(self, color: str, channels: List[str], company: str) -> List[str]:
        """Build execution plan based on lead color"""
        
        if color == "RED":
            return [
                f"1. Send LinkedIn connection request with hook within 2 hours",
                f"2. Follow up with InMail/email same day if no response",
                f"3. Call directly if contact number available (Day 2)",
                f"4. Send case study specific to {company.split()[0] if company else 'their'} industry (Day 3)",
                f"5. Final follow-up with calendar link (Day 5)",
                "6. Move to CRM if no response after 5 days",
                "7. Escalate to sales team for direct outreach"
            ]
        
        elif color == "ORANGE":
            return [
                f"1. Send personalized email with value-first message (Day 1)",
                f"2. LinkedIn connection request with note (Day 2)",
                f"3. Share relevant case study or content (Day 4)",
                f"4. Soft follow-up asking if they saw the value piece (Day 7)",
                f"5. Send framework/guide related to their pain (Day 10)",
                "6. Nurture with monthly value content",
                "7. Re-score in 30 days"
            ]
        
        elif color == "YELLOW":
            return [
                f"1. Add to email nurture sequence (Day 1)",
                f"2. Connect on LinkedIn with soft message (Day 3)",
                f"3. Send weekly newsletter with valuable content",
                f"4. Engage with their content on social (ongoing)",
                "5. Re-evaluate in 60 days for score upgrade"
            ]
        
        else:
            return ["No action required - lead disqualified"]
    
    def _determine_angle(self, pain: str) -> str:
        """Determine messaging angle based on pain"""
        angles = {
            "low ROAS": "Revenue Recovery",
            "high CAC": "Cost Reduction",
            "losing money": "Profit Protection",
            "ads not working": "Performance Fix",
            "scaling": "Growth Enablement",
            "hiring": "Team Support",
            "conversion": "Conversion Optimization",
            "leads": "Lead Volume"
        }
        
        for key, angle in angles.items():
            if key in pain.lower():
                return angle
        
        return "Growth Acceleration"
    
    def _generate_ignore_strategy(self, company: str, score: int) -> Dict[str, Any]:
        """Generate strategy for ignored leads"""
        return {
            "company": company,
            "score": score,
            "color": "BLACK",
            "priority": "IGNORE",
            "channel": [],
            "angle": "None",
            "hook": "N/A",
            "offer": {"name": "None", "description": "Lead does not meet criteria"},
            "cta": "None",
            "message": "No outreach - lead disqualified",
            "execution_plan": ["Do not contact", "Archive for future re-evaluation"],
            "pain_identified": "N/A",
            "reason": f"Score {score} below threshold"
        }
    
    def generate_batch_strategies(self, leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate strategies for multiple leads"""
        strategies = []
        
        for lead in leads:
            strategy = self.generate_strategy(lead)
            strategies.append(strategy)
        
        return strategies


# Example usage
if __name__ == "__main__":
    engine = LeadStrategyEngine()
    
    # Test RED lead
    red_lead = {
        "company_name": "ScaleUp Agency",
        "score": 100,
        "color": "🔴 RED",
        "reason": [
            "Running ads",
            "Low ROAS",
            "Scaling problem",
            "Hiring team"
        ]
    }
    
    strategy = engine.generate_strategy(red_lead)
    print("=" * 60)
    print("RED LEAD STRATEGY")
    print("=" * 60)
    print(json.dumps(strategy, indent=2))
