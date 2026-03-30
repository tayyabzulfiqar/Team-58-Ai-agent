"""
Competitor Analyzer - Analyzes competition levels and market saturation
"""
import random
from typing import Dict, Any, List
from datetime import datetime


class CompetitorAnalyzer:
    """
    Analyzes competitor activity, market saturation, and identifies gaps
    """
    
    def __init__(self):
        self.competition_indicators = [
            "competitor", "competition", "saturated", "crowded",
            "many players", "price war", "commoditized", "red ocean"
        ]
        
        self.gap_indicators = [
            "underserved", "niche", "emerging", "blue ocean",
            "unmet need", "gap in market", "opportunity", "first mover"
        ]
    
    def analyze(self, market_data: Dict, leads: List[Dict]) -> Dict[str, Any]:
        """
        Analyze competition level for market and leads
        """
        # Detect if competitors are running ads
        competitor_activity = self._detect_competitor_activity(leads)
        
        # Calculate saturation level
        saturation_level = self._calculate_saturation(market_data, leads)
        
        # Identify market gaps
        market_gaps = self._identify_market_gaps(market_data, leads)
        
        # Calculate opportunity score
        opportunity_score = self._calculate_opportunity_score(
            saturation_level, market_gaps, competitor_activity
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            saturation_level, market_gaps, opportunity_score
        )
        
        return {
            "competition_level": saturation_level,
            "competitor_activity": competitor_activity,
            "market_gap": market_gaps,
            "opportunity_score": opportunity_score,
            "recommendations": recommendations,
            "analyzed_at": datetime.now().isoformat()
        }
    
    def _detect_competitor_activity(self, leads: List[Dict]) -> Dict[str, Any]:
        """Detect competitor advertising activity"""
        running_ads_count = sum(1 for l in leads if l.get("running_ads", False))
        total_leads = len(leads)
        
        ads_ratio = running_ads_count / total_leads if total_leads > 0 else 0
        
        return {
            "leads_running_ads": running_ads_count,
            "total_leads": total_leads,
            "ads_penetration": f"{ads_ratio:.1%}",
            "competitor_presence": "HIGH" if ads_ratio >= 0.5 else "MEDIUM" if ads_ratio >= 0.3 else "LOW",
            "intensity": "Aggressive" if ads_ratio >= 0.6 else "Moderate" if ads_ratio >= 0.3 else "Low"
        }
    
    def _calculate_saturation(self, market_data: Dict, leads: List[Dict]) -> str:
        """Calculate market saturation level"""
        # Count leads per industry
        industry_counts = {}
        for lead in leads:
            industry = lead.get("industry", "Unknown")
            industry_counts[industry] = industry_counts.get(industry, 0) + 1
        
        # Calculate average leads per industry
        avg_count = sum(industry_counts.values()) / len(industry_counts) if industry_counts else 0
        
        # Count high-scoring leads (indicates competition for good leads)
        high_score_count = sum(1 for l in leads if l.get("score", 0) >= 70)
        high_score_ratio = high_score_count / len(leads) if leads else 0
        
        # Determine saturation
        if avg_count >= 3 and high_score_ratio >= 0.4:
            return "HIGH"
        elif avg_count >= 2 and high_score_ratio >= 0.2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _identify_market_gaps(self, market_data: Dict, leads: List[Dict]) -> List[Dict]:
        """Identify gaps in the market"""
        gaps = []
        
        # Analyze by score distribution
        low_score_leads = [l for l in leads if l.get("score", 0) < 50]
        if len(low_score_leads) >= 3:
            gaps.append({
                "type": "underserved_segment",
                "description": "Many leads with low scores indicate underserved needs",
                "opportunity": "High - potential to capture unoptimized market"
            })
        
        # Check for industries with few leads but high demand signals
        hot_markets = market_data.get("hot_markets", [])
        for market in hot_markets:
            if market.get("lead_count", 0) <= 2 and market.get("heat_level") == "HOT":
                gaps.append({
                    "type": "emerging_market",
                    "description": f"{market['market']} shows high demand but low lead volume",
                    "opportunity": "HIGH - First mover advantage possible"
                })
        
        # Check for urgency signals without solutions
        if market_data.get("urgency_level") == "HIGH":
            gaps.append({
                "type": "urgent_unmet_need",
                "description": "High urgency signals suggest market needs faster solutions",
                "opportunity": "MEDIUM - Speed as competitive advantage"
            })
        
        return gaps
    
    def _calculate_opportunity_score(self, saturation: str, gaps: List[Dict], 
                                     competitor_activity: Dict) -> int:
        """Calculate overall opportunity score (0-100)"""
        score = 50  # Base score
        
        # Saturation impact
        if saturation == "LOW":
            score += 25
        elif saturation == "MEDIUM":
            score += 10
        else:  # HIGH
            score -= 15
        
        # Gap bonus
        for gap in gaps:
            if "HIGH" in gap.get("opportunity", ""):
                score += 15
            elif "MEDIUM" in gap.get("opportunity", ""):
                score += 8
        
        # Competitor activity impact
        competitor_level = competitor_activity.get("competitor_presence", "LOW")
        if competitor_level == "LOW":
            score += 10
        elif competitor_level == "HIGH":
            score -= 10
        
        return max(0, min(100, score))
    
    def _generate_recommendations(self, saturation: str, gaps: List[Dict], 
                                opportunity_score: int) -> List[str]:
        """Generate strategic recommendations"""
        recommendations = []
        
        if saturation == "HIGH":
            recommendations.append("Market is saturated - focus on differentiation and niche specialization")
        elif saturation == "MEDIUM":
            recommendations.append("Moderate competition - establish positioning quickly")
        else:
            recommendations.append("Low saturation - aggressive market entry recommended")
        
        if opportunity_score >= 75:
            recommendations.append("STRONG OPPORTUNITY - Prioritize this market for immediate campaign launch")
        elif opportunity_score >= 50:
            recommendations.append("MODERATE OPPORTUNITY - Test with limited budget before scaling")
        else:
            recommendations.append("WEAK OPPORTUNITY - Consider alternative markets or approach")
        
        for gap in gaps[:2]:
            if "emerging" in gap.get("type", ""):
                recommendations.append(f"First-mover opportunity in {gap.get('description', 'emerging market')}")
        
        return recommendations


# Example usage
if __name__ == "__main__":
    analyzer = CompetitorAnalyzer()
    
    market = {
        "hot_markets": [{"market": "SaaS", "lead_count": 5, "heat_level": "HOT"}],
        "urgency_level": "HIGH"
    }
    
    leads = [
        {"industry": "SaaS", "running_ads": True, "score": 85},
        {"industry": "SaaS", "running_ads": False, "score": 45}
    ]
    
    result = analyzer.analyze(market, leads)
    print(json.dumps(result, indent=2))
