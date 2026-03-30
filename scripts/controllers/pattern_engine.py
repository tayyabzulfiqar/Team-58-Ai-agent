"""
Pattern Engine
Advanced pattern detection and analysis system
"""
import statistics
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import numpy as np

class PatternEngine:
    def __init__(self):
        self.pattern_thresholds = {
            "min_sample_size": 5,
            "correlation_threshold": 0.3,
            "trend_significance": 0.1,
            "pattern_confidence": 0.7
        }
        
        self.pattern_types = [
            "correlation_patterns",
            "temporal_patterns", 
            "segmentation_patterns",
            "behavioral_patterns",
            "performance_patterns"
        ]
        
    def detect_all_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect all types of patterns in the data"""
        if len(data) < self.pattern_thresholds["min_sample_size"]:
            return {"status": "insufficient_data", "min_required": self.pattern_thresholds["min_sample_size"]}
        
        pattern_results = {
            "correlation_patterns": self._detect_correlation_patterns(data),
            "temporal_patterns": self._detect_temporal_patterns(data),
            "segmentation_patterns": self._detect_segmentation_patterns(data),
            "behavioral_patterns": self._detect_behavioral_patterns(data),
            "performance_patterns": self._detect_performance_patterns(data),
            "pattern_summary": {},
            "confidence_scores": {},
            "recommendations": [],
            "detection_timestamp": datetime.now().isoformat()
        }
        
        # Generate pattern summary
        pattern_results["pattern_summary"] = self._generate_pattern_summary(pattern_results)
        
        # Calculate confidence scores
        pattern_results["confidence_scores"] = self._calculate_pattern_confidence(pattern_results)
        
        # Generate recommendations
        pattern_results["recommendations"] = self._generate_pattern_recommendations(pattern_results)
        
        return pattern_results
    
    def _detect_correlation_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect correlation patterns between variables"""
        correlations = {}
        
        # Extract numeric fields
        numeric_fields = ["age", "income", "intelligence_score", "raw_score"]
        available_fields = [field for field in numeric_fields if all(field in record for record in data)]
        
        if len(available_fields) < 2:
            return {"status": "insufficient_numeric_fields"}
        
        # Calculate correlations
        for i, field1 in enumerate(available_fields):
            for field2 in available_fields[i+1:]:
                values1 = [record[field1] for record in data]
                values2 = [record[field2] for record in data]
                
                correlation = self._calculate_correlation(values1, values2)
                if abs(correlation) >= self.pattern_thresholds["correlation_threshold"]:
                    correlations[f"{field1}_vs_{field2}"] = {
                        "correlation": correlation,
                        "strength": self._classify_correlation_strength(correlation),
                        "significance": self._calculate_significance(correlation, len(data)),
                        "sample_size": len(data)
                    }
        
        return {
            "correlations": correlations,
            "strongest_correlation": self._find_strongest_correlation(correlations),
            "total_correlations": len(correlations)
        }
    
    def _detect_temporal_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect temporal patterns in the data"""
        if not all("timestamp" in record for record in data):
            return {"status": "no_timestamp_data"}
        
        # Sort by timestamp
        sorted_data = sorted(data, key=lambda x: datetime.fromisoformat(x["timestamp"]))
        
        temporal_patterns = {
            "trend_analysis": self._analyze_trends(sorted_data),
            "seasonal_patterns": self._detect_seasonal_patterns(sorted_data),
            "time_based_performance": self._analyze_time_based_performance(sorted_data),
            "data_velocity": self._calculate_data_velocity(sorted_data)
        }
        
        return temporal_patterns
    
    def _detect_segmentation_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect patterns within different segments"""
        segmentation_patterns = {}
        
        # Segment by different criteria
        segment_fields = ["source", "age_group", "income_category"]
        
        for field in segment_fields:
            if all(field in record for record in data):
                segments = defaultdict(list)
                for record in data:
                    segments[record[field]].append(record)
                
                segment_analysis = {}
                for segment_name, segment_data in segments.items():
                    if len(segment_data) >= 3:  # Minimum for pattern detection
                        segment_analysis[segment_name] = {
                            "size": len(segment_data),
                            "avg_income": statistics.mean([r["income"] for r in segment_data]),
                            "avg_age": statistics.mean([r["age"] for r in segment_data]),
                            "avg_score": statistics.mean([r.get("intelligence_score", r.get("raw_score", 0)) for r in segment_data]),
                            "variance": statistics.variance([r.get("intelligence_score", r.get("raw_score", 0)) for r in segment_data]) if len(segment_data) > 1 else 0
                        }
                
                segmentation_patterns[f"by_{field}"] = {
                    "segments": segment_analysis,
                    "total_segments": len(segment_analysis),
                    "largest_segment": max(segment_analysis.items(), key=lambda x: x[1]["size"]) if segment_analysis else None,
                    "highest_performing": max(segment_analysis.items(), key=lambda x: x[1]["avg_score"]) if segment_analysis else None
                }
        
        return segmentation_patterns
    
    def _detect_behavioral_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect behavioral patterns in the data"""
        behavioral_patterns = {
            "source_behavior": self._analyze_source_behavior(data),
            "quality_behavior": self._analyze_quality_behavior(data),
            "performance_clusters": self._detect_performance_clusters(data),
            "outlier_patterns": self._detect_outlier_patterns(data)
        }
        
        return behavioral_patterns
    
    def _detect_performance_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect performance-related patterns"""
        performance_patterns = {
            "high_performance_indicators": self._identify_high_performance_indicators(data),
            "performance_distributions": self._analyze_performance_distributions(data),
            "performance_trends": self._analyze_performance_trends(data),
            "bottleneck_patterns": self._identify_bottleneck_patterns(data)
        }
        
        return performance_patterns
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient"""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        try:
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(xi * yi for xi, yi in zip(x, y))
            sum_x2 = sum(xi * xi for xi in x)
            sum_y2 = sum(yi * yi for yi in y)
            
            numerator = n * sum_xy - sum_x * sum_y
            denominator = ((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2)) ** 0.5
            
            return numerator / denominator if denominator != 0 else 0.0
        except:
            return 0.0
    
    def _classify_correlation_strength(self, correlation: float) -> str:
        """Classify correlation strength"""
        abs_corr = abs(correlation)
        if abs_corr >= 0.8:
            return "very_strong"
        elif abs_corr >= 0.6:
            return "strong"
        elif abs_corr >= 0.4:
            return "moderate"
        elif abs_corr >= 0.2:
            return "weak"
        else:
            return "very_weak"
    
    def _calculate_significance(self, correlation: float, sample_size: int) -> float:
        """Calculate statistical significance of correlation"""
        if sample_size <= 2:
            return 0.0
        
        # Simple significance calculation
        t_stat = abs(correlation) * ((sample_size - 2) / (1 - correlation ** 2)) ** 0.5
        return min(1.0, t_stat / 10)  # Normalized significance
    
    def _find_strongest_correlation(self, correlations: Dict[str, Any]) -> Dict[str, Any]:
        """Find the strongest correlation"""
        if not correlations:
            return None
        
        strongest = max(correlations.items(), key=lambda x: abs(x[1]["correlation"]))
        return {
            "pair": strongest[0],
            "correlation": strongest[1]["correlation"],
            "strength": strongest[1]["strength"]
        }
    
    def _analyze_trends(self, sorted_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends over time"""
        if len(sorted_data) < 3:
            return {"status": "insufficient_data"}
        
        # Extract numeric fields for trend analysis
        numeric_fields = ["age", "income", "raw_score"]
        trends = {}
        
        for field in numeric_fields:
            if all(field in record for record in sorted_data):
                values = [record[field] for record in sorted_data]
                time_points = list(range(len(values)))
                
                # Simple linear trend
                correlation = self._calculate_correlation(time_points, values)
                trend_direction = "increasing" if correlation > 0.1 else "decreasing" if correlation < -0.1 else "stable"
                
                trends[field] = {
                    "direction": trend_direction,
                    "strength": abs(correlation),
                    "start_value": values[0],
                    "end_value": values[-1],
                    "change_percentage": ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0
                }
        
        return trends
    
    def _detect_seasonal_patterns(self, sorted_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect seasonal patterns (simplified for demo data)"""
        # For demo purposes, analyze by hour of day
        hourly_patterns = defaultdict(list)
        
        for record in sorted_data:
            try:
                timestamp = datetime.fromisoformat(record["timestamp"])
                hour = timestamp.hour
                hourly_patterns[hour].append(record.get("intelligence_score", record.get("raw_score", 0)))
            except:
                continue
        
        seasonal_analysis = {}
        for hour, scores in hourly_patterns.items():
            if len(scores) >= 2:
                seasonal_analysis[f"hour_{hour}"] = {
                    "avg_score": statistics.mean(scores),
                    "count": len(scores),
                    "variance": statistics.variance(scores) if len(scores) > 1 else 0
                }
        
        return {
            "hourly_patterns": seasonal_analysis,
            "best_hour": max(seasonal_analysis.items(), key=lambda x: x[1]["avg_score"]) if seasonal_analysis else None,
            "worst_hour": min(seasonal_analysis.items(), key=lambda x: x[1]["avg_score"]) if seasonal_analysis else None
        }
    
    def _analyze_time_based_performance(self, sorted_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance over time"""
        performance_over_time = []
        
        for i, record in enumerate(sorted_data):
            performance_over_time.append({
                "index": i,
                "timestamp": record["timestamp"],
                "score": record.get("intelligence_score", record.get("raw_score", 0)),
                "quality": record.get("processing_metadata", {}).get("quality_score", 1.0)
            })
        
        return {
            "performance_series": performance_over_time,
            "avg_performance": statistics.mean([p["score"] for p in performance_over_time]),
            "performance_variance": statistics.variance([p["score"] for p in performance_over_time]) if len(performance_over_time) > 1 else 0
        }
    
    def _calculate_data_velocity(self, sorted_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate data velocity (records per time unit)"""
        if len(sorted_data) < 2:
            return {"status": "insufficient_data"}
        
        start_time = datetime.fromisoformat(sorted_data[0]["timestamp"])
        end_time = datetime.fromisoformat(sorted_data[-1]["timestamp"])
        time_span = (end_time - start_time).total_seconds()
        
        if time_span == 0:
            return {"status": "no_time_span"}
        
        velocity = len(sorted_data) / time_span  # Records per second
        
        return {
            "records_per_second": velocity,
            "records_per_minute": velocity * 60,
            "total_time_span_seconds": time_span,
            "total_records": len(sorted_data)
        }
    
    def _analyze_source_behavior(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze behavior patterns by source"""
        source_behavior = defaultdict(list)
        
        for record in data:
            source_behavior[record["source"]].append({
                "score": record.get("intelligence_score", record.get("raw_score", 0)),
                "quality": record.get("processing_metadata", {}).get("quality_score", 1.0),
                "income": record["income"],
                "age": record["age"]
            })
        
        behavior_analysis = {}
        for source, records in source_behavior.items():
            scores = [r["score"] for r in records]
            qualities = [r["quality"] for r in records]
            incomes = [r["income"] for r in records]
            
            behavior_analysis[source] = {
                "record_count": len(records),
                "avg_score": statistics.mean(scores),
                "score_consistency": 1 - (statistics.stdev(scores) / statistics.mean(scores)) if len(scores) > 1 and statistics.mean(scores) > 0 else 1,
                "avg_quality": statistics.mean(qualities),
                "avg_income": statistics.mean(incomes),
                "reliability_score": self._calculate_reliability_score(records)
            }
        
        return behavior_analysis
    
    def _analyze_quality_behavior(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze quality-related behavior patterns"""
        quality_scores = [record.get("processing_metadata", {}).get("quality_score", 1.0) for record in data]
        
        if not quality_scores:
            return {"status": "no_quality_data"}
        
        return {
            "avg_quality": statistics.mean(quality_scores),
            "quality_variance": statistics.variance(quality_scores) if len(quality_scores) > 1 else 0,
            "quality_trend": self._calculate_quality_trend(data),
            "high_quality_percentage": sum(1 for q in quality_scores if q > 0.8) / len(quality_scores),
            "low_quality_percentage": sum(1 for q in quality_scores if q < 0.5) / len(quality_scores)
        }
    
    def _detect_performance_clusters(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect performance clusters using simple clustering"""
        scores = [record.get("intelligence_score", record.get("raw_score", 0)) for record in data]
        
        if len(scores) < 3:
            return {"status": "insufficient_data"}
        
        # Simple k-means clustering (k=3 for demo)
        k = 3
        sorted_scores = sorted(scores)
        n = len(sorted_scores)
        
        # Create clusters
        cluster_size = n // k
        clusters = {
            "low_performance": sorted_scores[:cluster_size],
            "medium_performance": sorted_scores[cluster_size:2*cluster_size],
            "high_performance": sorted_scores[2*cluster_size:]
        }
        
        cluster_analysis = {}
        for cluster_name, cluster_scores in clusters.items():
            if cluster_scores:
                cluster_analysis[cluster_name] = {
                    "size": len(cluster_scores),
                    "min_score": min(cluster_scores),
                    "max_score": max(cluster_scores),
                    "avg_score": statistics.mean(cluster_scores),
                    "score_range": max(cluster_scores) - min(cluster_scores)
                }
        
        return {
            "clusters": cluster_analysis,
            "cluster_separation": self._calculate_cluster_separation(cluster_analysis)
        }
    
    def _detect_outlier_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect outlier patterns"""
        scores = [record.get("intelligence_score", record.get("raw_score", 0)) for record in data]
        
        if len(scores) < 4:
            return {"status": "insufficient_data"}
        
        # Calculate outliers using IQR method
        q1 = np.percentile(scores, 25)
        q3 = np.percentile(scores, 75)
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = [score for score in scores if score < lower_bound or score > upper_bound]
        
        return {
            "outlier_count": len(outliers),
            "outlier_percentage": len(outliers) / len(scores),
            "outlier_values": outliers,
            "bounds": {
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "iqr": iqr
            },
            "data_cleanliness": "clean" if len(outliers) / len(scores) < 0.1 else "moderate" if len(outliers) / len(scores) < 0.2 else "noisy"
        }
    
    def _identify_high_performance_indicators(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify indicators of high performance"""
        high_performers = [record for record in data if record.get("intelligence_score", record.get("raw_score", 0)) > 80]
        
        if not high_performers:
            return {"status": "no_high_performers"}
        
        indicators = {
            "common_sources": Counter(record["source"] for record in high_performers).most_common(3),
            "avg_age": statistics.mean([record["age"] for record in high_performers]),
            "avg_income": statistics.mean([record["income"] for record in high_performers]),
            "common_age_groups": Counter(record.get("age_group", "unknown") for record in high_performers).most_common(3),
            "common_income_categories": Counter(record.get("income_category", "unknown") for record in high_performers).most_common(3)
        }
        
        return indicators
    
    def _analyze_performance_distributions(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance distributions"""
        scores = [record.get("intelligence_score", record.get("raw_score", 0)) for record in data]
        
        return {
            "distribution_stats": {
                "mean": statistics.mean(scores),
                "median": statistics.median(scores),
                "std_dev": statistics.stdev(scores) if len(scores) > 1 else 0,
                "min": min(scores),
                "max": max(scores),
                "skewness": self._calculate_skewness(scores),
                "kurtosis": self._calculate_kurtosis(scores)
            },
            "percentiles": {
                "25th": np.percentile(scores, 25),
                "50th": np.percentile(scores, 50),
                "75th": np.percentile(scores, 75),
                "90th": np.percentile(scores, 90),
                "95th": np.percentile(scores, 95)
            }
        }
    
    def _analyze_performance_trends(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance trends"""
        if "timestamp" not in data[0]:
            return {"status": "no_timestamp_data"}
        
        sorted_data = sorted(data, key=lambda x: datetime.fromisoformat(x["timestamp"]))
        scores = [record.get("intelligence_score", record.get("raw_score", 0)) for record in sorted_data]
        
        # Calculate trend
        time_points = list(range(len(scores)))
        trend_correlation = self._calculate_correlation(time_points, scores)
        
        return {
            "trend_direction": "improving" if trend_correlation > 0.1 else "declining" if trend_correlation < -0.1 else "stable",
            "trend_strength": abs(trend_correlation),
            "recent_performance": statistics.mean(scores[-3:]) if len(scores) >= 3 else statistics.mean(scores),
            "early_performance": statistics.mean(scores[:3]) if len(scores) >= 3 else statistics.mean(scores)
        }
    
    def _identify_bottleneck_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify bottleneck patterns"""
        bottlenecks = []
        
        # Check for quality bottlenecks
        low_quality_records = [record for record in data if record.get("processing_metadata", {}).get("quality_score", 1.0) < 0.5]
        if len(low_quality_records) / len(data) > 0.2:
            bottlenecks.append({
                "type": "quality_bottleneck",
                "severity": "high" if len(low_quality_records) / len(data) > 0.3 else "medium",
                "affected_percentage": len(low_quality_records) / len(data)
            })
        
        # Check for source bottlenecks
        source_counts = Counter(record["source"] for record in data)
        dominant_source = source_counts.most_common(1)[0]
        if dominant_source[1] / len(data) > 0.7:
            bottlenecks.append({
                "type": "source_concentration",
                "severity": "high",
                "source": dominant_source[0],
                "concentration_percentage": dominant_source[1] / len(data)
            })
        
        return {
            "bottlenecks": bottlenecks,
            "total_bottlenecks": len(bottlenecks),
            "system_health": "healthy" if len(bottlenecks) == 0 else "warning" if len(bottlenecks) == 1 else "critical"
        }
    
    def _calculate_reliability_score(self, records: List[Dict[str, Any]]) -> float:
        """Calculate reliability score for a source"""
        if not records:
            return 0.0
        
        # Factors: consistency, quality, performance
        scores = [r["score"] for r in records]
        qualities = [r["quality"] for r in records]
        
        consistency_score = 1 - (statistics.stdev(scores) / statistics.mean(scores)) if len(scores) > 1 and statistics.mean(scores) > 0 else 1
        quality_score = statistics.mean(qualities)
        
        return (consistency_score * 0.5 + quality_score * 0.5)
    
    def _calculate_quality_trend(self, data: List[Dict[str, Any]]) -> str:
        """Calculate quality trend over time"""
        if "timestamp" not in data[0]:
            return "unknown"
        
        sorted_data = sorted(data, key=lambda x: datetime.fromisoformat(x["timestamp"]))
        qualities = [record.get("processing_metadata", {}).get("quality_score", 1.0) for record in sorted_data]
        
        if len(qualities) < 3:
            return "insufficient_data"
        
        time_points = list(range(len(qualities)))
        trend = self._calculate_correlation(time_points, qualities)
        
        return "improving" if trend > 0.05 else "declining" if trend < -0.05 else "stable"
    
    def _calculate_cluster_separation(self, cluster_analysis: Dict[str, Any]) -> float:
        """Calculate separation between clusters"""
        if len(cluster_analysis) < 2:
            return 0.0
        
        cluster_means = [data["avg_score"] for data in cluster_analysis.values()]
        return max(cluster_means) - min(cluster_means)
    
    def _calculate_skewness(self, data: List[float]) -> float:
        """Calculate skewness of data"""
        if len(data) < 3:
            return 0.0
        
        mean = statistics.mean(data)
        std_dev = statistics.stdev(data)
        
        if std_dev == 0:
            return 0.0
        
        skewness = sum((x - mean) ** 3 for x in data) / (len(data) * std_dev ** 3)
        return skewness
    
    def _calculate_kurtosis(self, data: List[float]) -> float:
        """Calculate kurtosis of data"""
        if len(data) < 4:
            return 0.0
        
        mean = statistics.mean(data)
        std_dev = statistics.stdev(data)
        
        if std_dev == 0:
            return 0.0
        
        kurtosis = sum((x - mean) ** 4 for x in data) / (len(data) * std_dev ** 4) - 3
        return kurtosis
    
    def _generate_pattern_summary(self, pattern_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of all detected patterns"""
        summary = {
            "total_pattern_types": len([p for p in pattern_results.values() if isinstance(p, dict) and "status" not in p]),
            "significant_patterns": 0,
            "pattern_confidence": 0.0,
            "key_insights": []
        }
        
        # Count significant patterns
        for pattern_type, patterns in pattern_results.items():
            if isinstance(patterns, dict) and "status" not in patterns:
                if pattern_type == "correlation_patterns":
                    summary["significant_patterns"] += len(patterns.get("correlations", {}))
                elif pattern_type == "segmentation_patterns":
                    summary["significant_patterns"] += len(patterns)
                elif pattern_type == "behavioral_patterns":
                    summary["significant_patterns"] += len([p for p in patterns.values() if isinstance(p, dict)])
        
        return summary
    
    def _calculate_pattern_confidence(self, pattern_results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate confidence scores for each pattern type"""
        confidence_scores = {}
        
        for pattern_type, patterns in pattern_results.items():
            if isinstance(patterns, dict) and "status" not in patterns:
                # Simple confidence calculation based on data quality and pattern strength
                if pattern_type == "correlation_patterns":
                    correlations = patterns.get("correlations", {})
                    if correlations:
                        avg_strength = sum(abs(c["correlation"]) for c in correlations.values()) / len(correlations)
                        confidence_scores[pattern_type] = min(1.0, avg_strength * 2)
                    else:
                        confidence_scores[pattern_type] = 0.0
                else:
                    confidence_scores[pattern_type] = 0.7  # Default confidence
        
        return confidence_scores
    
    def _generate_pattern_recommendations(self, pattern_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on detected patterns"""
        recommendations = []
        
        # Correlation-based recommendations
        correlations = pattern_results.get("correlation_patterns", {}).get("correlations", {})
        strong_correlations = [k for k, v in correlations.items() if abs(v["correlation"]) > 0.7]
        
        if strong_correlations:
            recommendations.append(f"Strong correlations detected: {', '.join(strong_correlations)}. Consider leveraging these relationships in decision making.")
        
        # Performance-based recommendations
        performance_patterns = pattern_results.get("performance_patterns", {})
        bottlenecks = performance_patterns.get("bottleneck_patterns", {}).get("bottlenecks", [])
        
        if bottlenecks:
            recommendations.append(f"System bottlenecks identified: {len(bottlenecks)}. Address these to improve overall performance.")
        
        # Source-based recommendations
        behavioral_patterns = pattern_results.get("behavioral_patterns", {})
        source_behavior = behavioral_patterns.get("source_behavior", {})
        
        if source_behavior:
            best_source = max(source_behavior.items(), key=lambda x: x[1]["reliability_score"])
            recommendations.append(f"Highest reliability source: {best_source[0]} (score: {best_source[1]['reliability_score']:.2f}). Consider increasing reliance on this source.")
        
        return recommendations
