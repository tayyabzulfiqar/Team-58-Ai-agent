"""
Campaign Intelligence Brain - Full Integration Test
Tests all 4 new intelligence engines end-to-end
"""
import json
import sys
sys.path.append('c:\\Users\\HP\\team58-ai-engine\\scripts')

from intelligence.market_analyzer import MarketAnalyzer
from intelligence.competitor_analyzer import CompetitorAnalyzer
from intelligence.positioning_engine import PositioningEngine
from intelligence.prediction_engine import PredictionEngine
from agents.lead_qualification_agent import LeadQualificationAgent
from controllers.lead_strategy_engine import LeadStrategyEngine

print("=" * 70)
print("🧠 CAMPAIGN INTELLIGENCE BRAIN")
print("=" * 70)

# Initialize all engines
market_analyzer = MarketAnalyzer()
competitor_analyzer = CompetitorAnalyzer()
positioning_engine = PositioningEngine()
prediction_engine = PredictionEngine()
scoring_engine = LeadQualificationAgent()
strategy_engine = LeadStrategyEngine()

# Test leads
raw_leads = [
    {"company_name": "TechScale Solutions", "industry": "B2B SaaS", "services": ["lead generation", "crm software"], "target_audience": "enterprise companies", "pain_points": ["low conversion", "high cost per lead"], "intent_signals": ["actively optimizing", "hiring sales team"], "website_quality": "average", "has_blog": True, "running_ads": True, "revenue_range": "$5M+", "team_size": 30, "hiring": True},
    {"company_name": "GrowthRocket Agency", "industry": "Marketing", "services": ["ppc management", "facebook ads"], "target_audience": "ecommerce brands", "pain_points": ["ROAS dropped", "ads not converting"], "intent_signals": ["urgent help needed", "losing money"], "website_quality": "poor", "has_blog": False, "running_ads": True, "revenue_range": "$1M+", "team_size": 12, "hiring": True},
    {"company_name": "DataDriven Marketing", "industry": "Digital Marketing", "services": ["analytics", "conversion optimization"], "target_audience": "SaaS startups", "pain_points": ["need more qualified leads"], "intent_signals": ["exploring partnerships"], "website_quality": "strong", "has_blog": True, "running_ads": False, "revenue_range": "$500K", "team_size": 8, "hiring": False},
    {"company_name": "StartupXYZ", "industry": "Tech", "services": ["app development"], "target_audience": "small businesses", "pain_points": ["want to grow faster"], "intent_signals": ["testing marketing channels"], "website_quality": "average", "has_blog": False, "running_ads": False, "revenue_range": "", "team_size": 3, "hiring": False},
    {"company_name": "Enterprise Co", "industry": "Enterprise Software", "services": ["enterprise solutions", "consulting"], "target_audience": "fortune 500", "pain_points": ["scaling issues", "inefficient lead process"], "intent_signals": ["series b funding", "expansion"], "website_quality": "strong", "has_blog": True, "running_ads": True, "revenue_range": "$10M+", "team_size": 150, "hiring": True},
]

# Phase 1: Lead Scoring
print("\n📊 PHASE 1: LEAD SCORING")
scored_leads = []
for lead in raw_leads:
    result = scoring_engine.qualify_lead(lead)
    scored_leads.append(result)
    print(f"   • {result['company_name']}: {result['score']}/100 [{result['color']}]")

# Phase 2: Strategy Generation
print("\n🎯 PHASE 2: STRATEGY GENERATION")
strategies = []
for lead in scored_leads:
    strategy = strategy_engine.generate_strategy(lead)
    strategies.append(strategy)
    if strategy['color'] != 'BLACK':
        print(f"   • {strategy['company']}: {strategy['angle']}")

# Phase 3: Market Intelligence
print("\n📈 PHASE 3: MARKET ANALYZER")
market_insights = market_analyzer.analyze(raw_leads)
print(f"   • Urgency Level: {market_insights['urgency_level']}")
print(f"   • Market Sentiment: {market_insights['market_sentiment']}")
print(f"   • Top Problems: {len(market_insights['top_problems'])}")
for problem in market_insights['top_problems'][:2]:
    print(f"     - {problem['problem']} ({problem['severity']})")
print(f"   • Hot Markets: {len(market_insights['hot_markets'])}")
for market in market_insights['hot_markets'][:2]:
    print(f"     - {market['market']}: {market['heat_level']}")

# Phase 4: Competitor Analysis
print("\n🔍 PHASE 4: COMPETITOR ANALYZER")
competitor_insights = competitor_analyzer.analyze(market_insights, raw_leads)
print(f"   • Competition Level: {competitor_insights['competition_level']}")
print(f"   • Competitor Activity: {competitor_insights['competitor_activity']['competitor_presence']}")
print(f"   • Opportunity Score: {competitor_insights['opportunity_score']}/100")
if competitor_insights['market_gap']:
    print(f"   • Market Gaps Found: {len(competitor_insights['market_gap'])}")
    for gap in competitor_insights['market_gap'][:1]:
        print(f"     - {gap['type']}")

# Phase 5: Positioning Engine (for top 3 leads)
print("\n🎯 PHASE 5: POSITIONING ENGINE")
positioning_results = []
for i, (lead, strategy) in enumerate(zip(scored_leads[:3], strategies[:3])):
    if strategy['color'] != 'BLACK':
        positioning = positioning_engine.generate(strategy, market_insights, competitor_insights)
        positioning_results.append(positioning)
        print(f"\n   Lead {i+1}: {strategy['company']}")
        print(f"   • Angle: {positioning['angle']}")
        print(f"   • Tagline: {positioning['tagline']}")
        print(f"   • Why Us: {positioning['why_us'][:60]}...")

# Phase 6: Prediction Engine
print("\n📊 PHASE 6: PREDICTION ENGINE")
# Mock patterns for prediction
patterns = {
    "top_patterns": [{"pattern": "low ROAS", "ratio": 3.0}],
    "weak_patterns": []
}

for i, (lead, strategy, positioning) in enumerate(zip(scored_leads[:3], strategies[:3], positioning_results)):
    if strategy['color'] != 'BLACK':
        prediction = prediction_engine.predict(lead, patterns, market_insights, competitor_insights, positioning)
        print(f"\n   Lead {i+1}: {strategy['company']}")
        print(f"   • Success Probability: {prediction['success_probability']}%")
        print(f"   • Campaign Strength: {prediction['campaign_strength']}")
        print(f"   • Score Contribution: {prediction['score_contribution']}")
        print(f"   • Market Contribution: {prediction['market_contribution']}")
        print(f"   • Predicted Outcome: {prediction['predicted_outcome'][:50]}...")

# Final Summary
print(f"\n{'='*70}")
print("✅ CAMPAIGN INTELLIGENCE BRAIN OPERATIONAL")
print(f"{'='*70}")

print(f"\n📊 SYSTEM CAPABILITIES:")
print(f"   • Market Analysis: ACTIVE")
print(f"   • Competitor Intelligence: ACTIVE")
print(f"   • Positioning Engine: ACTIVE")
print(f"   • Prediction Engine: ACTIVE")

print(f"\n📈 TEST RESULTS:")
print(f"   • Leads analyzed: {len(raw_leads)}")
print(f"   • Market insights: {len(market_insights['top_problems'])} problems, {len(market_insights['hot_markets'])} hot markets")
print(f"   • Competition level: {competitor_insights['competition_level']}")
print(f"   • Positioning angles: {len(positioning_results)} generated")
print(f"   • Success predictions: 3 completed")

print(f"\n🧠 MILITARY-GRADE CAMPAIGN INTELLIGENCE: OPERATIONAL")
print(f"{'='*70}")
