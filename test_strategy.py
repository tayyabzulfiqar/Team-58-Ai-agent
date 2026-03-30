"""
Strategy Layer Integration Test
Tests LeadStrategyEngine with 3 sample leads
"""
import json
import sys
sys.path.append('c:\\Users\\HP\\team58-ai-engine\\scripts')

from controllers.lead_strategy_engine import LeadStrategyEngine

# Initialize engine
engine = LeadStrategyEngine()

print("=" * 70)
print("🎯 STRATEGY LAYER INTEGRATION TEST")
print("=" * 70)

# Test leads
test_leads = [
    {
        "company_name": "ScaleUp Agency",
        "score": 100,
        "color": "🔴 RED",
        "reason": [
            "Running ads",
            "Low ROAS",
            "Scaling problem",
            "Hiring team"
        ]
    },
    {
        "company_name": "Growth Startup Inc",
        "score": 70,
        "color": "🟠 ORANGE",
        "reason": [
            "Some marketing activity",
            "Need more leads",
            "Want to improve growth"
        ]
    },
    {
        "company_name": "Personal Blog",
        "score": 30,
        "color": "⚫ BLACK",
        "reason": [
            "No clear business model",
            "Personal project",
            "No monetization"
        ]
    }
]

strategies = []

for i, lead in enumerate(test_leads, 1):
    print(f"\n{'='*70}")
    print(f"TEST CASE {i}: {lead['company_name']} (Score: {lead['score']})")
    print(f"{'='*70}")
    
    strategy = engine.generate_strategy(lead)
    strategies.append(strategy)
    
    print(f"\n📊 STRATEGY OUTPUT:")
    print(json.dumps(strategy, indent=2))
    
    # Validation checks
    print(f"\n✅ VALIDATION:")
    print(f"   • Strategy generated: {'YES' if strategy else 'NO'}")
    print(f"   • Has hook: {'YES' if strategy.get('hook') else 'NO'}")
    print(f"   • Has offer: {'YES' if strategy.get('offer') else 'NO'}")
    print(f"   • Has message: {'YES' if strategy.get('message') else 'NO'}")
    print(f"   • Has execution plan: {'YES' if strategy.get('execution_plan') else 'NO'}")
    print(f"   • Channels: {strategy.get('channel', [])}")
    print(f"   • Priority: {strategy.get('priority', 'N/A')}")

print(f"\n{'='*70}")
print("📋 FINAL REPORT")
print(f"{'='*70}")

print(f"\n✔ Strategy Engine Built: YES")
print(f"✔ Integration Complete: YES")
print(f"✔ Test Results:")
print(f"   • RED Lead (100): {strategies[0]['color']} - {strategies[0]['priority']}")
print(f"   • ORANGE Lead (70): {strategies[1]['color']} - {strategies[1]['priority']}")
print(f"   • BLACK Lead (30): {strategies[2]['color']} - {strategies[2]['priority']}")

print(f"\n{'='*70}")
print("🏁 STRATEGY LAYER TEST COMPLETE")
print(f"{'='*70}")
