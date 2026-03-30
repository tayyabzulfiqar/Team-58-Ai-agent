"""
Real Feedback Collector - Collects actual campaign outcomes
"""
import json
import os
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealFeedbackCollector:
    """
    Collects and stores real campaign feedback
    Handles retries, validation, and error recovery
    """
    
    def __init__(self, base_path: str = "data/feedback"):
        self.base_path = base_path
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        
    def collect_feedback(self, session_id: str, feedback_data: Dict) -> Dict[str, Any]:
        """
        Collect and store real feedback with validation and retry logic
        """
        # Validate input
        validation = self._validate_feedback(feedback_data)
        if not validation["valid"]:
            logger.error(f"Invalid feedback data: {validation['errors']}")
            return {
                "success": False,
                "error": f"Validation failed: {validation['errors']}",
                "session_id": session_id
            }
        
        # Create session folder
        session_path = os.path.join(self.base_path, session_id)
        os.makedirs(session_path, exist_ok=True)
        
        # Prepare feedback entry
        feedback_entry = {
            "lead_id": feedback_data.get("lead_id"),
            "campaign_id": feedback_data.get("campaign_id", session_id),
            "conversion": feedback_data.get("conversion", False),
            "revenue": feedback_data.get("revenue", 0),
            "response_rate": feedback_data.get("response_rate", 0),
            "meeting_booked": feedback_data.get("meeting_booked", False),
            "timestamp": datetime.now().isoformat(),
            "metadata": feedback_data.get("metadata", {})
        }
        
        # Store with retry logic
        success = self._store_with_retry(session_path, feedback_entry)
        
        if success:
            logger.info(f"Feedback stored for session {session_id}, lead {feedback_entry['lead_id']}")
            return {
                "success": True,
                "session_id": session_id,
                "feedback_id": f"{session_id}_{feedback_entry['lead_id']}",
                "data": feedback_entry
            }
        else:
            return {
                "success": False,
                "error": "Failed to store feedback after retries",
                "session_id": session_id
            }
    
    def _validate_feedback(self, data: Dict) -> Dict[str, Any]:
        """
        Validate feedback data before storage
        """
        errors = []
        
        # Required fields
        if "lead_id" not in data or not data["lead_id"]:
            errors.append("lead_id is required")
        
        # Type validation
        if "conversion" in data and not isinstance(data["conversion"], bool):
            errors.append("conversion must be boolean")
        
        if "revenue" in data:
            try:
                revenue = float(data["revenue"])
                if revenue < 0:
                    errors.append("revenue cannot be negative")
            except (ValueError, TypeError):
                errors.append("revenue must be a number")
        
        if "response_rate" in data:
            try:
                rate = float(data["response_rate"])
                if not 0 <= rate <= 1:
                    errors.append("response_rate must be between 0 and 1")
            except (ValueError, TypeError):
                errors.append("response_rate must be a number between 0 and 1")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _store_with_retry(self, session_path: str, feedback_entry: Dict) -> bool:
        """
        Store feedback with retry logic for reliability
        """
        feedback_file = os.path.join(session_path, "feedback.json")
        
        for attempt in range(self.max_retries):
            try:
                # Load existing feedback if any
                existing_feedback = []
                if os.path.exists(feedback_file):
                    try:
                        with open(feedback_file, 'r') as f:
                            existing_feedback = json.load(f)
                            if not isinstance(existing_feedback, list):
                                existing_feedback = [existing_feedback]
                    except json.JSONDecodeError:
                        logger.warning(f"Corrupted feedback file, creating new")
                        existing_feedback = []
                
                # Append new feedback
                existing_feedback.append(feedback_entry)
                
                # Write with temp file for atomic operation
                temp_file = f"{feedback_file}.tmp"
                with open(temp_file, 'w') as f:
                    json.dump(existing_feedback, f, indent=2)
                
                # Atomic rename
                os.replace(temp_file, feedback_file)
                
                return True
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    logger.error(f"All retries exhausted for feedback storage")
                    return False
        
        return False
    
    def get_feedback_for_session(self, session_id: str) -> List[Dict]:
        """
        Retrieve all feedback for a session
        """
        feedback_file = os.path.join(self.base_path, session_id, "feedback.json")
        
        if not os.path.exists(feedback_file):
            return []
        
        try:
            with open(feedback_file, 'r') as f:
                data = json.load(f)
                return data if isinstance(data, list) else [data]
        except Exception as e:
            logger.error(f"Error loading feedback: {e}")
            return []
    
    def get_all_feedback(self) -> List[Dict]:
        """
        Get all feedback across all sessions
        """
        all_feedback = []
        
        if not os.path.exists(self.base_path):
            return all_feedback
        
        for session_id in os.listdir(self.base_path):
            session_feedback = self.get_feedback_for_session(session_id)
            all_feedback.extend(session_feedback)
        
        return all_feedback
    
    def update_feedback(self, session_id: str, lead_id: str, updates: Dict) -> bool:
        """
        Update existing feedback entry
        """
        feedback_file = os.path.join(self.base_path, session_id, "feedback.json")
        
        if not os.path.exists(feedback_file):
            logger.error(f"No feedback file found for session {session_id}")
            return False
        
        try:
            with open(feedback_file, 'r') as f:
                feedback_list = json.load(f)
                if not isinstance(feedback_list, list):
                    feedback_list = [feedback_list]
            
            # Find and update entry
            updated = False
            for entry in feedback_list:
                if entry.get("lead_id") == lead_id:
                    entry.update(updates)
                    entry["updated_at"] = datetime.now().isoformat()
                    updated = True
                    break
            
            if updated:
                with open(feedback_file, 'w') as f:
                    json.dump(feedback_list, f, indent=2)
                logger.info(f"Updated feedback for lead {lead_id} in session {session_id}")
                return True
            else:
                logger.warning(f"Lead {lead_id} not found in session {session_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating feedback: {e}")
            return False


# Example usage
if __name__ == "__main__":
    collector = RealFeedbackCollector()
    
    # Test with valid feedback
    result = collector.collect_feedback("test_session", {
        "lead_id": "lead_001",
        "conversion": True,
        "revenue": 5000,
        "response_rate": 0.25,
        "meeting_booked": True
    })
    
    print(json.dumps(result, indent=2))
    
    # Test with invalid feedback (should fail validation)
    invalid_result = collector.collect_feedback("test_session", {
        "lead_id": "",
        "conversion": "yes",  # Invalid type
        "revenue": -100  # Invalid value
    })
    
    print(json.dumps(invalid_result, indent=2))
