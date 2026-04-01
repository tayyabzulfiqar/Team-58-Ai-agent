"""
Session Manager - Handles session isolation and data persistence
"""
import uuid
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime


class SessionManager:
    """
    Manages session isolation with UUID-based folders
    """
    
    def __init__(self, base_path: str = "data/sessions"):
        self.base_path = base_path
        self.current_session_id = None
        self.session_data = {}
        
    def create_session(self, metadata: Dict = None) -> str:
        """
        Create new session with UUID and folder structure
        """
        session_id = str(uuid.uuid4())
        self.current_session_id = session_id
        
        # Create session folder
        session_path = os.path.join(self.base_path, session_id)
        os.makedirs(session_path, exist_ok=True)
        
        # Initialize session data
        self.session_data = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "steps": {},
            "metadata": metadata or {}
        }
        
        # Save session manifest
        self._save_manifest()
        
        return session_id
    
    def save_step(self, step_name: str, data: Any) -> bool:
        """
        Save step output to session folder
        """
        if not self.current_session_id:
            raise ValueError("No active session. Call create_session() first.")
        
        # Store in session data
        self.session_data["steps"][step_name] = {
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        # Save to file
        session_path = os.path.join(self.base_path, self.current_session_id)
        step_file = os.path.join(session_path, f"{step_name}.json")
        
        try:
            with open(step_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving step {step_name}: {e}")
            return False
    
    def load_step(self, step_name: str) -> Optional[Any]:
        """
        Load step output from session
        """
        if not self.current_session_id:
            return None
        
        # Check memory first
        if step_name in self.session_data.get("steps", {}):
            return self.session_data["steps"][step_name]["data"]
        
        # Load from file
        session_path = os.path.join(self.base_path, self.current_session_id)
        step_file = os.path.join(session_path, f"{step_name}.json")
        
        if os.path.exists(step_file):
            try:
                with open(step_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading step {step_name}: {e}")
        
        return None
    
    def load_session(self, session_id: str) -> Dict:
        """
        Load existing session by ID
        """
        session_path = os.path.join(self.base_path, session_id)
        manifest_file = os.path.join(session_path, "manifest.json")
        
        if not os.path.exists(manifest_file):
            raise ValueError(f"Session {session_id} not found")
        
        with open(manifest_file, 'r') as f:
            manifest = json.load(f)
        
        self.current_session_id = session_id
        self.session_data = manifest
        
        # Load all steps
        for step_name in manifest.get("steps", {}).keys():
            step_data = self.load_step(step_name)
            if step_data:
                self.session_data["steps"][step_name]["data"] = step_data
        
        return manifest
    
    def save_input(self, input_data: Dict) -> bool:
        """
        Save initial input to session
        """
        return self.save_step("input", input_data)
    
    def save_final_output(self, output_data: Dict) -> bool:
        """
        Save final output to session
        """
        success = self.save_step("final_output", output_data)
        if success:
            self._save_manifest()
        return success
    
    def get_session_path(self) -> str:
        """Get current session folder path"""
        if not self.current_session_id:
            raise ValueError("No active session")
        return os.path.join(self.base_path, self.current_session_id)
    
    def get_session_summary(self) -> Dict:
        """Get summary of current session"""
        return {
            "session_id": self.current_session_id,
            "created_at": self.session_data.get("created_at"),
            "total_steps": len(self.session_data.get("steps", {})),
            "step_names": list(self.session_data.get("steps", {}).keys())
        }
    
    def list_all_sessions(self) -> list:
        """List all existing sessions"""
        if not os.path.exists(self.base_path):
            return []
        
        sessions = []
        for session_id in os.listdir(self.base_path):
            session_path = os.path.join(self.base_path, session_id)
            if os.path.isdir(session_path):
                manifest_file = os.path.join(session_path, "manifest.json")
                if os.path.exists(manifest_file):
                    try:
                        with open(manifest_file, 'r') as f:
                            manifest = json.load(f)
                            sessions.append({
                                "session_id": session_id,
                                "created_at": manifest.get("created_at"),
                                "step_count": len(manifest.get("steps", {}))
                            })
                    except:
                        pass
        
        return sessions
    
    def _save_manifest(self):
        """Save session manifest"""
        if not self.current_session_id:
            return
        
        session_path = os.path.join(self.base_path, self.current_session_id)
        manifest_file = os.path.join(session_path, "manifest.json")
        
        with open(manifest_file, 'w') as f:
            json.dump(self.session_data, f, indent=2, default=str)
    
    def close_session(self):
        """Close current session"""
        if self.current_session_id:
            self._save_manifest()
            self.current_session_id = None
            self.session_data = {}


# Example usage
if __name__ == "__main__":
    manager = SessionManager()
    
    # Create session
    session_id = manager.create_session({"user": "admin"})
    print(f"Created session: {session_id}")
    
    # Save input
    manager.save_input({"leads": [{"name": "Test"}]})
    
    # Save step
    manager.save_step("scoring", {"score": 85})
    
    # Get summary
    print(manager.get_session_summary())
