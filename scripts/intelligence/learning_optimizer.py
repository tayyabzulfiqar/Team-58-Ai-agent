"""
Learning Optimizer - Adjusts scoring weights and strategy priorities based on patterns
"""
import json
import os
from typing import Dict, Any, List


class LearningOptimizer:
    """
    Updates system configuration based on learned patterns
    """
    
    def __init__(self, config_path: str = "config/learning_state.json"):
        self.config_path = config_path
        self.current_weights = self._load_weights()
        self.update_history = []
    
    def _load_weights(self) -> Dict[str, float]:
        """
        Load current weights from config file or use defaults
        """
        defaults = {
            "service_fit": 25,
            "ads_presence": 15,
            "pain_clarity": 20,
            "icp_match": 10,
            "urgency_signals": 15,
            "decision_maker": 10,
            "business_size": 5
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    stored = json.load(f)
                    return stored.get("weights", defaults)
            except:
                return defaults
        
        return defaults
    
    def update(self, pattern_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update weights and priorities based on pattern analysis
        """
        top_patterns = pattern_analysis.get("top_patterns", [])
        weak_patterns = pattern_analysis.get("weak_patterns", [])
        insights = pattern_analysis.get("insights", [])
        
        updates = []
        
        # Adjust weights based on top patterns
        for pattern in top_patterns:
            weight_update = self._adjust_weight_for_pattern(pattern, "increase")
            if weight_update:
                updates.append(weight_update)
        
        # Adjust weights based on weak patterns
        for pattern in weak_patterns:
            weight_update = self._adjust_weight_for_pattern(pattern, "decrease")
            if weight_update:
                updates.append(weight_update)
        
        # Determine strategy priority shifts
        strategy_shifts = self._determine_strategy_shifts(top_patterns, weak_patterns)
        
        # Save updated weights
        self._save_weights()
        
        # Build update report
        update_report = {
            "previous_weights": self._get_previous_weights(),
            "current_weights": self.current_weights.copy(),
            "updates_made": updates,
            "strategy_priority_shifts": strategy_shifts,
            "key_insights": insights[:5],
            "learning_iteration": len(self.update_history) + 1
        }
        
        self.update_history.append(update_report)
        
        return update_report
    
    def _adjust_weight_for_pattern(self, pattern: Dict, direction: str) -> Dict:
        """
        Adjust a specific weight based on pattern data
        """
        pattern_name = pattern.get("pattern", "").lower()
        pattern_type = pattern.get("type", "")
        
        weight_mapping = {
            # Pain points -> pain_clarity weight
            "low roas": "pain_clarity",
            "high cac": "pain_clarity",
            "losing money": "pain_clarity",
            "ads not working": "pain_clarity",
            "scaling": "urgency_signals",
            "hiring": "urgency_signals",
            "need leads": "pain_clarity",
            
            # Angles -> various weights
            "revenue recovery": "pain_clarity",
            "cost reduction": "pain_clarity",
            "growth enablement": "service_fit",
            "lead volume": "service_fit",
            
            # Signals
            "ads": "ads_presence",
            "roas": "pain_clarity",
            "cac": "pain_clarity",
            "conversion": "service_fit",
            "leads": "service_fit",
            "scaling": "urgency_signals",
            "hiring": "urgency_signals",
            "revenue": "business_size",
            "growth": "service_fit",
            "marketing": "service_fit"
        }
        
        # Find matching weight key
        weight_key = None
        for key, mapped_weight in weight_mapping.items():
            if key in pattern_name:
                weight_key = mapped_weight
                break
        
        if not weight_key:
            return None
        
        # Get current weight
        current = self.current_weights.get(weight_key, 10)
        
        # Calculate adjustment
        if direction == "increase":
            adjustment = min(5, max(1, int(current * 0.1)))  # 10% increase, max 5 points
            new_weight = min(35, current + adjustment)  # Cap at 35
        else:
            adjustment = min(3, max(1, int(current * 0.05)))  # 5% decrease, max 3 points
            new_weight = max(0, current - adjustment)
        
        # Update weight
        self.current_weights[weight_key] = new_weight
        
        return {
            "weight_name": weight_key,
            "previous_value": current,
            "new_value": new_weight,
            "adjustment": new_weight - current,
            "reason": f"Pattern '{pattern_name}' appears {direction}ingly in results",
            "pattern_type": pattern_type
        }
    
    def _determine_strategy_shifts(self, top_patterns: List, weak_patterns: List) -> List[Dict]:
        """
        Determine which strategy angles to prioritize or deprioritize
        """
        shifts = []
        
        # Prioritize top performing angles
        for pattern in top_patterns:
            if pattern.get("type") == "angle":
                shifts.append({
                    "action": "prioritize",
                    "angle": pattern["pattern"],
                    "reason": f"High success ratio ({pattern.get('ratio', 0):.1f}x)",
                    "priority_boost": min(20, int(pattern.get('ratio', 1) * 5))
                })
        
        # Deprioritize weak performing angles
        for pattern in weak_patterns:
            if pattern.get("type") == "angle":
                shifts.append({
                    "action": "deprioritize",
                    "angle": pattern["pattern"],
                    "reason": f"Poor performance ({pattern.get('ratio', 0):.1f}x in losers)",
                    "priority_reduction": 10
                })
        
        # Pain-based shifts
        top_pains = [p for p in top_patterns if p.get("type") == "pain"]
        for pain in top_pains[:2]:
            shifts.append({
                "action": "prioritize",
                "strategy_focus": pain["pattern"],
                "reason": "Strong correlation with success",
                "apply_to_hooks": True,
                "apply_to_offers": True
            })
        
        return shifts
    
    def _save_weights(self):
        """
        Save current weights to config file
        """
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        config = {
            "weights": self.current_weights,
            "update_count": len(self.update_history),
            "version": "2.0"
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _get_previous_weights(self) -> Dict:
        """
        Get weights from previous iteration
        """
        if self.update_history:
            return self.update_history[-1].get("current_weights", self.current_weights)
        return self.current_weights
    
    def get_current_config(self) -> Dict[str, Any]:
        """
        Get current optimized configuration
        """
        return {
            "weights": self.current_weights,
            "total_updates": len(self.update_history),
            "config_path": self.config_path
        }
    
    def reset_to_defaults(self):
        """
        Reset weights to default values
        """
        defaults = {
            "service_fit": 25,
            "ads_presence": 15,
            "pain_clarity": 20,
            "icp_match": 10,
            "urgency_signals": 15,
            "decision_maker": 10,
            "business_size": 5
        }
        
        self.current_weights = defaults
        self._save_weights()


# Example usage
if __name__ == "__main__":
    optimizer = LearningOptimizer()
    
    # Simulated pattern analysis
    patterns = {
        "top_patterns": [
            {"type": "pain", "pattern": "low ROAS", "winner_count": 10, "loser_count": 2, "ratio": 5.0}
        ],
        "weak_patterns": [
            {"type": "color", "pattern": "BLACK", "loser_count": 15, "winner_count": 1, "ratio": 15.0}
        ],
        "insights": ["Test insight"]
    }
    
    result = optimizer.update(patterns)
    print(json.dumps(result, indent=2))
