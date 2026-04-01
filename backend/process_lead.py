"""
Process the provided lead through the Advanced Qualification Engine
"""
import json
import sys
sys.path.append('c:\\Users\\HP\\team58-ai-engine\\scripts')

from agents.lead_qualification_agent import LeadQualificationAgent

# Initialize agent
agent = LeadQualificationAgent()

print("=" * 60)
print("ADVANCED LEAD QUALIFICATION ENGINE")
print("=" * 60)

# Test Case 1: HOT LEAD (should score 90+ for RED)
print("\n🔥 TEST 1: HOT LEAD (Target: 90+ for RED)")
print("-" * 40)

hot_lead = {
    "company_name": "ScaleUp Agency",
    "industry": "Marketing Services",
    "services": [
        "lead generation",
        "paid ads",
        "ppc management",
        "facebook ads"
    ],
    "target_audience": "B2B SaaS companies and agencies",
    "pain_points": [
        "losing money on ads",
        "low ROAS",
        "high CAC",
        "ads not working"
    ],
    "intent_signals": [
        "actively optimizing campaigns",
        "hiring marketers",
        "looking for growth partner",
        "series a funding"
    ],
    "website_quality": "average",
    "has_blog": True,
    "running_ads": True,
    "social_links": {"linkedin": "https://linkedin.com/company/scaleup"},
    "decision_maker": True,
    "contact_title": "CEO",
    "revenue_range": "$1M+",
    "team_size": 25,
    "hiring": True
}

result1 = agent.qualify_lead(hot_lead)
print(json.dumps(result1, indent=2))

# Test Case 2: WARM LEAD (should score 50-69)
print("\n🟡 TEST 2: WARM LEAD")
print("-" * 40)

warm_lead = {
    "company_name": "Growth Startup Inc",
    "industry": "SaaS",
    "services": ["software development", "b2b platform"],
    "target_audience": "small businesses and startups",
    "pain_points": [
        "need more clients",
        "want to improve growth"
    ],
    "intent_signals": [
        "looking for marketing help"
    ],
    "website_quality": "average",
    "has_blog": False,
    "running_ads": False,
    "social_links": {"twitter": "https://twitter.com/growthstartup"}
}

result2 = agent.qualify_lead(warm_lead)
print(json.dumps(result2, indent=2))

# Test Case 3: COLD/REJECT LEAD (should trigger negative filters)
print("\n⚫ TEST 3: COLD LEAD (Personal Blog - Should trigger filters)")
print("-" * 40)

cold_lead = {
    "company_name": "Personal Blog",
    "industry": "",
    "services": [],
    "target_audience": "",
    "pain_points": ["want more readers"],
    "intent_signals": [],
    "website_quality": "poor",
    "has_blog": True,
    "running_ads": False
}

result3 = agent.qualify_lead(cold_lead)
print(json.dumps(result3, indent=2))

print("\n" + "=" * 60)
print("QUALIFICATION COMPLETE")
print("=" * 60)

