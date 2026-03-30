"""
Market Analyzer - Analyzes market trends, pain points, and demand signals
"""
import json
from typing import Dict, Any, List
from collections import Counter
from datetime import datetime


class MarketAnalyzer:
    """
    Analyzes market trends, pain points, and demand clusters from processed data
    """
    
    def __init__(self):
        self.pain_keywords = [
            "low conversion", "high cost", "expensive leads", "burning budget",
            "ROAS", "CAC", "not working", "leaking money", "struggling",
            "need more leads", "scaling issues", "growth problem",
            "can't scale", "funnel broken", "ads failing"
        ]
        
        self.urgency_keywords = [
            "urgent", "asap", "critical", "losing money", "emergency",
            "immediate", "right now", "desperate", "burning cash",
            "need help today", "this week", "can't wait"
        ]
        
        self.demand_indicators = [
            "hiring", "expanding", "new funding", "series a", "series b",
            "scaling fast", "growth mode", "aggressive growth",
            "doubling team", "new market", "launching"
        ]
    
    def analyze(self, processed_leads: List[Dict], content_text: str = "") -> Dict[str, Any]:
        """
        Analyze market trends from leads and content
        """
        # Extract all pain points
        all_pains = []
        all_signals = []
        all_industries = []
        
        for lead in processed_leads:
            pains = lead.get("pain_points", [])
            signals = lead.get("intent_signals", [])
            industry = lead.get("industry", "")
            
            all_pains.extend(pains)
            all_signals.extend(signals)
            if industry:
                all_industries.append(industry)
        
        # Analyze trending problems
        trending_problems = self._identify_trending_problems(all_pains, all_signals)
        
        # Analyze demand signals
        demand_signals = self._analyze_demand_signals(all_signals, all_industries)
        
        # Calculate urgency level
        urgency_level = self._calculate_urgency(all_pains, all_signals)
        
        # Identify hot markets
        hot_markets = self._identify_hot_markets(all_industries, processed_leads)
        
        # Market sentiment
        market_sentiment = self._assess_market_sentiment(trending_problems, demand_signals)
        
        return {
            "top_problems": trending_problems[:5],
            "demand_signals": demand_signals[:5],
            "urgency_level": urgency_level,
            "hot_markets": hot_markets[:3],
            "market_sentiment": market_sentiment,
            "total_leads_analyzed": len(processed_leads),
            "pain_point_count": len(all_pains),
            "analyzed_at": datetime.now().isoformat()
        }
    
    def _identify_trending_problems(self, pains: List[str], signals: List[str]) -> List[Dict]:
        """Identify most repeated pain points"""
        all_text = " ".join(pains + signals).lower()
        
        problem_counts = []
        for problem in self.pain_keywords:
            count = all_text.count(problem.lower())
            if count > 0:
                problem_counts.append({
                    "problem": problem,
                    "mentions": count,
                    "severity": "HIGH" if count >= 3 else "MEDIUM" if count >= 2 else "LOW"
                })
        
        # Sort by mentions
        problem_counts.sort(key=lambda x: x["mentions"], reverse=True)
        return problem_counts
    
    def _analyze_demand_signals(self, signals: List[str], industries: List[str]) -> List[Dict]:
        """Analyze demand signals in the market"""
        all_text = " ".join(signals).lower()
        
        demand_counts = []
        for indicator in self.demand_indicators:
            count = all_text.count(indicator.lower())
            if count > 0:
                demand_counts.append({
                    "signal": indicator,
                    "mentions": count,
                    "strength": "STRONG" if count >= 3 else "MODERATE" if count >= 2 else "WEAK"
                })
        
        # Sort by mentions
        demand_counts.sort(key=lambda x: x["mentions"], reverse=True)
        
        # Add industry-based demand
        industry_counter = Counter(industries)
        for industry, count in industry_counter.most_common(3):
            demand_counts.append({
                "signal": f"{industry} growth",
                "mentions": count,
                "strength": "STRONG" if count >= 3 else "MODERATE",
                "type": "industry_trend"
            })
        
        return demand_counts
    
    def _calculate_urgency(self, pains: List[str], signals: List[str]) -> str:
        """Calculate overall market urgency level"""
        all_text = " ".join(pains + signals).lower()
        
        urgency_count = 0
        for keyword in self.urgency_keywords:
            urgency_count += all_text.count(keyword.lower())
        
        total_signals = len(pains) + len(signals)
        if total_signals == 0:
            return "LOW"
        
        urgency_ratio = urgency_count / total_signals
        
        if urgency_ratio >= 0.3:
            return "HIGH"
        elif urgency_ratio >= 0.15:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _identify_hot_markets(self, industries: List[str], leads: List[Dict]) -> List[Dict]:
        """Identify hot markets with high activity"""
        industry_counter = Counter(industries)
        
        hot_markets = []
        for industry, count in industry_counter.most_common(5):
            # Calculate average score for this industry
            industry_leads = [l for l in leads if l.get("industry") == industry]
            avg_score = sum(l.get("score", 0) for l in industry_leads) / len(industry_leads) if industry_leads else 0
            
            hot_markets.append({
                "market": industry,
                "lead_count": count,
                "avg_score": round(avg_score, 1),
                "heat_level": "HOT" if count >= 3 and avg_score >= 70 else "WARM" if count >= 2 else "COOL"
            })
        
        return hot_markets
    
    def _assess_market_sentiment(self, problems: List[Dict], demand: List[Dict]) -> str:
        """Assess overall market sentiment"""
        problem_severity = sum(1 for p in problems if p["severity"] == "HIGH")
        demand_strength = sum(1 for d in demand if d["strength"] == "STRONG")
        
        if problem_severity >= 3 and demand_strength >= 3:
            return "URGENT_DEMAND - High pain + High demand = OPPORTUNITY"
        elif problem_severity >= 2:
            return "PROBLEM_AWARE - Market recognizes pain points"
        elif demand_strength >= 2:
            return "GROWTH_MODE - Active expansion detected"
        else:
            return "EXPLORATORY - Early stage market"


# Example usage
if __name__ == "__main__":
    analyzer = MarketAnalyzer()
    
    test_leads = [
        {"industry": "SaaS", "pain_points": ["low conversion", "high CAC"], "intent_signals": ["hiring", "scaling"], "score": 85},
        {"industry": "Agency", "pain_points": ["ROAS dropped"], "intent_signals": ["urgent help"], "score": 90}
    ]
    
    result = analyzer.analyze(test_leads)
    print(json.dumps(result, indent=2))
