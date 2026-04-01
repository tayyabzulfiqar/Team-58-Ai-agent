"""
Feedback Analyzer - Analyzes past results and simulates outcomes
"""
import random
import json
from typing import Dict, Any, List
from datetime import datetime


class FeedbackAnalyzer:
    """
    Analyzes scored leads and strategies, simulates outcomes
    """
    
    def __init__(self):
        self.evaluated_results = []
        self.success_patterns = []
        self.failure_patterns = []
    
    def analyze(self, leads: List[Dict], strategies: List[Dict]) -> Dict[str, Any]:
        """
        Analyze leads and strategies, simulate outcomes
        """
        results = []
        
        for lead, strategy in zip(leads, strategies):
            # Simulate strategy quality (1-10)
            strategy_quality = random.randint(5, 10) if strategy.get("color") != "BLACK" else random.randint(1, 4)
            
            # Determine predicted success based on multiple factors
            predicted_success = self._predict_success(lead, strategy, strategy_quality)
            
            # Calculate confidence score
            confidence = self._calculate_confidence(lead, strategy_quality)
            
            result = {
                "lead": lead.get("company_name", "Unknown"),
                "score": lead.get("score", 0),
                "color": lead.get("color", "BLACK"),
                "strategy_quality": strategy_quality,
                "predicted_success": predicted_success,
                "confidence": confidence,
                "reasons": lead.get("reason", []),
                "pain": strategy.get("pain_identified", ""),
                "angle": strategy.get("angle", ""),
                "channels": strategy.get("channel", []),
                "evaluated_at": datetime.now().isoformat()
            }
            
            results.append(result)
        
        # Calculate summary stats
        total = len(results)
        predicted_wins = sum(1 for r in results if r["predicted_success"])
        avg_quality = sum(r["strategy_quality"] for r in results) / total if total else 0
        
        # Identify strong and weak signals
        success_signals = self._extract_signals([r for r in results if r["predicted_success"]])
        failure_signals = self._extract_signals([r for r in results if not r["predicted_success"]])
        
        self.evaluated_results = results
        
        return {
            "total_analyzed": total,
            "predicted_wins": predicted_wins,
            "predicted_losses": total - predicted_wins,
            "win_rate": predicted_wins / total if total else 0,
            "avg_strategy_quality": avg_quality,
            "success_signals": success_signals,
            "failure_signals": failure_signals,
            "results": results
        }
    
    def _predict_success(self, lead: Dict, strategy: Dict, quality: int) -> bool:
        """
        Predict success based on lead score, strategy quality, and signals
        """
        score = lead.get("score", 0)
        color = strategy.get("color", "BLACK")
        
        # Base probability from score
        base_prob = score / 100
        
        # Quality adjustment
        quality_boost = (quality - 5) / 20  # -0.2 to +0.25
        
        # Color adjustment
        color_boost = {
            "RED": 0.3,
            "ORANGE": 0.15,
            "YELLOW": 0.05,
            "BLACK": -0.4
        }.get(color, 0)
        
        # Final probability
        final_prob = base_prob + quality_boost + color_boost
        final_prob = max(0.05, min(0.95, final_prob))
        
        # Return prediction
        return random.random() < final_prob
    
    def _calculate_confidence(self, lead: Dict, strategy_quality: int) -> float:
        """
        Calculate confidence in prediction
        """
        score = lead.get("score", 0)
        
        # High scores with high quality = high confidence
        if score >= 85 and strategy_quality >= 8:
            return random.uniform(0.85, 0.95)
        elif score >= 65 and strategy_quality >= 6:
            return random.uniform(0.70, 0.85)
        elif score >= 40:
            return random.uniform(0.50, 0.70)
        else:
            return random.uniform(0.30, 0.50)
    
    def _extract_signals(self, results: List[Dict]) -> Dict[str, int]:
        """
        Extract signal frequency from results
        """
        signals = {}
        
        for result in results:
            # Extract from reasons
            for reason in result.get("reasons", []):
                # Extract key terms
                key_terms = [
                    "ads", "ROAS", "CAC", "conversion", "leads", "scaling",
                    "hiring", "revenue", "growth", "marketing"
                ]
                for term in key_terms:
                    if term.lower() in reason.lower():
                        signals[term] = signals.get(term, 0) + 1
            
            # Extract from pain
            pain = result.get("pain", "")
            if pain:
                signals[pain] = signals.get(pain, 0) + 1
            
            # Extract from angle
            angle = result.get("angle", "")
            if angle:
                signals[angle] = signals.get(angle, 0) + 1
        
        return signals


# Example usage
if __name__ == "__main__":
    analyzer = FeedbackAnalyzer()
    
    test_leads = [
        {"company_name": "Test Co", "score": 90, "color": "RED", "reason": ["Running ads", "Low ROAS"]},
        {"company_name": "Test Co 2", "score": 50, "color": "ORANGE", "reason": ["Some activity"]}
    ]
    
    test_strategies = [
        {"color": "RED", "pain_identified": "low ROAS", "angle": "Revenue Recovery", "channel": ["email"]},
        {"color": "ORANGE", "pain_identified": "need leads", "angle": "Lead Volume", "channel": ["email"]}
    ]
    
    result = analyzer.analyze(test_leads, test_strategies)
    print(json.dumps(result, indent=2))
