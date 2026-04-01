"""
Positioning Engine - Generates positioning angles and messaging direction
"""
from typing import Dict, Any, List
from datetime import datetime


class PositioningEngine:
    """
    Generates positioning strategy based on market and competitor insights
    """
    
    def __init__(self):
        self.angle_templates = {
            "performance": {
                "name": "Performance Leader",
                "tagline": "We don't just run ads—we optimize for profit",
                "positioning": "ROI-first agency focused on measurable revenue growth",
                "why_us": "Data-driven optimization that prioritizes your bottom line over vanity metrics"
            },
            "speed": {
                "name": "Speed-to-Results",
                "tagline": "Results in weeks, not months",
                "positioning": "Rapid deployment agency for urgent growth needs",
                "why_us": "14-day intensive audits with immediate fixes—not 90-day roadmaps"
            },
            "specialist": {
                "name": "Niche Specialist",
                "tagline": "Deep expertise in {niche}",
                "positioning": "Specialized agency for {niche} companies only",
                "why_us": "Industry-specific playbooks vs generic approaches"
            },
            "premium": {
                "name": "Premium Partner",
                "tagline": "White-glove service for serious growth",
                "positioning": "High-touch agency for established companies",
                "why_us": "Direct access to senior strategists, not junior account managers"
            },
            "disruptor": {
                "name": "Market Disruptor",
                "tagline": "The anti-agency agency",
                "positioning": "Transparent, no-BS approach to paid acquisition",
                "why_us": "No long-term contracts, no hidden fees, no fluff"
            }
        }
    
    def generate(self, strategy: Dict, market_insights: Dict, 
                competitor_insights: Dict) -> Dict[str, Any]:
        """
        Generate positioning based on strategy, market, and competition
        """
        # Select positioning angle
        angle = self._select_angle(strategy, market_insights, competitor_insights)
        
        # Generate positioning statement
        positioning = self._generate_positioning_statement(angle, market_insights)
        
        # Generate unique advantage
        why_us = self._generate_why_us(angle, strategy, competitor_insights)
        
        # Identify market gap used
        market_gap = self._identify_market_gap_used(market_insights, competitor_insights)
        
        # Generate messaging direction
        messaging = self._generate_messaging_direction(angle, strategy)
        
        return {
            "angle": angle["name"],
            "tagline": angle["tagline"],
            "positioning": positioning,
            "why_us": why_us,
            "market_gap_used": market_gap,
            "messaging_direction": messaging,
            "key_differentiators": self._extract_differentiators(angle, competitor_insights),
            "generated_at": datetime.now().isoformat()
        }
    
    def _select_angle(self, strategy: Dict, market: Dict, competitor: Dict) -> Dict:
        """Select the best positioning angle"""
        score = strategy.get("score", 0)
        color = strategy.get("color", "BLACK")
        pain = strategy.get("pain_identified", "")
        urgency = market.get("urgency_level", "LOW")
        saturation = competitor.get("competition_level", "MEDIUM")
        opportunity = competitor.get("opportunity_score", 50)
        
        angle_scores = {}
        
        # Performance angle - best for high-pain, performance issues
        if "ROAS" in pain or "CAC" in pain or "conversion" in pain:
            angle_scores["performance"] = 10
        else:
            angle_scores["performance"] = 5
        
        # Speed angle - best for high urgency
        if urgency == "HIGH":
            angle_scores["speed"] = 10
        elif urgency == "MEDIUM":
            angle_scores["speed"] = 7
        else:
            angle_scores["speed"] = 4
        
        # Specialist angle - best for specific industries
        hot_markets = market.get("hot_markets", [])
        if hot_markets and len(hot_markets) <= 2:
            angle_scores["specialist"] = 9
        else:
            angle_scores["specialist"] = 4
        
        # Premium angle - best for high-value, established markets
        if score >= 80 and saturation == "HIGH":
            angle_scores["premium"] = 9
        else:
            angle_scores["premium"] = 5
        
        # Disruptor angle - best for saturated markets with gaps
        if saturation == "HIGH" and opportunity >= 60:
            angle_scores["disruptor"] = 8
        else:
            angle_scores["disruptor"] = 5
        
        # Select highest scoring angle
        best_angle_key = max(angle_scores, key=angle_scores.get)
        
        # Personalize if specialist
        angle = self.angle_templates[best_angle_key].copy()
        if best_angle_key == "specialist" and hot_markets:
            niche = hot_markets[0].get("market", "B2B")
            angle["tagline"] = angle["tagline"].replace("{niche}", niche)
            angle["positioning"] = angle["positioning"].replace("{niche}", niche)
        
        return angle
    
    def _generate_positioning_statement(self, angle: Dict, market: Dict) -> str:
        """Generate full positioning statement"""
        base = angle.get("positioning", "")
        
        # Add market context
        urgency = market.get("urgency_level", "LOW")
        sentiment = market.get("market_sentiment", "")
        
        if urgency == "HIGH":
            return f"{base} — purpose-built for urgent revenue recovery"
        elif "URGENT_DEMAND" in sentiment:
            return f"{base} — capturing high-demand market opportunity"
        else:
            return base
    
    def _generate_why_us(self, angle: Dict, strategy: Dict, competitor: Dict) -> str:
        """Generate unique advantage statement"""
        base_why = angle.get("why_us", "")
        
        # Add competitive differentiation
        saturation = competitor.get("competition_level", "MEDIUM")
        gaps = competitor.get("market_gap", [])
        
        if saturation == "HIGH":
            base_why += " — while others compete on price, we compete on results"
        
        if gaps and len(gaps) > 0:
            gap_type = gaps[0].get("type", "")
            if "underserved" in gap_type:
                base_why += " — focused on the 90% of companies Big Agencies ignore"
        
        return base_why
    
    def _identify_market_gap_used(self, market: Dict, competitor: Dict) -> str:
        """Identify which market gap the positioning exploits"""
        gaps = competitor.get("market_gap", [])
        urgency = market.get("urgency_level", "LOW")
        
        if gaps:
            primary_gap = gaps[0]
            gap_type = primary_gap.get("type", "")
            
            if "emerging" in gap_type:
                return "First-mover advantage in underserved segment"
            elif "underserved" in gap_type:
                return "Capturing overlooked segment with specialized approach"
            elif "urgent" in gap_type:
                return "Speed as competitive advantage in urgent market"
        
        if urgency == "HIGH":
            return "Meeting urgent demand with rapid response capability"
        
        return "General differentiation through performance focus"
    
    def _generate_messaging_direction(self, angle: Dict, strategy: Dict) -> Dict[str, str]:
        """Generate messaging direction for different channels"""
        angle_name = angle.get("name", "")
        pain = strategy.get("pain_identified", "")
        
        messaging = {
            "headline_tone": "",
            "key_message": "",
            "proof_points": [],
            "emotion": ""
        }
        
        if angle_name == "Performance Leader":
            messaging["headline_tone"] = "Results-focused, data-backed"
            messaging["key_message"] = "We fix broken funnels and recover lost revenue"
            messaging["proof_points"] = ["ROI tracking", "Case studies", "Before/after metrics"]
            messaging["emotion"] = "Confidence, security, relief"
        
        elif angle_name == "Speed-to-Results":
            messaging["headline_tone"] = "Urgent, immediate, action-oriented"
            messaging["key_message"] = "Stop bleeding budget. Start seeing results this month."
            messaging["proof_points"] = ["14-day turnaround", "Quick wins", "No long onboarding"]
            messaging["emotion"] = "Urgency, hope, momentum"
        
        elif angle_name == "Niche Specialist":
            messaging["headline_tone"] = "Expert, insider, authoritative"
            messaging["key_message"] = "Industry-specific strategies that generic agencies can't replicate"
            messaging["proof_points"] = ["Industry expertise", "Specialized tools", "N case studies"]
            messaging["emotion"] = "Trust, expertise, belonging"
        
        elif angle_name == "Premium Partner":
            messaging["headline_tone"] = "Sophisticated, exclusive, high-value"
            messaging["key_message"] = "Senior-level strategy for companies serious about growth"
            messaging["proof_points"] = ["Senior team", "White-glove service", "Strategic partnership"]
            messaging["emotion"] = "Prestige, importance, partnership"
        
        else:  # Disruptor
            messaging["headline_tone"] = "Direct, honest, refreshing"
            messaging["key_message"] = "No contracts. No BS. Just results."
            messaging["proof_points"] = ["Transparent pricing", "Month-to-month", "No hidden fees"]
            messaging["emotion"] = "Trust, relief, empowerment"
        
        return messaging
    
    def _extract_differentiators(self, angle: Dict, competitor: Dict) -> List[str]:
        """Extract key differentiators"""
        differentiators = [angle.get("why_us", "")]
        
        # Add competition-based differentiators
        competitor_level = competitor.get("competitor_presence", "LOW")
        if competitor_level == "HIGH":
            differentiators.append("Differentiated approach in saturated market")
        
        # Add opportunity-based differentiators
        opportunity = competitor.get("opportunity_score", 50)
        if opportunity >= 75:
            differentiators.append("First-mover advantage in high-opportunity market")
        
        return differentiators


# Example usage
if __name__ == "__main__":
    engine = PositioningEngine()
    
    strategy = {"score": 90, "color": "RED", "pain_identified": "low ROAS"}
    market = {"urgency_level": "HIGH", "hot_markets": [{"market": "SaaS"}]}
    competitor = {"competition_level": "MEDIUM", "opportunity_score": 80}
    
    result = engine.generate(strategy, market, competitor)
    print(json.dumps(result, indent=2))
