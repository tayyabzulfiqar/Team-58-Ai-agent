"""
Data Processing Agent
Responsible for cleaning, structuring, and normalizing data
"""
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

class ProcessingAgent:
    def __init__(self):
        self.processing_rules = {
            "name_cleaning": True,
            "age_validation": True,
            "income_normalization": True,
            "duplicate_detection": True
        }
        
    def process_raw_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process raw data through all cleaning and structuring steps"""
        processed_data = []
        
        for record in raw_data:
            processed_record = self._process_single_record(record)
            if processed_record:  # Only keep valid records
                processed_data.append(processed_record)
                
        # Remove duplicates
        processed_data = self._remove_duplicates(processed_data)
        
        # Add processing metadata
        for record in processed_data:
            record["processing_metadata"] = {
                "processed_at": datetime.now().isoformat(),
                "processing_version": "1.0",
                "quality_score": self._calculate_quality_score(record)
            }
            
        return processed_data
    
    def _process_single_record(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual record"""
        try:
            processed = record.copy()
            
            # Clean and validate name
            if self.processing_rules["name_cleaning"]:
                processed["name"] = self._clean_name(processed["name"])
                
            # Validate age
            if self.processing_rules["age_validation"]:
                if not self._validate_age(processed["age"]):
                    return None
                processed["age"] = int(processed["age"])
                
            # Normalize income
            if self.processing_rules["income_normalization"]:
                processed["income"] = self._normalize_income(processed["income"])
                
            # Add derived fields
            processed["age_group"] = self._categorize_age(processed["age"])
            processed["income_category"] = self._categorize_income(processed["income"])
            
            return processed
            
        except Exception as e:
            print(f"Error processing record {record.get('id', 'unknown')}: {e}")
            return None
    
    def _clean_name(self, name: str) -> str:
        """Clean and standardize name field"""
        if not isinstance(name, str):
            name = str(name)
            
        # Remove extra whitespace and special characters
        name = re.sub(r'\s+', ' ', name.strip())
        name = re.sub(r'[^\w\s]', '', name)
        
        # Capitalize properly
        return ' '.join(word.capitalize() for word in name.split())
    
    def _validate_age(self, age: Any) -> bool:
        """Validate age field"""
        try:
            age_int = int(age)
            return 18 <= age_int <= 100
        except (ValueError, TypeError):
            return False
    
    def _normalize_income(self, income: Any) -> float:
        """Normalize income to standard format"""
        try:
            income_float = float(income)
            # Ensure positive income
            return max(0, income_float)
        except (ValueError, TypeError):
            return 0.0
    
    def _categorize_age(self, age: int) -> str:
        """Categorize age into groups"""
        if age < 25:
            return "young"
        elif age < 35:
            return "young_adult"
        elif age < 50:
            return "adult"
        elif age < 65:
            return "mature"
        else:
            return "senior"
    
    def _categorize_income(self, income: float) -> str:
        """Categorize income into levels"""
        if income < 2000:
            return "low"
        elif income < 4000:
            return "medium"
        elif income < 7000:
            return "high"
        else:
            return "very_high"
    
    def _remove_duplicates(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate records based on name and age"""
        seen = set()
        unique_data = []
        
        for record in data:
            # Create unique key based on name and age
            key = (record["name"].lower(), record["age"])
            if key not in seen:
                seen.add(key)
                unique_data.append(record)
                
        return unique_data
    
    def _calculate_quality_score(self, record: Dict[str, Any]) -> float:
        """Calculate quality score for processed record"""
        score = 0.0
        
        # Name quality (30%)
        if record["name"] and len(record["name"]) > 2:
            score += 0.3
            
        # Age quality (25%)
        if 18 <= record["age"] <= 100:
            score += 0.25
            
        # Income quality (25%)
        if record["income"] > 0:
            score += 0.25
            
        # Source quality (20%)
        source_scores = {
            "internal_db": 0.2,
            "external_api": 0.15,
            "file_import": 0.18,
            "manual_entry": 0.1
        }
        score += source_scores.get(record["source"], 0.1)
        
        return min(1.0, score)
    
    def get_processing_summary(self, processed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of processing results"""
        if not processed_data:
            return {"total_processed": 0}
            
        return {
            "total_processed": len(processed_data),
            "avg_quality_score": sum(r["processing_metadata"]["quality_score"] for r in processed_data) / len(processed_data),
            "age_distribution": {age_group: sum(1 for r in processed_data if r["age_group"] == age_group) for age_group in set(r["age_group"] for r in processed_data)},
            "income_distribution": {inc_cat: sum(1 for r in processed_data if r["income_category"] == inc_cat) for inc_cat in set(r["income_category"] for r in processed_data)},
            "sources": list(set(r["source"] for r in processed_data)),
            "processing_timestamp": datetime.now().isoformat()
        }
