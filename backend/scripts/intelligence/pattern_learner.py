"""
Pattern Learner - Detects patterns in feedback results
"""
import json
from typing import Dict, Any, List
from collections import Counter


class PatternLearner:
    """
    Analyzes results and detects success/failure patterns
    """
    
    def __init__(self):
        self.top_patterns = []
        self.weak_patterns = []
        self.insights = []
    
    def analyze(self, feedback_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze feedback results and detect patterns
        """
        results = feedback_results.get("results", [])
        
        if not results:
            return {
                "top_patterns": [],
                "weak_patterns": [],
                "insights": ["No data to analyze"]
            }
        
        # Separate winners and losers
        winners = [r for r in results if r["predicted_success"]]
        losers = [r for r in results if not r["predicted_success"]]
        
        # Analyze patterns in winners
        winner_patterns = self._analyze_patterns(winners)
        
        # Analyze patterns in losers
        loser_patterns = self._analyze_patterns(losers)
        
        # Identify top patterns (strong in winners, weak in losers)
        top_patterns = self._identify_top_patterns(winner_patterns, loser_patterns)
        
        # Identify weak patterns (strong in losers, weak in winners)
        weak_patterns = self._identify_weak_patterns(winner_patterns, loser_patterns)
        
        # Generate insights
        insights = self._generate_insights(winners, losers, top_patterns, weak_patterns)
        
        self.top_patterns = top_patterns
        self.weak_patterns = weak_patterns
        self.insights = insights
        
        return {
            "total_winners": len(winners),
            "total_losers": len(losers),
            "top_patterns": top_patterns,
            "weak_patterns": weak_patterns,
            "insights": insights,
            "winner_patterns": winner_patterns,
            "loser_patterns": loser_patterns
        }
    
    def _analyze_patterns(self, results: List[Dict]) -> Dict[str, Any]:
        """
        Analyze patterns in a set of results
        """
        patterns = {
            "colors": Counter(),
            "scores": [],
            "pains": Counter(),
            "angles": Counter(),
            "channels": Counter(),
            "signals": Counter(),
            "avg_quality": 0
        }
        
        qualities = []
        
        for result in results:
            # Color distribution
            patterns["colors"][result.get("color", "UNKNOWN")] += 1
            
            # Score distribution
            patterns["scores"].append(result.get("score", 0))
            
            # Pain points
            pain = result.get("pain", "")
            if pain:
                patterns["pains"][pain] += 1
            
            # Angles
            angle = result.get("angle", "")
            if angle:
                patterns["angles"][angle] += 1
            
            # Channels
            for channel in result.get("channels", []):
                patterns["channels"][channel] += 1
            
            # Extract signals from reasons
            for reason in result.get("reasons", []):
                signals = self._extract_signal_keywords(reason)
                for sig in signals:
                    patterns["signals"][sig] += 1
            
            qualities.append(result.get("strategy_quality", 5))
        
        patterns["avg_quality"] = sum(qualities) / len(qualities) if qualities else 0
        patterns["avg_score"] = sum(patterns["scores"]) / len(patterns["scores"]) if patterns["scores"] else 0
        
        return patterns
    
    def _extract_signal_keywords(self, text: str) -> List[str]:
        """
        Extract relevant signal keywords from text
        """
        keywords = [
            "ads", "ROAS", "CAC", "conversion", "leads", "scaling",
            "hiring", "revenue", "growth", "marketing", "budget",
            "performance", "funnel", "optimization"
        ]
        
        found = []
        text_lower = text.lower()
        
        for kw in keywords:
            if kw in text_lower:
                found.append(kw)
        
        return found
    
    def _identify_top_patterns(self, winner_patterns: Dict, loser_patterns: Dict) -> List[Dict]:
        """
        Identify patterns that appear strongly in winners but weakly in losers
        """
        top = []
        
        # Check pains
        winner_pains = winner_patterns.get("pains", {})
        loser_pains = loser_patterns.get("pains", {})
        
        for pain, count in winner_pains.most_common(5):
            loser_count = loser_pains.get(pain, 0)
            ratio = count / (loser_count + 1)  # Avoid division by zero
            
            if ratio >= 2 and count >= 2:
                top.append({
                    "type": "pain",
                    "pattern": pain,
                    "winner_count": count,
                    "loser_count": loser_count,
                    "ratio": ratio,
                    "strength": "high"
                })
        
        # Check angles
        winner_angles = winner_patterns.get("angles", {})
        loser_angles = loser_patterns.get("angles", {})
        
        for angle, count in winner_angles.most_common(5):
            loser_count = loser_angles.get(angle, 0)
            ratio = count / (loser_count + 1)
            
            if ratio >= 2 and count >= 2:
                top.append({
                    "type": "angle",
                    "pattern": angle,
                    "winner_count": count,
                    "loser_count": loser_count,
                    "ratio": ratio,
                    "strength": "high"
                })
        
        # Check signals
        winner_signals = winner_patterns.get("signals", {})
        loser_signals = loser_patterns.get("signals", {})
        
        for signal, count in winner_signals.most_common(5):
            loser_count = loser_signals.get(signal, 0)
            ratio = count / (loser_count + 1)
            
            if ratio >= 1.5 and count >= 3:
                top.append({
                    "type": "signal",
                    "pattern": signal,
                    "winner_count": count,
                    "loser_count": loser_count,
                    "ratio": ratio,
                    "strength": "medium" if ratio < 2 else "high"
                })
        
        # Sort by ratio
        top.sort(key=lambda x: x["ratio"], reverse=True)
        
        return top[:10]  # Top 10
    
    def _identify_weak_patterns(self, winner_patterns: Dict, loser_patterns: Dict) -> List[Dict]:
        """
        Identify patterns that appear strongly in losers but weakly in winners
        """
        weak = []
        
        # Check pains
        winner_pains = winner_patterns.get("pains", {})
        loser_pains = loser_patterns.get("pains", {})
        
        for pain, count in loser_pains.most_common(5):
            winner_count = winner_pains.get(pain, 0)
            ratio = count / (winner_count + 1)
            
            if ratio >= 2 and count >= 2:
                weak.append({
                    "type": "pain",
                    "pattern": pain,
                    "loser_count": count,
                    "winner_count": winner_count,
                    "ratio": ratio,
                    "issue": "strong_in_losers"
                })
        
        # Check colors
        winner_colors = winner_patterns.get("colors", {})
        loser_colors = loser_patterns.get("colors", {})
        
        for color, count in loser_colors.most_common():
            winner_count = winner_colors.get(color, 0)
            ratio = count / (winner_count + 1)
            
            if ratio >= 3 and count >= 3:
                weak.append({
                    "type": "color",
                    "pattern": color,
                    "loser_count": count,
                    "winner_count": winner_count,
                    "ratio": ratio,
                    "issue": "poor_performing_segment"
                })
        
        # Sort by ratio
        weak.sort(key=lambda x: x["ratio"], reverse=True)
        
        return weak[:5]
    
    def _generate_insights(self, winners: List, losers: List, 
                          top_patterns: List, weak_patterns: List) -> List[str]:
        """
        Generate actionable insights from pattern analysis
        """
        insights = []
        
        # Overall performance
        total = len(winners) + len(losers)
        win_rate = len(winners) / total if total else 0
        
        insights.append(f"Overall win rate: {win_rate:.1%} ({len(winners)}/{total})")
        
        # Top pattern insights
        if top_patterns:
            insights.append("Strong signals in winning leads:")
            for p in top_patterns[:3]:
                insights.append(f"  • {p['pattern']}: {p['winner_count']}x winners vs {p['loser_count']}x losers")
        
        # Weak pattern insights
        if weak_patterns:
            insights.append("Warning signals in losing leads:")
            for p in weak_patterns[:3]:
                insights.append(f"  • {p['pattern']}: appears {p['ratio']:.1f}x more in losers")
        
        # Score insights
        winner_scores = [w.get("score", 0) for w in winners]
        loser_scores = [l.get("score", 0) for l in losers]
        
        if winner_scores and loser_scores:
            avg_winner = sum(winner_scores) / len(winner_scores)
            avg_loser = sum(loser_scores) / len(loser_scores)
            
            insights.append(f"Average winner score: {avg_winner:.1f}")
            insights.append(f"Average loser score: {avg_loser:.1f}")
            
            if avg_winner - avg_loser > 20:
                insights.append("Score threshold is well-calibrated")
            elif avg_winner - avg_loser < 10:
                insights.append("WARNING: Scoring may need recalibration")
        
        # Recommendations
        if top_patterns:
            top_signal = top_patterns[0]["pattern"]
            insights.append(f"RECOMMENDATION: Increase weight for '{top_signal}' in scoring")
        
        if weak_patterns:
            weak_signal = weak_patterns[0]["pattern"]
            insights.append(f"RECOMMENDATION: Decrease weight for '{weak_signal}' or investigate cause")
        
        return insights


# Example usage
if __name__ == "__main__":
    learner = PatternLearner()
    
    # Simulated feedback results
    feedback = {
        "results": [
            {"predicted_success": True, "color": "RED", "score": 90, "pain": "low ROAS", "angle": "Revenue Recovery", "channels": ["email"], "reasons": ["Running ads", "Low ROAS"]},
            {"predicted_success": False, "color": "BLACK", "score": 30, "pain": "none", "angle": "None", "channels": [], "reasons": ["No activity"]}
        ]
    }
    
    result = learner.analyze(feedback)
    print(json.dumps(result, indent=2))
