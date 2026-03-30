"""
Intelligence Agent
Responsible for analyzing patterns, scoring, and extracting insights
"""
import statistics
from typing import List, Dict, Any, Tuple
from datetime import datetime
from collections import defaultdict, Counter

class IntelligenceAgent:
    def __init__(self):
        self.scoring_weights = {
            "age_weight": 0.3,
            "income_weight": 0.4,
            "source_weight": 0.2,
            "quality_weight": 0.1
        }
        
        self.pattern_thresholds = {
            "min_sample_size": 3,
            "correlation_threshold": 0.5,
            "outlier_threshold": 2.0
        }
        
    def analyze_data(self, processed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Main analysis function - comprehensive data intelligence"""
        if not processed_data:
            return {"error": "No data to analyze"}
            
        analysis_results = {
            "scoring_analysis": self._score_all_records(processed_data),
            "pattern_analysis": self._detect_patterns(processed_data),
            "statistical_analysis": self._calculate_statistics(processed_data),
            "segmentation_analysis": self._segment_data(processed_data),
            "risk_analysis": self._assess_risks(processed_data),
            "opportunity_analysis": self._identify_opportunities(processed_data),
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        return analysis_results
    
    def _score_all_records(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Score all records using multiple criteria"""
        scored_records = []
        
        for record in data:
            score = self._calculate_intelligence_score(record)
            record["intelligence_score"] = score
            scored_records.append(record)
            
        # Score distribution analysis
        scores = [r["intelligence_score"] for r in scored_records]
        
        return {
            "scored_records": scored_records,
            "score_stats": {
                "mean": statistics.mean(scores),
                "median": statistics.median(scores),
                "min": min(scores),
                "max": max(scores),
                "std_dev": statistics.stdev(scores) if len(scores) > 1 else 0
            },
            "score_distribution": self._create_score_distribution(scores)
        }
    
    def _calculate_intelligence_score(self, record: Dict[str, Any]) -> float:
        """Calculate comprehensive intelligence score for single record"""
        score = 0.0
        
        # Age scoring (0-100)
        age_score = self._score_age(record["age"])
        score += age_score * self.scoring_weights["age_weight"]
        
        # Income scoring (0-100)
        income_score = self._score_income(record["income"])
        score += income_score * self.scoring_weights["income_weight"]
        
        # Source scoring (0-100)
        source_score = self._score_source(record["source"])
        score += source_score * self.scoring_weights["source_weight"]
        
        # Quality scoring (0-100)
        quality_score = record.get("processing_metadata", {}).get("quality_score", 0) * 100
        score += quality_score * self.scoring_weights["quality_weight"]
        
        return min(100.0, score)
    
    def _score_age(self, age: int) -> float:
        """Score age based on optimal ranges"""
        if 35 <= age <= 55:
            return 100.0  # Prime age range
        elif 25 <= age <= 65:
            return 80.0   # Good age range
        elif 18 <= age <= 70:
            return 60.0   # Acceptable age range
        else:
            return 20.0   # Poor age range
    
    def _score_income(self, income: float) -> float:
        """Score income based on levels"""
        if income >= 7000:
            return 100.0  # Very high income
        elif income >= 4000:
            return 85.0   # High income
        elif income >= 2000:
            return 70.0   # Medium income
        elif income >= 1000:
            return 50.0   # Low income
        else:
            return 20.0   # Very low income
    
    def _score_source(self, source: str) -> float:
        """Score data source reliability"""
        source_scores = {
            "internal_db": 95.0,
            "file_import": 85.0,
            "external_api": 75.0,
            "manual_entry": 60.0
        }
        return source_scores.get(source, 50.0)
    
    def _create_score_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Create score distribution buckets"""
        distribution = {
            "excellent (90-100)": 0,
            "good (70-89)": 0,
            "average (50-69)": 0,
            "poor (30-49)": 0,
            "very_poor (0-29)": 0
        }
        
        for score in scores:
            if score >= 90:
                distribution["excellent (90-100)"] += 1
            elif score >= 70:
                distribution["good (70-89)"] += 1
            elif score >= 50:
                distribution["average (50-69)"] += 1
            elif score >= 30:
                distribution["poor (30-49)"] += 1
            else:
                distribution["very_poor (0-29)"] += 1
                
        return distribution
    
    def _detect_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect meaningful patterns in the data"""
        patterns = {}
        
        # Age-Income correlation
        if len(data) >= self.pattern_thresholds["min_sample_size"]:
            age_income_corr = self._calculate_correlation(
                [r["age"] for r in data],
                [r["income"] for r in data]
            )
            patterns["age_income_correlation"] = age_income_corr
        
        # Source performance patterns
        source_performance = defaultdict(list)
        for record in data:
            source_performance[record["source"]].append(record["intelligence_score"])
        
        patterns["source_performance"] = {
            source: {
                "avg_score": statistics.mean(scores),
                "count": len(scores)
            }
            for source, scores in source_performance.items()
        }
        
        # Age group patterns
        age_group_performance = defaultdict(list)
        for record in data:
            age_group_performance[record["age_group"]].append(record["intelligence_score"])
        
        patterns["age_group_performance"] = {
            group: {
                "avg_score": statistics.mean(scores),
                "count": len(scores)
            }
            for group, scores in age_group_performance.items()
        }
        
        return patterns
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate correlation coefficient between two variables"""
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
    
    def _calculate_statistics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate comprehensive statistics"""
        ages = [r["age"] for r in data]
        incomes = [r["income"] for r in data]
        scores = [r["intelligence_score"] for r in data]
        
        return {
            "age_stats": self._calc_stat_dict(ages),
            "income_stats": self._calc_stat_dict(incomes),
            "score_stats": self._calc_stat_dict(scores),
            "demographic_breakdown": {
                "age_groups": Counter(r["age_group"] for r in data),
                "income_categories": Counter(r["income_category"] for r in data),
                "sources": Counter(r["source"] for r in data)
            }
        }
    
    def _calc_stat_dict(self, values: List[float]) -> Dict[str, float]:
        """Calculate statistical measures"""
        if not values:
            return {}
            
        return {
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "min": min(values),
            "max": max(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
            "count": len(values)
        }
    
    def _segment_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Segment data for targeted analysis"""
        segments = {
            "high_value": [r for r in data if r["intelligence_score"] >= 80],
            "medium_value": [r for r in data if 60 <= r["intelligence_score"] < 80],
            "low_value": [r for r in data if r["intelligence_score"] < 60]
        }
        
        # Analyze each segment
        segment_analysis = {}
        for segment_name, segment_data in segments.items():
            if segment_data:
                segment_analysis[segment_name] = {
                    "count": len(segment_data),
                    "avg_score": statistics.mean([r["intelligence_score"] for r in segment_data]),
                    "avg_income": statistics.mean([r["income"] for r in segment_data]),
                    "avg_age": statistics.mean([r["age"] for r in segment_data]),
                    "top_sources": Counter(r["source"] for r in segment_data).most_common(3)
                }
            else:
                segment_analysis[segment_name] = {"count": 0}
                
        return {
            "segments": segments,
            "segment_analysis": segment_analysis
        }
    
    def _assess_risks(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess potential risks in the data"""
        risks = {
            "data_quality_risks": [],
            "concentration_risks": [],
            "performance_risks": []
        }
        
        # Quality risks
        low_quality_count = sum(1 for r in data if r.get("processing_metadata", {}).get("quality_score", 0) < 0.5)
        if low_quality_count > len(data) * 0.2:
            risks["data_quality_risks"].append(f"High percentage of low-quality records: {low_quality_count}/{len(data)}")
        
        # Concentration risks
        source_counter = Counter(r["source"] for r in data)
        dominant_source = source_counter.most_common(1)[0]
        if dominant_source[1] > len(data) * 0.7:
            risks["concentration_risks"].append(f"Over-reliance on single source: {dominant_source[0]} ({dominant_source[1]} records)")
        
        # Performance risks
        low_score_count = sum(1 for r in data if r["intelligence_score"] < 50)
        if low_score_count > len(data) * 0.3:
            risks["performance_risks"].append(f"High percentage of low-scoring records: {low_score_count}/{len(data)}")
        
        return risks
    
    def _identify_opportunities(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify opportunities and recommendations"""
        opportunities = {
            "improvement_opportunities": [],
            "growth_opportunities": [],
            "optimization_opportunities": []
        }
        
        # High-value segment analysis
        high_value = [r for r in data if r["intelligence_score"] >= 80]
        if high_value:
            common_characteristics = self._find_common_characteristics(high_value)
            opportunities["growth_opportunities"].append(f"Target profiles with: {common_characteristics}")
        
        # Underperforming sources
        source_performance = defaultdict(list)
        for record in data:
            source_performance[record["source"]].append(record["intelligence_score"])
        
        for source, scores in source_performance.items():
            if statistics.mean(scores) < 60:
                opportunities["improvement_opportunities"].append(f"Improve data quality from {source} source")
        
        # Age group opportunities
        age_groups = Counter(r["age_group"] for r in data if r["intelligence_score"] >= 80)
        if age_groups:
            top_age_group = age_groups.most_common(1)[0]
            opportunities["optimization_opportunities"].append(f"Focus on {top_age_group[0]} age group ({top_age_group[1]} high-value records)")
        
        return opportunities
    
    def _find_common_characteristics(self, records: List[Dict[str, Any]]) -> str:
        """Find common characteristics among high-performing records"""
        if not records:
            return "None"
            
        characteristics = []
        
        # Most common age group
        age_groups = [r["age_group"] for r in records]
        most_common_age = Counter(age_groups).most_common(1)[0][0]
        characteristics.append(f"age_group: {most_common_age}")
        
        # Most common income category
        income_cats = [r["income_category"] for r in records]
        most_common_income = Counter(income_cats).most_common(1)[0][0]
        characteristics.append(f"income: {most_common_income}")
        
        # Most common source
        sources = [r["source"] for r in records]
        most_common_source = Counter(sources).most_common(1)[0][0]
        characteristics.append(f"source: {most_common_source}")
        
        return ", ".join(characteristics)
