"""
Event-Based Trigger System for High-Value Leads
Detects leads with score > 90 or revenue > $50K and triggers immediate pipeline runs
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from threading import Lock

from core.master_controller import MasterController

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/live/priority_events.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('EventTrigger')

# Constants
PRIORITY_THRESHOLD_SCORE = 90
PRIORITY_THRESHOLD_REVENUE = 50000
PRIORITY_DATA_PATH = Path('data/live/priority_run.json')
PRIORITY_HISTORY_PATH = Path('data/live/priority_history.json')

class EventTrigger:
    """
    Event-based trigger system for high-value lead detection
    Triggers immediate pipeline run when conditions met
    Prevents duplicate triggers
    """
    
    def __init__(self):
        self.controller = MasterController()
        self.triggered_leads = set()  # Track already-triggered leads
        self.lock = Lock()
        self._load_history()
        
    def _load_history(self):
        """Load previously triggered leads from history"""
        try:
            if PRIORITY_HISTORY_PATH.exists():
                with open(PRIORITY_HISTORY_PATH, 'r') as f:
                    history = json.load(f)
                    for event in history.get('events', []):
                        lead_id = event.get('lead_id')
                        if lead_id:
                            self.triggered_leads.add(lead_id)
                logger.info(f"Loaded {len(self.triggered_leads)} previously triggered leads")
        except Exception as e:
            logger.error(f"Error loading history: {e}")
    
    def _get_lead_id(self, lead: Dict[str, Any]) -> str:
        """Generate unique ID for lead"""
        name = lead.get('name', 'unknown')
        company = lead.get('company', 'unknown')
        timestamp = lead.get('timestamp', datetime.now().isoformat())
        return f"{name}_{company}_{timestamp}"
    
    def _is_high_value(self, lead: Dict[str, Any]) -> tuple[bool, str]:
        """
        Check if lead meets high-value criteria
        Returns: (is_high_value, reason)
        """
        score = lead.get('score', 0)
        budget = lead.get('budget', 0)
        
        if score > PRIORITY_THRESHOLD_SCORE:
            return True, f"Score {score} > {PRIORITY_THRESHOLD_SCORE}"
        
        if budget > PRIORITY_THRESHOLD_REVENUE:
            return True, f"Revenue ${budget:,} > ${PRIORITY_THRESHOLD_REVENUE:,}"
        
        return False, ""
    
    def _is_duplicate(self, lead_id: str) -> bool:
        """Check if lead was already triggered"""
        with self.lock:
            return lead_id in self.triggered_leads
    
    def _mark_triggered(self, lead_id: str):
        """Mark lead as triggered"""
        with self.lock:
            self.triggered_leads.add(lead_id)
    
    def _save_priority_run(self, lead: Dict[str, Any], result: Dict[str, Any], reason: str):
        """Save priority run to file"""
        try:
            PRIORITY_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
            
            priority_data = {
                "timestamp": datetime.now().isoformat(),
                "trigger_reason": reason,
                "lead": lead,
                "result": result,
                "event_type": "HIGH PRIORITY EVENT"
            }
            
            with open(PRIORITY_DATA_PATH, 'w') as f:
                json.dump(priority_data, f, indent=2, default=str)
            
            logger.info(f"Priority run saved to {PRIORITY_DATA_PATH}")
            
        except Exception as e:
            logger.error(f"Error saving priority run: {e}")
    
    def _save_to_history(self, lead: Dict[str, Any], reason: str):
        """Save event to history file"""
        try:
            history = {"events": []}
            if PRIORITY_HISTORY_PATH.exists():
                with open(PRIORITY_HISTORY_PATH, 'r') as f:
                    history = json.load(f)
            
            lead_id = self._get_lead_id(lead)
            
            event = {
                "lead_id": lead_id,
                "timestamp": datetime.now().isoformat(),
                "reason": reason,
                "lead_name": lead.get('name', 'unknown'),
                "lead_company": lead.get('company', 'unknown'),
                "score": lead.get('score', 0),
                "budget": lead.get('budget', 0),
                "event_type": "HIGH PRIORITY EVENT"
            }
            
            history['events'].insert(0, event)  # Add to beginning
            
            # Keep only last 100 events
            history['events'] = history['events'][:100]
            
            with open(PRIORITY_HISTORY_PATH, 'w') as f:
                json.dump(history, f, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"Error saving history: {e}")
    
    def check_and_trigger(self, lead: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Check lead and trigger pipeline if high-value
        Returns result if triggered, None otherwise
        """
        lead_id = self._get_lead_id(lead)
        
        # Check if high-value
        is_high_value, reason = self._is_high_value(lead)
        
        if not is_high_value:
            return None
        
        # Check for duplicate
        if self._is_duplicate(lead_id):
            logger.info(f"Duplicate trigger prevented for {lead.get('name', 'unknown')}")
            return None
        
        # Mark as triggered to prevent duplicates
        self._mark_triggered(lead_id)
        
        # Log HIGH PRIORITY EVENT
        logger.info(f"HIGH PRIORITY EVENT DETECTED: {reason}")
        logger.info(f"Triggering immediate pipeline for {lead.get('name', 'unknown')}")
        
        try:
            # Run pipeline immediately
            result = self.controller.run_full_pipeline(
                {"leads": [lead]},
                role="admin"
            )
            
            # Save priority run
            self._save_priority_run(lead, result, reason)
            
            # Save to history
            self._save_to_history(lead, reason)
            
            logger.info(f"Priority pipeline completed for {lead.get('name', 'unknown')}")
            
            return {
                "triggered": True,
                "reason": reason,
                "lead": lead,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error triggering priority pipeline: {e}")
            return {
                "triggered": False,
                "error": str(e),
                "lead": lead,
                "timestamp": datetime.now().isoformat()
            }
    
    def check_batch(self, leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Check batch of leads and trigger for each high-value lead
        Returns list of triggered results
        """
        results = []
        
        for lead in leads:
            result = self.check_and_trigger(lead)
            if result:
                results.append(result)
        
        return results
    
    def get_priority_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get all high-priority events from history
        """
        try:
            if not PRIORITY_HISTORY_PATH.exists():
                return []
            
            with open(PRIORITY_HISTORY_PATH, 'r') as f:
                history = json.load(f)
            
            return history.get('events', [])[:limit]
            
        except Exception as e:
            logger.error(f"Error loading priority events: {e}")
            return []
    
    def get_latest_priority_run(self) -> Optional[Dict[str, Any]]:
        """
        Get latest priority run
        """
        try:
            if not PRIORITY_DATA_PATH.exists():
                return None
            
            with open(PRIORITY_DATA_PATH, 'r') as f:
                return json.load(f)
            
        except Exception as e:
            logger.error(f"Error loading latest priority run: {e}")
            return None

# Global event trigger instance
_event_trigger = None

def get_event_trigger() -> EventTrigger:
    """Get or create global event trigger instance"""
    global _event_trigger
    if _event_trigger is None:
        _event_trigger = EventTrigger()
    return _event_trigger

def check_lead(lead: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Check single lead for high-value trigger"""
    trigger = get_event_trigger()
    return trigger.check_and_trigger(lead)

def check_leads_batch(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Check batch of leads for high-value triggers"""
    trigger = get_event_trigger()
    return trigger.check_batch(leads)

def get_priority_events(limit: int = 50) -> List[Dict[str, Any]]:
    """Get all high-priority events"""
    trigger = get_event_trigger()
    return trigger.get_priority_events(limit)

def get_latest_priority_run() -> Optional[Dict[str, Any]]:
    """Get latest priority run"""
    trigger = get_event_trigger()
    return trigger.get_latest_priority_run()

if __name__ == "__main__":
    # Test event trigger
    test_leads = [
        {"name": "High Value Lead", "company": "BigCorp", "score": 95, "budget": 75000, "industry": "Tech", "location": "Dubai"},
        {"name": "Normal Lead", "company": "SmallCorp", "score": 70, "budget": 25000, "industry": "Retail", "location": "London"},
        {"name": "Revenue Lead", "company": "RichCorp", "score": 85, "budget": 100000, "industry": "Finance", "location": "NYC"},
    ]
    
    trigger = EventTrigger()
    
    for lead in test_leads:
        result = trigger.check_and_trigger(lead)
        if result:
            print(f"Triggered for {lead['name']}: {result.get('reason')}")
        else:
            print(f"No trigger for {lead['name']}")
