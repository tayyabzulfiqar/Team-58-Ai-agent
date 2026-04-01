"""
Learning Updater - Updates weights based on real feedback vs predictions
"""
import json
import os
import logging
from typing import Dict, Any, List
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LearningUpdater:
    """
    Updates scoring weights based on real outcomes vs predictions
    """
    
    def __init__(self, weights_path: str = "config/weights.json"):
        self.weights_path = weights_path
        self.current_weights = self._load_weights()
        self.learning_history = []
        
    def _load_weights(self) -> Dict[str, float]:
        """Load current weights from config"""
        defaults = {
            "service_fit": 25,
            "ads_presence": 15,
            "pain_clarity": 20,
            "icp_match": 10,
            "urgency_signals": 15,
            "decision_maker": 10,
            "business_size": 5
        }
        
        if os.path.exists(self.weights_path):
            try:
                with open(self.weights_path, 'r') as f:
                    stored = json.load(f)
                    return stored.get("weights", defaults)
            except Exception as e:
                logger.error(f"Error loading weights: {e}")
                return defaults
        
        return defaults
    
    def update_from_feedback(self, predictions: List[Dict], feedback: List[Dict], 
                            patterns: Dict = None) -> Dict[str, Any]:
        """
        Update weights based on prediction accuracy from real feedback
        """
        if not predictions or not feedback:
            logger.warning("No data available for learning update")
            return {
                "updated": False,
                "reason": "Missing predictions or feedback",
                "current_weights": self.current_weights
            }
        
        updates = []
        
        # Compare each prediction with actual outcome
        for pred, actual in zip(predictions, feedback):
            predicted_prob = pred.get("success_probability", 50)
            predicted_success = predicted_prob >= 70
            actual_success = actual.get("conversion", False) or actual.get("meeting_booked", False)
            
            # Determine if prediction was accurate
            if predicted_success and not actual_success:
                # Predicted HIGH but failed - reduce weights
                weight_update = self._adjust_weight("reduce", "overprediction")
                if weight_update:
                    updates.append(weight_update)
                    
            elif not predicted_success and actual_success:
                # Predicted LOW but succeeded - increase weights  
                weight_update = self._adjust_weight("increase", "underprediction")
                if weight_update:
                    updates.append(weight_update)
        
        # Update pattern strength if patterns provided
        if patterns:
            pattern_updates = self._update_pattern_strengths(patterns, feedback)
            updates.extend(pattern_updates)
        
        # Save updated weights
        self._save_weights()
        
        # Record learning iteration
        learning_record = {
            "timestamp": datetime.now().isoformat(),
            "total_comparisons": len(predictions),
            "updates_made": len(updates),
            "updates": updates,
            "weights_after": self.current_weights.copy()
        }
        self.learning_history.append(learning_record)
        
        logger.info(f"Learning update complete: {len(updates)} weight adjustments")
        
        return {
            "updated": True,
            "updates_made": updates,
            "current_weights": self.current_weights,
            "learning_iteration": len(self.learning_history)
        }
    
    def _adjust_weight(self, direction: str, reason: str) -> Dict:
        """
        Adjust weights based on prediction accuracy
        """
        # Find most impactful weight to adjust
        # For simplicity, adjust pain_clarity and service_fit as primary drivers
        
        target_weights = ["pain_clarity", "service_fit", "ads_presence"]
        
        updates = []
        for weight_name in target_weights:
            current = self.current_weights.get(weight_name, 10)
            
            if direction == "increase":
                # Increase by 10% or minimum 1 point
                adjustment = max(1, int(current * 0.1))
                new_value = min(40, current + adjustment)  # Cap at 40
            else:  # reduce
                # Decrease by 10% or minimum 1 point
                adjustment = max(1, int(current * 0.1))
                new_value = max(0, current - adjustment)
            
            self.current_weights[weight_name] = new_value
            
            updates.append({
                "weight": weight_name,
                "previous": current,
                "new": new_value,
                "change": new_value - current,
                "reason": reason
            })
        
        return updates[0] if updates else None  # Return first update as representative
    
    def _update_pattern_strengths(self, patterns: Dict, feedback: List[Dict]) -> List[Dict]:
        """
        Update pattern strengths based on real feedback
        """
        updates = []
        
        top_patterns = patterns.get("top_patterns", [])
        
        for pattern in top_patterns:
            pattern_name = pattern.get("pattern", "")
            
            # Check if this pattern appeared in successful conversions
            success_count = 0
            for fb in feedback:
                if fb.get("conversion", False):
                    metadata = fb.get("metadata", {})
                    if pattern_name.lower() in str(metadata).lower():
                        success_count += 1
            
            # Update pattern strength
            if success_count >= 2:
                updates.append({
                    "type": "pattern_strength",
                    "pattern": pattern_name,
                    "adjustment": "increase",
                    "reason": f"Appeared in {success_count} successful conversions"
                })
            elif success_count == 0 and len(feedback) >= 3:
                updates.append({
                    "type": "pattern_strength",
                    "pattern": pattern_name,
                    "adjustment": "decrease",
                    "reason": "No correlation with actual conversions"
                })
        
        return updates
    
    def _save_weights(self):
        """Save updated weights to config file"""
        try:
            os.makedirs(os.path.dirname(self.weights_path), exist_ok=True)
            
            config = {
                "weights": self.current_weights,
                "last_updated": datetime.now().isoformat(),
                "update_count": len(self.learning_history),
                "version": "2.0"
            }
            
            with open(self.weights_path, 'w') as f:
                json.dump(config, f, indent=2)
                
            logger.info(f"Weights saved to {self.weights_path}")
            
        except Exception as e:
            logger.error(f"Error saving weights: {e}")
    
    def get_weight_adjustment_summary(self) -> Dict[str, Any]:
        """Get summary of all weight adjustments made"""
        if not self.learning_history:
            return {
                "total_iterations": 0,
                "current_weights": self.current_weights,
                "adjustments": []
            }
        
        all_adjustments = []
        for record in self.learning_history:
            all_adjustments.extend(record.get("updates", []))
        
        return {
            "total_iterations": len(self.learning_history),
            "current_weights": self.current_weights,
            "total_adjustments": len(all_adjustments),
            "adjustments": all_adjustments[-10:]  # Last 10
        }
    
    def reset_weights(self):
        """Reset weights to defaults"""
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
        logger.info("Weights reset to defaults")


# Example usage
if __name__ == "__main__":
    updater = LearningUpdater()
    
    # Test with sample predictions and feedback
    predictions = [
        {"success_probability": 85},  # Predicted high
        {"success_probability": 45},  # Predicted low
    ]
    
    feedback = [
        {"conversion": False, "meeting_booked": False},  # Actually failed (overprediction)
        {"conversion": True, "meeting_booked": True},    # Actually succeeded (underprediction)
    ]
    
    result = updater.update_from_feedback(predictions, feedback)
    print(json.dumps(result, indent=2))
