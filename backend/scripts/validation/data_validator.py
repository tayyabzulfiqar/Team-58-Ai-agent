"""Data Validation Layer - Production Ready"""
import re
import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class DataValidator:
    """Production data validation with scoring"""
    
    REQUIRED_FIELDS = ['id', 'source']
    
    def validate(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a data record and return validation result"""
        errors = []
        score = 1.0
        
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in record or not record[field]:
                errors.append(f"Missing: {field}")
                score -= 0.3
        
        # Check for content
        content_fields = ['name', 'title', 'content', 'description', 'email']
        has_content = any(record.get(f) for f in content_fields)
        if not has_content:
            errors.append("No content")
            score -= 0.5
        
        # Validate email format
        if record.get('email'):
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, str(record['email'])):
                errors.append("Invalid email")
                score -= 0.2
        
        score = max(0.0, score)
        
        return {
            'valid': score > 0.5 and len(errors) == 0,
            'score': round(score, 2),
            'errors': errors
        }
    
    def clean(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize a record"""
        cleaned = record.copy()
        
        # Truncate long text
        for field in ['content', 'description', 'selftext']:
            if field in cleaned and cleaned[field]:
                cleaned[field] = str(cleaned[field])[:1000]
        
        # Normalize strings
        if cleaned.get('name'):
            cleaned['name'] = str(cleaned['name']).strip()[:100]
        
        # Add metadata
        cleaned['_processed_at'] = datetime.now().isoformat()
        cleaned['_version'] = '1.0'
        
        return cleaned
    
    def validate_batch(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate a batch of records"""
        results = {
            'total': len(records),
            'valid': 0,
            'invalid': 0,
            'records': [],
            'errors': []
        }
        
        for idx, record in enumerate(records):
            validation = self.validate(record)
            if validation['valid']:
                results['valid'] += 1
                results['records'].append(self.clean(record))
            else:
                results['invalid'] += 1
                results['errors'].append({
                    'index': idx,
                    'errors': validation['errors']
                })
        
        return results
