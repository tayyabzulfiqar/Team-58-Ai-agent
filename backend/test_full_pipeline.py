"""
End-to-End Integration Test
Full pipeline: Data → Processing → Scoring → Strategy → Intelligence
"""
import json
import sys
sys.path.append('c:\\Users\\HP\\team58-ai-engine\\scripts')

from scripts.agents.lead_qualification_agent import LeadQualificationAgent
from scripts.controllers.lead_strategy_engine import LeadStrategyEngine
from scripts.intelligence.feedback_analyzer import FeedbackAnalyzer
from scripts.intelligence.pattern_learner import PatternLearner
from scripts.intelligence.learning_optimizer import LearningOptimizer

print("=" * 70)
print("🔥 END-TO-END INTEGRATION TEST")
print("=" * 70)

# Initialize all engines
scoring_engine = LeadQualificationAgent()
strategy_engine = LeadStrategyEngine()
feedback_analyzer = FeedbackAnalyzer()
pattern_learner = PatternLearner()
learning_optimizer = LearningOptimizer()

# Test with 10 realistic leads
raw_leads = [
    {"company_name": "TechScale Solutions", "industry": "B2B SaaS", "services": ["lead generation", "crm software"], "target_audience": "enterprise companies", "pain_points": ["low conversion", "high cost per lead"], "intent_signals": ["actively optimizing", "hiring sales team"], "website_quality": "average", "has_blog": True, "running_ads": True, "revenue_range": "$5M+", "team_size": 30, "hiring": True, "decision_maker": True, "contact_title": "CEO"},
    {"company_name": "GrowthRocket Agency", "industry": "Marketing", "services": ["ppc management", "facebook ads"], "target_audience": "ecommerce brands", "pain_points": ["ROAS dropped", "ads not converting"], "intent_signals": ["urgent help needed", "losing money"], "website_quality": "poor", "has_blog": False, "running_ads": True, "revenue_range": "$1M+", "team_size": 12, "hiring": True, "decision_maker": True, "contact_title": "Founder"},
    {"company_name": "DataDriven Marketing", "industry": "Digital Marketing", "services": ["analytics", "conversion optimization"], "target_audience": "SaaS startups", "pain_points": ["need more qualified leads"], "intent_signals": ["exploring partnerships"], "website_quality": "strong", "has_blog": True, "running_ads": False, "revenue_range": "$500K", "team_size": 8, "hiring": False, "decision_maker": True, "contact_title": "CMO"},
    {"company_name": "StartupXYZ", "industry": "Tech", "services": ["app development"], "target_audience": "small businesses", "pain_points": ["want to grow faster"], "intent_signals": ["testing marketing channels"], "website_quality": "average", "has_blog": False, "running_ads": False, "revenue_range": "", "team_size": 3, "hiring": False, "decision_maker": False, "contact_title": ""},
    {"company_name": "Personal Blog John", "industry": "", "services": [], "target_audience": "", "pain_points": ["want more readers"], "intent_signals": [], "website_quality": "poor", "has_blog": True, "running_ads": False, "revenue_range": "", "team_size": 1, "hiring": False, "decision_maker": False, "contact_title": ""},
    {"company_name": "Enterprise Co", "industry": "Enterprise Software", "services": ["enterprise solutions", "consulting"], "target_audience": "fortune 500", "pain_points": ["scaling issues", "inefficient lead process"], "intent_signals": ["series b funding", "expansion"], "website_quality": "strong", "has_blog": True, "running_ads": True, "revenue_range": "$10M+", "team_size": 150, "hiring": True, "decision_maker": True, "contact_title": "VP Sales"},
    {"company_name": "LocalBiz Pro", "industry": "Local Services", "services": ["local marketing"], "target_audience": "local customers", "pain_points": ["low visibility"], "intent_signals": ["budget conscious"], "website_quality": "average", "has_blog": False, "running_ads": False, "revenue_range": "$100K", "team_size": 5, "hiring": False, "decision_maker": True, "contact_title": "Owner"},
    {"company_name": "CryptoScam Inc", "industry": "Crypto", "services": ["make money fast"], "target_audience": "retail investors", "pain_points": ["need traffic"], "intent_signals": ["get rich quick"], "website_quality": "poor", "has_blog": False, "running_ads": True, "revenue_range": "unknown", "team_size": 2, "hiring": False, "decision_maker": True, "contact_title": "CEO"},
]

print(f"\n📥 PROCESSING {len(raw_leads)} LEADS...\n")

# Phase 1: Scoring
print("⚡ PHASE 1: LEAD SCORING")
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
        print(f"   • {strategy['company']}: {strategy['angle']} via {', '.join(strategy['channel'])}")

# Phase 3: Feedback Analysis
print("\n📊 PHASE 3: FEEDBACK ANALYSIS")
feedback = feedback_analyzer.analyze(scored_leads, strategies)
print(f"   • Total analyzed: {feedback['total_analyzed']}")
print(f"   • Predicted wins: {feedback['predicted_wins']}")
print(f"   • Win rate: {feedback['win_rate']:.1%}")
print(f"   • Avg quality: {feedback['avg_strategy_quality']:.1f}/10")

# Phase 4: Pattern Learning
print("\n🔍 PHASE 4: PATTERN LEARNING")
patterns = pattern_learner.analyze(feedback)
print(f"   • Winners: {patterns['total_winners']}")
print(f"   • Losers: {patterns['total_losers']}")
if patterns['top_patterns']:
    print(f"   • Strong patterns: {len(patterns['top_patterns'])}")
    for p in patterns['top_patterns'][:3]:
        print(f"     - {p['pattern']}: {p['ratio']:.1f}x ratio")
if patterns['weak_patterns']:
    print(f"   • Weak patterns: {len(patterns['weak_patterns'])}")

# Phase 5: Learning Optimization
print("\n⚙️  PHASE 5: LEARNING OPTIMIZATION")
optimization = learning_optimizer.update(patterns)
print(f"   • Updates made: {len(optimization['updates_made'])}")
for update in optimization['updates_made']:
    direction = "↑" if update['adjustment'] > 0 else "↓"
    print(f"     - {update['weight_name']}: {update['previous_value']} → {update['new_value']} {direction}")

# Final Summary
print(f"\n{'='*70}")
print("✅ INTEGRATION TEST COMPLETE")
print(f"{'='*70}")

# Count by color
red_count = sum(1 for s in scored_leads if 'RED' in s['color'])
orange_count = sum(1 for s in scored_leads if 'ORANGE' in s['color'])
yellow_count = sum(1 for s in scored_leads if 'YELLOW' in s['color'])
black_count = sum(1 for s in scored_leads if 'BLACK' in s['color'])

print(f"\n📊 FINAL PIPELINE RESULTS:")
print(f"   • Total leads processed: {len(raw_leads)}")
print(f"   • 🔴 RED (Attack): {red_count}")
print(f"   • 🟠 ORANGE (Priority): {orange_count}")
print(f"   • 🟡 YELLOW (Nurture): {yellow_count}")
print(f"   • ⚫ BLACK (Ignore): {black_count}")
print(f"   • Predicted win rate: {feedback['win_rate']:.1%}")
print(f"   • Patterns learned: {len(patterns['top_patterns'])}")
print(f"   • System optimizations: {len(optimization['updates_made'])}")

print(f"\n🧠 SYSTEM STATUS: OPERATIONAL")
print(f"{'='*70}")
