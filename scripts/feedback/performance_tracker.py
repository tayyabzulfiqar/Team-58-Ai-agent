"""
Performance Tracker - Aggregates real campaign metrics
"""
import json
import os
import logging
from typing import Dict, Any, List
from collections import defaultdict
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceTracker:
    """
    Tracks and aggregates real performance metrics from campaign feedback
    """
    
    def __init__(self, base_path: str = "data/feedback"):
        self.base_path = base_path
        
    def track_performance(self, session_id: str = None, feedback_list: List[Dict] = None) -> Dict[str, Any]:
        """
        Calculate performance metrics from real feedback
        """
        # Load feedback if not provided
        if feedback_list is None:
            feedback_list = self._load_feedback(session_id)
        
        if not feedback_list:
            logger.warning(f"No feedback data available for tracking")
            return {
                "total_leads": 0,
                "conversions": 0,
                "conversion_rate": 0.0,
                "total_revenue": 0,
                "average_deal_size": 0,
                "meetings_booked": 0,
                "average_response_rate": 0.0,
                "top_performing_segment": None,
                "low_performing_segment": None,
                "feedback_available": False
            }
        
        # Aggregate metrics
        total_leads = len(feedback_list)
        conversions = sum(1 for f in feedback_list if f.get("conversion", False))
        meetings_booked = sum(1 for f in feedback_list if f.get("meeting_booked", False))
        total_revenue = sum(f.get("revenue", 0) for f in feedback_list)
        
        # Calculate rates
        conversion_rate = conversions / total_leads if total_leads > 0 else 0.0
        
        # Average deal size (only for converted leads)
        converted_revenues = [f.get("revenue", 0) for f in feedback_list if f.get("conversion", False)]
        average_deal_size = sum(converted_revenues) / len(converted_revenues) if converted_revenues else 0
        
        # Average response rate
        response_rates = [f.get("response_rate", 0) for f in feedback_list if f.get("response_rate") is not None]
        average_response_rate = sum(response_rates) / len(response_rates) if response_rates else 0.0
        
        # Segment analysis (requires metadata)
        segment_performance = self._analyze_segments(feedback_list)
        
        top_segment = max(segment_performance.items(), key=lambda x: x[1]["conversion_rate"]) if segment_performance else (None, {})
        low_segment = min(segment_performance.items(), key=lambda x: x[1]["conversion_rate"]) if segment_performance else (None, {})
        
        metrics = {
            "total_leads": total_leads,
            "conversions": conversions,
            "conversion_rate": round(conversion_rate, 4),
            "total_revenue": round(total_revenue, 2),
            "average_deal_size": round(average_deal_size, 2),
            "meetings_booked": meetings_booked,
            "average_response_rate": round(average_response_rate, 4),
            "top_performing_segment": {
                "segment": top_segment[0],
                "conversion_rate": round(top_segment[1].get("conversion_rate", 0), 4),
                "revenue": top_segment[1].get("total_revenue", 0)
            } if top_segment[0] else None,
            "low_performing_segment": {
                "segment": low_segment[0],
                "conversion_rate": round(low_segment[1].get("conversion_rate", 0), 4),
                "revenue": low_segment[1].get("total_revenue", 0)
            } if low_segment[0] else None,
            "feedback_available": True,
            "segment_breakdown": segment_performance,
            "tracked_at": datetime.now().isoformat()
        }
        
        logger.info(f"Performance tracked: {metrics['conversion_rate']:.1%} conversion rate, ${metrics['total_revenue']} revenue")
        
        return metrics
    
    def _load_feedback(self, session_id: str = None) -> List[Dict]:
        """Load feedback from storage"""
        if session_id:
            feedback_file = os.path.join(self.base_path, session_id, "feedback.json")
            if os.path.exists(feedback_file):
                try:
                    with open(feedback_file, 'r') as f:
                        data = json.load(f)
                        return data if isinstance(data, list) else [data]
                except Exception as e:
                    logger.error(f"Error loading feedback: {e}")
                    return []
        else:
            # Load all sessions
            all_feedback = []
            if os.path.exists(self.base_path):
                for sid in os.listdir(self.base_path):
                    session_feedback = self._load_feedback(sid)
                    all_feedback.extend(session_feedback)
            return all_feedback
        
        return []
    
    def _analyze_segments(self, feedback_list: List[Dict]) -> Dict[str, Dict]:
        """Analyze performance by segment"""
        segments = defaultdict(lambda: {"leads": 0, "conversions": 0, "total_revenue": 0})
        
        for feedback in feedback_list:
            # Extract segment from metadata
            metadata = feedback.get("metadata", {})
            segment = metadata.get("segment", metadata.get("industry", "Unknown"))
            color = metadata.get("color", "Unknown")
            
            # Use color + industry as segment key
            segment_key = f"{color}_{segment}" if color != "Unknown" else segment
            
            segments[segment_key]["leads"] += 1
            if feedback.get("conversion", False):
                segments[segment_key]["conversions"] += 1
            segments[segment_key]["total_revenue"] += feedback.get("revenue", 0)
        
        # Calculate conversion rates
        for segment, data in segments.items():
            data["conversion_rate"] = data["conversions"] / data["leads"] if data["leads"] > 0 else 0
        
        return dict(segments)
    
    def compare_prediction_vs_reality(self, predictions: List[Dict], feedback: List[Dict]) -> Dict[str, Any]:
        """
        Compare predicted outcomes with actual outcomes
        """
        if not predictions or not feedback:
            return {"comparison_available": False}
        
        comparisons = []
        accuracy_count = 0
        
        for pred, actual in zip(predictions, feedback):
            predicted_prob = pred.get("success_probability", 50)
            predicted_success = predicted_prob >= 70  # Threshold for predicted success
            actual_success = actual.get("conversion", False) or actual.get("meeting_booked", False)
            
            accurate = (predicted_success and actual_success) or (not predicted_success and not actual_success)
            if accurate:
                accuracy_count += 1
            
            comparison = {
                "lead_id": actual.get("lead_id"),
                "predicted_probability": predicted_prob,
                "predicted_success": predicted_success,
                "actual_success": actual_success,
                "accurate": accurate,
                "revenue": actual.get("revenue", 0)
            }
            comparisons.append(comparison)
        
        total = len(comparisons)
        accuracy_rate = accuracy_count / total if total > 0 else 0
        
        return {
            "comparison_available": True,
            "total_comparisons": total,
            "accurate_predictions": accuracy_count,
            "accuracy_rate": round(accuracy_rate, 4),
            "comparisons": comparisons,
            "prediction_quality": "HIGH" if accuracy_rate >= 0.7 else "MEDIUM" if accuracy_rate >= 0.5 else "LOW"
        }
    
    def generate_performance_report(self, session_id: str = None) -> Dict[str, Any]:
        """
        Generate comprehensive performance report
        """
        metrics = self.track_performance(session_id)
        
        # Add trend analysis if multiple sessions
        all_feedback = self._load_feedback()
        
        report = {
            "report_type": "performance_summary",
            "session_id": session_id,
            "metrics": metrics,
            "generated_at": datetime.now().isoformat(),
            "recommendations": self._generate_recommendations(metrics)
        }
        
        return report
    
    def _generate_recommendations(self, metrics: Dict) -> List[str]:
        """Generate recommendations based on metrics"""
        recommendations = []
        
        if not metrics.get("feedback_available", False):
            recommendations.append("No feedback data available - collect real outcomes to enable learning")
            return recommendations
        
        conversion_rate = metrics.get("conversion_rate", 0)
        
        if conversion_rate >= 0.3:
            recommendations.append("Excellent conversion rate - scale this approach")
        elif conversion_rate >= 0.15:
            recommendations.append("Good conversion rate - optimize targeting for better results")
        elif conversion_rate >= 0.05:
            recommendations.append("Below average conversion - review lead quality and messaging")
        else:
            recommendations.append("Poor conversion rate - significant strategy adjustment needed")
        
        top_segment = metrics.get("top_performing_segment")
        if top_segment and top_segment.get("segment"):
            recommendations.append(f"Prioritize {top_segment['segment']} segment (highest conversion)")
        
        low_segment = metrics.get("low_performing_segment")
        if low_segment and low_segment.get("segment"):
            recommendations.append(f"Review {low_segment['segment']} segment (lowest conversion)")
        
        return recommendations


# Example usage
if __name__ == "__main__":
    tracker = PerformanceTracker()
    
    # Simulate some feedback
    test_feedback = [
        {"lead_id": "1", "conversion": True, "revenue": 5000, "response_rate": 0.3, "meeting_booked": True, "metadata": {"color": "RED", "industry": "SaaS"}},
        {"lead_id": "2", "conversion": False, "revenue": 0, "response_rate": 0.1, "meeting_booked": False, "metadata": {"color": "ORANGE", "industry": "Agency"}},
        {"lead_id": "3", "conversion": True, "revenue": 3000, "response_rate": 0.25, "meeting_booked": True, "metadata": {"color": "RED", "industry": "SaaS"}}
    ]
    
    metrics = tracker.track_performance(feedback_list=test_feedback)
    print(json.dumps(metrics, indent=2))
