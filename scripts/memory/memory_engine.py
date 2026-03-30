"""
Memory Engine
Responsible for storing, retrieving, and managing system memory and learning
"""
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque

class MemoryEngine:
    def __init__(self, memory_path: str = "memory"):
        self.memory_path = memory_path
        self.memory_store = {}
        self.pattern_memory = deque(maxlen=1000)  # Rolling pattern memory
        self.decision_memory = deque(maxlen=500)   # Rolling decision memory
        self.performance_memory = deque(maxlen=200) # Rolling performance memory
        
        # Memory retention policies
        self.retention_days = 30
        self.min_confidence_threshold = 0.5
        
        # Initialize memory directories
        self._initialize_memory_structure()
        
    def _initialize_memory_structure(self):
        """Initialize memory directory structure"""
        memory_types = ["patterns", "decisions", "performance", "learning", "feedback"]
        
        for memory_type in memory_types:
            path = os.path.join(self.memory_path, memory_type)
            os.makedirs(path, exist_ok=True)
    
    def store_patterns(self, patterns: Dict[str, Any]) -> str:
        """Store patterns in memory with metadata"""
        memory_entry = {
            "id": self._generate_memory_id("pattern"),
            "type": "pattern",
            "data": patterns,
            "timestamp": datetime.now().isoformat(),
            "confidence": self._calculate_pattern_confidence(patterns),
            "access_count": 0,
            "last_accessed": datetime.now().isoformat()
        }
        
        # Store in rolling memory
        self.pattern_memory.append(memory_entry)
        
        # Persist to disk
        self._persist_memory(memory_entry, "patterns")
        
        return memory_entry["id"]
    
    def store_decisions(self, decisions: Dict[str, Any]) -> str:
        """Store decisions in memory with metadata"""
        memory_entry = {
            "id": self._generate_memory_id("decision"),
            "type": "decision",
            "data": decisions,
            "timestamp": datetime.now().isoformat(),
            "confidence": self._calculate_decision_confidence(decisions),
            "access_count": 0,
            "last_accessed": datetime.now().isoformat(),
            "outcomes": {}  # To be updated with actual outcomes
        }
        
        # Store in rolling memory
        self.decision_memory.append(memory_entry)
        
        # Persist to disk
        self._persist_memory(memory_entry, "decisions")
        
        return memory_entry["id"]
    
    def store_performance(self, performance_data: Dict[str, Any]) -> str:
        """Store performance metrics in memory"""
        memory_entry = {
            "id": self._generate_memory_id("performance"),
            "type": "performance",
            "data": performance_data,
            "timestamp": datetime.now().isoformat(),
            "confidence": 1.0,  # Performance data is factual
            "access_count": 0,
            "last_accessed": datetime.now().isoformat()
        }
        
        # Store in rolling memory
        self.performance_memory.append(memory_entry)
        
        # Persist to disk
        self._persist_memory(memory_entry, "performance")
        
        return memory_entry["id"]
    
    def retrieve_similar_patterns(self, current_patterns: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve similar patterns from memory"""
        similar_patterns = []
        
        for pattern_entry in self.pattern_memory:
            if pattern_entry["confidence"] >= self.min_confidence_threshold:
                similarity = self._calculate_pattern_similarity(current_patterns, pattern_entry["data"])
                if similarity > 0.5:  # Similarity threshold
                    similar_patterns.append({
                        "memory_entry": pattern_entry,
                        "similarity_score": similarity
                    })
        
        # Sort by similarity and return top results
        similar_patterns.sort(key=lambda x: x["similarity_score"], reverse=True)
        return similar_patterns[:limit]
    
    def retrieve_decision_history(self, decision_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve decision history from memory"""
        decisions = list(self.decision_memory)
        
        if decision_type:
            decisions = [d for d in decisions if d["data"].get("decision_type") == decision_type]
        
        # Sort by timestamp (most recent first)
        decisions.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return decisions[:limit]
    
    def retrieve_performance_trends(self, days: int = 7) -> Dict[str, Any]:
        """Retrieve performance trends over specified period"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_performance = [
            entry for entry in self.performance_memory
            if datetime.fromisoformat(entry["timestamp"]) >= cutoff_date
        ]
        
        if not recent_performance:
            return {"trend": "insufficient_data"}
        
        # Calculate trends
        trends = {
            "period_days": days,
            "data_points": len(recent_performance),
            "trend_analysis": self._analyze_performance_trends(recent_performance),
            "recommendations": self._generate_performance_recommendations(recent_performance)
        }
        
        return trends
    
    def update_decision_outcome(self, decision_id: str, outcome: Dict[str, Any]) -> bool:
        """Update decision with actual outcome for learning"""
        # Find decision in memory
        for decision_entry in self.decision_memory:
            if decision_entry["id"] == decision_id:
                decision_entry["outcomes"] = outcome
                decision_entry["last_updated"] = datetime.now().isoformat()
                
                # Update persistence
                self._persist_memory(decision_entry, "decisions")
                
                # Trigger learning update
                self._update_learning_from_outcome(decision_entry, outcome)
                
                return True
        
        return False
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Generate learning insights from memory"""
        insights = {
            "pattern_evolution": self._analyze_pattern_evolution(),
            "decision_accuracy": self._analyze_decision_accuracy(),
            "performance_improvements": self._analyze_performance_improvements(),
            "strategic_learnings": self._extract_strategic_learnings(),
            "recommendations": self._generate_learning_recommendations()
        }
        
        return insights
    
    def cleanup_old_memory(self) -> Dict[str, int]:
        """Clean up old memory entries based on retention policy"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        cleanup_stats = {
            "patterns_removed": 0,
            "decisions_removed": 0,
            "performance_removed": 0,
            "total_removed": 0
        }
        
        # Clean pattern memory
        original_size = len(self.pattern_memory)
        self.pattern_memory = deque(
            [entry for entry in self.pattern_memory 
             if datetime.fromisoformat(entry["timestamp"]) >= cutoff_date],
            maxlen=1000
        )
        cleanup_stats["patterns_removed"] = original_size - len(self.pattern_memory)
        
        # Clean decision memory
        original_size = len(self.decision_memory)
        self.decision_memory = deque(
            [entry for entry in self.decision_memory 
             if datetime.fromisoformat(entry["timestamp"]) >= cutoff_date],
            maxlen=500
        )
        cleanup_stats["decisions_removed"] = original_size - len(self.decision_memory)
        
        # Clean performance memory
        original_size = len(self.performance_memory)
        self.performance_memory = deque(
            [entry for entry in self.performance_memory 
             if datetime.fromisoformat(entry["timestamp"]) >= cutoff_date],
            maxlen=200
        )
        cleanup_stats["performance_removed"] = original_size - len(self.performance_memory)
        
        cleanup_stats["total_removed"] = sum([
            cleanup_stats["patterns_removed"],
            cleanup_stats["decisions_removed"],
            cleanup_stats["performance_removed"]
        ])
        
        return cleanup_stats
    
    def _generate_memory_id(self, memory_type: str) -> str:
        """Generate unique memory ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{memory_type}_{timestamp}_{hash(datetime.now()) % 10000}"
    
    def _calculate_pattern_confidence(self, patterns: Dict[str, Any]) -> float:
        """Calculate confidence score for patterns"""
        confidence = 0.0
        
        # Check pattern completeness
        if patterns.get("age_income_correlation"):
            confidence += 0.3
        
        if patterns.get("source_performance"):
            confidence += 0.3
        
        if patterns.get("age_group_performance"):
            confidence += 0.2
        
        # Check data quality indicators
        if len(patterns) >= 3:
            confidence += 0.2
        
        return min(1.0, confidence)
    
    def _calculate_decision_confidence(self, decisions: Dict[str, Any]) -> float:
        """Calculate confidence score for decisions"""
        confidence = 0.0
        
        # Check decision completeness
        if decisions.get("individual_decisions"):
            confidence += 0.4
        
        if decisions.get("portfolio_decisions"):
            confidence += 0.3
        
        if decisions.get("strategic_decisions"):
            confidence += 0.3
        
        return min(1.0, confidence)
    
    def _calculate_pattern_similarity(self, patterns1: Dict[str, Any], patterns2: Dict[str, Any]) -> float:
        """Calculate similarity between two pattern sets"""
        similarity_score = 0.0
        total_comparisons = 0
        
        # Compare correlation patterns
        corr1 = patterns1.get("age_income_correlation", 0)
        corr2 = patterns2.get("age_income_correlation", 0)
        if corr1 and corr2:
            similarity = 1.0 - abs(corr1 - corr2) / max(abs(corr1), abs(corr2), 1.0)
            similarity_score += similarity
            total_comparisons += 1
        
        # Compare source performance
        source_perf1 = patterns1.get("source_performance", {})
        source_perf2 = patterns2.get("source_performance", {})
        
        common_sources = set(source_perf1.keys()) & set(source_perf2.keys())
        if common_sources:
            source_similarity = 0
            for source in common_sources:
                score1 = source_perf1[source].get("avg_score", 0)
                score2 = source_perf2[source].get("avg_score", 0)
                if score1 and score2:
                    source_sim = 1.0 - abs(score1 - score2) / max(score1, score2, 1.0)
                    source_similarity += source_sim
            
            if common_sources:
                similarity_score += source_similarity / len(common_sources)
                total_comparisons += 1
        
        return similarity_score / total_comparisons if total_comparisons > 0 else 0.0
    
    def _persist_memory(self, memory_entry: Dict[str, Any], memory_type: str):
        """Persist memory entry to disk"""
        filename = f"{memory_entry['id']}.json"
        filepath = os.path.join(self.memory_path, memory_type, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(memory_entry, f, indent=2)
        except Exception as e:
            print(f"Error persisting memory entry: {e}")
    
    def _analyze_pattern_evolution(self) -> Dict[str, Any]:
        """Analyze how patterns have evolved over time"""
        if len(self.pattern_memory) < 2:
            return {"status": "insufficient_data"}
        
        # Compare recent patterns with older patterns
        recent_patterns = list(self.pattern_memory)[-5:]  # Last 5 patterns
        older_patterns = list(self.pattern_memory)[:5]   # First 5 patterns
        
        recent_correlations = [p["data"].get("age_income_correlation", 0) for p in recent_patterns if p["data"].get("age_income_correlation")]
        older_correlations = [p["data"].get("age_income_correlation", 0) for p in older_patterns if p["data"].get("age_income_correlation")]
        
        evolution = {
            "correlation_trend": "stable",
            "pattern_stability": "high",
            "confidence_evolution": "improving"
        }
        
        if recent_correlations and older_correlations:
            recent_avg = sum(recent_correlations) / len(recent_correlations)
            older_avg = sum(older_correlations) / len(older_correlations)
            
            if recent_avg > older_avg * 1.1:
                evolution["correlation_trend"] = "improving"
            elif recent_avg < older_avg * 0.9:
                evolution["correlation_trend"] = "declining"
        
        return evolution
    
    def _analyze_decision_accuracy(self) -> Dict[str, Any]:
        """Analyze decision accuracy based on outcomes"""
        decisions_with_outcomes = [
            entry for entry in self.decision_memory
            if entry.get("outcomes")
        ]
        
        if not decisions_with_outcomes:
            return {"status": "no_outcome_data"}
        
        # Calculate accuracy metrics
        correct_decisions = 0
        total_decisions = len(decisions_with_outcomes)
        
        for decision in decisions_with_outcomes:
            outcome = decision["outcomes"]
            if outcome.get("successful", False):
                correct_decisions += 1
        
        accuracy = correct_decisions / total_decisions if total_decisions > 0 else 0
        
        return {
            "accuracy_rate": accuracy,
            "total_evaluated": total_decisions,
            "correct_decisions": correct_decisions,
            "accuracy_trend": "improving" if accuracy > 0.7 else "needs_improvement"
        }
    
    def _analyze_performance_improvements(self) -> Dict[str, Any]:
        """Analyze performance improvements over time"""
        if len(self.performance_memory) < 2:
            return {"status": "insufficient_data"}
        
        # Compare recent performance with older performance
        recent_performance = list(self.performance_memory)[-3:]
        older_performance = list(self.performance_memory)[:3]
        
        # Calculate average performance metrics
        recent_avg = self._calculate_average_performance(recent_performance)
        older_avg = self._calculate_average_performance(older_performance)
        
        improvement = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
        
        return {
            "improvement_percentage": improvement * 100,
            "trend": "improving" if improvement > 0.05 else "stable" if improvement > -0.05 else "declining",
            "recent_average": recent_avg,
            "older_average": older_avg
        }
    
    def _calculate_average_performance(self, performance_entries: List[Dict[str, Any]]) -> float:
        """Calculate average performance score"""
        if not performance_entries:
            return 0.0
        
        total_score = 0
        for entry in performance_entries:
            data = entry["data"]
            # Simple performance score calculation
            score = 0
            if data.get("total_processed"):
                score += 0.3
            if data.get("avg_quality_score", 0) > 0.7:
                score += 0.4
            if data.get("processing_time_seconds", 0) < 60:
                score += 0.3
            
            total_score += score
        
        return total_score / len(performance_entries)
    
    def _extract_strategic_learnings(self) -> List[str]:
        """Extract strategic learnings from memory"""
        learnings = []
        
        # Analyze pattern memory for strategic insights
        if self.pattern_memory:
            recent_patterns = list(self.pattern_memory)[-5:]
            high_confidence_patterns = [p for p in recent_patterns if p["confidence"] > 0.8]
            
            if high_confidence_patterns:
                learnings.append("Consistent high-confidence patterns detected - strategy is stable")
            
            # Check source performance patterns
            source_performance = {}
            for pattern in high_confidence_patterns:
                source_perf = pattern["data"].get("source_performance", {})
                for source, metrics in source_perf.items():
                    if source not in source_performance:
                        source_performance[source] = []
                    source_performance[source].append(metrics.get("avg_score", 0))
            
            # Find best performing source
            best_source = None
            best_score = 0
            for source, scores in source_performance.items():
                avg_score = sum(scores) / len(scores) if scores else 0
                if avg_score > best_score:
                    best_score = avg_score
                    best_source = source
            
            if best_source:
                learnings.append(f"{best_source} consistently shows best performance")
        
        # Analyze decision outcomes
        decisions_with_outcomes = [
            entry for entry in self.decision_memory
            if entry.get("outcomes") and entry["outcomes"].get("successful")
        ]
        
        if decisions_with_outcomes:
            successful_decisions = decisions_with_outcomes[-5:]  # Recent successful decisions
            decision_types = [d["data"].get("decision_type") for d in successful_decisions]
            
            if decision_types:
                most_successful = max(set(decision_types), key=decision_types.count)
                learnings.append(f"{most_successful} decisions show highest success rate")
        
        return learnings
    
    def _generate_learning_recommendations(self) -> List[str]:
        """Generate recommendations based on learning insights"""
        recommendations = []
        
        # Pattern-based recommendations
        if len(self.pattern_memory) > 10:
            recommendations.append("Consider implementing automated pattern recognition")
        
        # Decision-based recommendations
        decisions_with_outcomes = [
            entry for entry in self.decision_memory
            if entry.get("outcomes")
        ]
        
        if len(decisions_with_outcomes) > 5:
            accuracy = self._analyze_decision_accuracy().get("accuracy_rate", 0)
            if accuracy < 0.7:
                recommendations.append("Review and improve decision criteria")
            else:
                recommendations.append("Current decision logic is performing well")
        
        # Performance-based recommendations
        if len(self.performance_memory) > 5:
            improvement_analysis = self._analyze_performance_improvements()
            if improvement_analysis.get("trend") == "declining":
                recommendations.append("Investigate performance degradation causes")
            elif improvement_analysis.get("trend") == "improving":
                recommendations.append("Continue current optimization strategies")
        
        return recommendations
    
    def _analyze_performance_trends(self, performance_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance trends"""
        if len(performance_data) < 2:
            return {"status": "insufficient_data"}
        
        # Extract key metrics over time
        processing_times = []
        quality_scores = []
        
        for entry in performance_data:
            data = entry["data"]
            if data.get("processing_time_seconds"):
                processing_times.append(data["processing_time_seconds"])
            if data.get("avg_quality_score"):
                quality_scores.append(data["avg_quality_score"])
        
        trends = {}
        
        if processing_times:
            trends["processing_time"] = {
                "trend": "improving" if processing_times[-1] < processing_times[0] else "declining",
                "current": processing_times[-1],
                "previous": processing_times[0]
            }
        
        if quality_scores:
            trends["quality_score"] = {
                "trend": "improving" if quality_scores[-1] > quality_scores[0] else "declining",
                "current": quality_scores[-1],
                "previous": quality_scores[0]
            }
        
        return trends
    
    def _generate_performance_recommendations(self, performance_data: List[Dict[str, Any]]) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        if not performance_data:
            return recommendations
        
        # Analyze recent performance
        latest_performance = performance_data[-1]["data"]
        
        if latest_performance.get("processing_time_seconds", 0) > 30:
            recommendations.append("Consider optimizing processing speed")
        
        if latest_performance.get("avg_quality_score", 0) < 0.8:
            recommendations.append("Focus on improving data quality")
        
        if latest_performance.get("total_processed", 0) < 10:
            recommendations.append("Increase processing volume for better insights")
        
        return recommendations
    
    def _update_learning_from_outcome(self, decision_entry: Dict[str, Any], outcome: Dict[str, Any]):
        """Update learning system based on decision outcome"""
        # Store learning feedback
        learning_entry = {
            "decision_id": decision_entry["id"],
            "decision_data": decision_entry["data"],
            "outcome": outcome,
            "learning_timestamp": datetime.now().isoformat(),
            "success": outcome.get("successful", False)
        }
        
        # Persist learning data
        self._persist_memory(learning_entry, "learning")
        
        # Update pattern memory if successful
        if outcome.get("successful", False):
            self._reinforce_successful_patterns(decision_entry["data"])
    
    def _reinforce_successful_patterns(self, decision_data: Dict[str, Any]):
        """Reinforce patterns that led to successful decisions"""
        # Extract successful patterns from decision data
        successful_patterns = {
            "success_factors": [],
            "context": decision_data.get("context", {}),
            "timestamp": datetime.now().isoformat()
        }
        
        # Store reinforced patterns
        memory_entry = {
            "id": self._generate_memory_id("reinforcement"),
            "type": "reinforcement",
            "data": successful_patterns,
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.9
        }
        
        self._persist_memory(memory_entry, "learning")
