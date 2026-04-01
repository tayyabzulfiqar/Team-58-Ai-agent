"""
Prediction Engine - Predicts campaign success probability and strength
"""
from typing import Dict, Any
from datetime import datetime


class PredictionEngine:
    """
    Predicts campaign success based on scoring, patterns, and market intelligence
    """
    
    def __init__(self):
        self.success_factors = {
            "score_weight": 0.35,
            "market_weight": 0.25,
            "competition_weight": 0.20,
            "positioning_weight": 0.20
        }
    
    def predict(self, scored_lead: Dict, patterns: Dict, market: Dict, 
               competitor: Dict, positioning: Dict) -> Dict[str, Any]:
        """
        Predict campaign success probability and strength
        """
        # Calculate base probability from score
        score = scored_lead.get("score", 0)
        color = scored_lead.get("color", "BLACK")
        
        # Score factor (0-35 points)
        score_factor = self._calculate_score_factor(score, color)
        
        # Market factor (0-25 points)
        market_factor = self._calculate_market_factor(market)
        
        # Competition factor (0-20 points)
        competition_factor = self._calculate_competition_factor(competitor)
        
        # Positioning factor (0-20 points)
        positioning_factor = self._calculate_positioning_factor(positioning)
        
        # Calculate total probability
        total_probability = score_factor + market_factor + competition_factor + positioning_factor
        
        # Clamp to 0-100
        success_probability = max(0, min(100, total_probability))
        
        # Determine campaign strength
        campaign_strength = self._determine_strength(success_probability, competitor, market)
        
        # Generate prediction insights
        insights = self._generate_insights(
            success_probability, score_factor, market_factor, 
            competition_factor, positioning_factor
        )
        
        # Risk assessment
        risks = self._assess_risks(scored_lead, competitor, market)
        
        return {
            "success_probability": round(success_probability),
            "campaign_strength": campaign_strength,
            "score_contribution": round(score_factor, 1),
            "market_contribution": round(market_factor, 1),
            "competition_contribution": round(competition_factor, 1),
            "positioning_contribution": round(positioning_factor, 1),
            "insights": insights,
            "risks": risks,
            "predicted_outcome": self._predict_outcome(success_probability, campaign_strength),
            "generated_at": datetime.now().isoformat()
        }
    
    def _calculate_score_factor(self, score: int, color: str) -> float:
        """Calculate contribution from lead score (max 35 points)"""
        base = (score / 100) * 35
        
        # Color bonus
        color_bonus = {
            "RED": 5,
            "ORANGE": 2,
            "YELLOW": 0,
            "BLACK": -10
        }.get(color, 0)
        
        return base + color_bonus
    
    def _calculate_market_factor(self, market: Dict) -> float:
        """Calculate contribution from market conditions (max 25 points)"""
        factor = 12.5  # Base neutral score
        
        # Urgency bonus
        urgency = market.get("urgency_level", "LOW")
        if urgency == "HIGH":
            factor += 7.5
        elif urgency == "MEDIUM":
            factor += 3
        
        # Sentiment bonus
        sentiment = market.get("market_sentiment", "")
        if "URGENT_DEMAND" in sentiment:
            factor += 5
        elif "PROBLEM_AWARE" in sentiment:
            factor += 2.5
        
        # Hot markets bonus
        hot_markets = market.get("hot_markets", [])
        hot_count = sum(1 for m in hot_markets if m.get("heat_level") == "HOT")
        factor += min(5, hot_count * 2.5)
        
        return min(25, factor)
    
    def _calculate_competition_factor(self, competitor: Dict) -> float:
        """Calculate contribution from competition analysis (max 20 points)"""
        opportunity_score = competitor.get("opportunity_score", 50)
        saturation = competitor.get("competition_level", "MEDIUM")
        
        # Base from opportunity score
        base = (opportunity_score / 100) * 15
        
        # Saturation adjustment
        saturation_bonus = {
            "LOW": 5,
            "MEDIUM": 2,
            "HIGH": -5
        }.get(saturation, 0)
        
        return max(0, min(20, base + saturation_bonus))
    
    def _calculate_positioning_factor(self, positioning: Dict) -> float:
        """Calculate contribution from positioning (max 20 points)"""
        factor = 10  # Base score
        
        angle = positioning.get("angle", "")
        
        # Strong angles get bonus
        strong_angles = ["Performance Leader", "Speed-to-Results", "Niche Specialist"]
        if any(a in angle for a in strong_angles):
            factor += 5
        
        # Market gap exploitation bonus
        market_gap = positioning.get("market_gap_used", "")
        if "First-mover" in market_gap or "advantage" in market_gap:
            factor += 5
        
        return min(20, factor)
    
    def _determine_strength(self, probability: float, competitor: Dict, market: Dict) -> str:
        """Determine campaign strength category"""
        opportunity = competitor.get("opportunity_score", 50)
        saturation = competitor.get("competition_level", "MEDIUM")
        urgency = market.get("urgency_level", "LOW")
        
        # DOMINANT: High probability + good conditions
        if probability >= 80 and opportunity >= 70:
            return "DOMINANT"
        
        # STRONG: Good probability or excellent conditions
        if probability >= 70:
            return "STRONG"
        if probability >= 60 and (urgency == "HIGH" or saturation == "LOW"):
            return "STRONG"
        
        # MODERATE: Decent probability
        if probability >= 50:
            return "MODERATE"
        
        # WEAK: Low probability
        return "WEAK"
    
    def _generate_insights(self, total: float, score_f: float, market_f: float,
                          comp_f: float, pos_f: float) -> list:
        """Generate prediction insights"""
        insights = []
        
        # Overall assessment
        if total >= 80:
            insights.append("HIGH PROBABILITY: All factors align for success")
        elif total >= 65:
            insights.append("GOOD PROBABILITY: Strong positioning with favorable conditions")
        elif total >= 50:
            insights.append("MODERATE PROBABILITY: Viable but requires careful execution")
        else:
            insights.append("CHALLENGING: Consider optimizing approach or targeting")
        
        # Factor-specific insights
        max_factor = max([("Lead quality", score_f), ("Market conditions", market_f),
                         ("Competition", comp_f), ("Positioning", pos_f)], key=lambda x: x[1])
        
        min_factor = min([("Lead quality", score_f), ("Market conditions", market_f),
                         ("Competition", comp_f), ("Positioning", pos_f)], key=lambda x: x[1])
        
        insights.append(f"Strongest factor: {max_factor[0]} ({max_factor[1]:.1f}/35)")
        
        if min_factor[1] < 10:
            insights.append(f"Improvement needed: {min_factor[0]} ({min_factor[1]:.1f}/35)")
        
        return insights
    
    def _assess_risks(self, lead: Dict, competitor: Dict, market: Dict) -> list:
        """Assess potential risks"""
        risks = []
        
        score = lead.get("score", 0)
        if score < 50:
            risks.append("LOW SCORE: Lead quality may limit campaign effectiveness")
        
        saturation = competitor.get("competition_level", "MEDIUM")
        if saturation == "HIGH":
            risks.append("HIGH COMPETITION: Differentiation critical for success")
        
        urgency = market.get("urgency_level", "LOW")
        if urgency == "LOW":
            risks.append("LOW URGENCY: Longer sales cycle expected")
        
        if not risks:
            risks.append("LOW RISK: Favorable conditions for campaign success")
        
        return risks
    
    def _predict_outcome(self, probability: float, strength: str) -> str:
        """Predict campaign outcome"""
        if probability >= 85:
            return "Highly likely to generate qualified opportunities within 30 days"
        elif probability >= 70:
            return "Good chance of success with consistent execution"
        elif probability >= 55:
            return "Moderate success expected - optimize based on early results"
        elif probability >= 40:
            return "Challenging - may require significant optimization or pivot"
        else:
            return "Low probability - consider alternative approach or targeting"


# Example usage
if __name__ == "__main__":
    engine = PredictionEngine()
    
    lead = {"score": 90, "color": "RED"}
    patterns = {"top_patterns": [{"pattern": "low ROAS"}]}
    market = {"urgency_level": "HIGH", "market_sentiment": "URGENT_DEMAND"}
    competitor = {"opportunity_score": 80, "competition_level": "MEDIUM"}
    positioning = {"angle": "Performance Leader", "market_gap_used": "First-mover"}
    
    result = engine.predict(lead, patterns, market, competitor, positioning)
    print(json.dumps(result, indent=2))
