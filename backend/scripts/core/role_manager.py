"""
Role Manager - Manages role-based access control
"""
from typing import Dict, List, Optional


class RoleManager:
    """
    Manages roles and permissions for system access
    """
    
    def __init__(self):
        self.roles = {
            "admin": {
                "name": "Administrator",
                "description": "Full system access",
                "allowed_agents": ["*"],  # All agents
                "allowed_pipelines": ["*"],  # All pipelines
                "permissions": ["full_pipeline", "single_agent", "view_all_sessions", "manage_system"]
            },
            "strategist": {
                "name": "Strategist",
                "description": "Campaign strategy and analysis",
                "allowed_agents": [
                    "scoring_agent",
                    "strategy_engine",
                    "positioning_engine",
                    "prediction_engine"
                ],
                "allowed_pipelines": ["strategy_pipeline", "scoring_only"],
                "permissions": ["single_agent", "view_own_sessions"]
            },
            "researcher": {
                "name": "Researcher",
                "description": "Data research and market analysis",
                "allowed_agents": [
                    "data_agent",
                    "processing_agent",
                    "market_analyzer",
                    "competitor_analyzer"
                ],
                "allowed_pipelines": ["research_pipeline"],
                "permissions": ["single_agent", "view_own_sessions"]
            }
        }
    
    def get_allowed_agents(self, role: str) -> List[str]:
        """
        Get list of agents allowed for a role
        """
        role_data = self.roles.get(role)
        if not role_data:
            return []
        
        allowed = role_data.get("allowed_agents", [])
        if "*" in allowed:
            # Return all agent names
            return [
                "data_agent",
                "processing_agent",
                "scoring_agent",
                "strategy_engine",
                "market_analyzer",
                "competitor_analyzer",
                "positioning_engine",
                "prediction_engine",
                "feedback_analyzer",
                "pattern_learner",
                "learning_optimizer",
                "celebrity_intelligence_agent"
            ]
        
        return allowed
    
    def can_run_agent(self, role: str, agent_name: str) -> bool:
        """
        Check if role can run specific agent
        """
        allowed_agents = self.get_allowed_agents(role)
        return agent_name in allowed_agents
    
    def can_run_pipeline(self, role: str, pipeline_type: str) -> bool:
        """
        Check if role can run specific pipeline
        """
        role_data = self.roles.get(role)
        if not role_data:
            return False
        
        allowed_pipelines = role_data.get("allowed_pipelines", [])
        return "*" in allowed_pipelines or pipeline_type in allowed_pipelines
    
    def get_role_permissions(self, role: str) -> List[str]:
        """
        Get permissions for a role
        """
        role_data = self.roles.get(role)
        if not role_data:
            return []
        return role_data.get("permissions", [])
    
    def has_permission(self, role: str, permission: str) -> bool:
        """
        Check if role has specific permission
        """
        permissions = self.get_role_permissions(role)
        return permission in permissions
    
    def is_valid_role(self, role: str) -> bool:
        """
        Check if role exists
        """
        return role in self.roles
    
    def list_roles(self) -> List[Dict]:
        """
        List all available roles
        """
        return [
            {
                "id": key,
                "name": data["name"],
                "description": data["description"],
                "agent_count": len(self.get_allowed_agents(key))
            }
            for key, data in self.roles.items()
        ]


# Example usage
if __name__ == "__main__":
    manager = RoleManager()
    
    print("Roles:")
    for role in manager.list_roles():
        print(f"  - {role['name']}: {role['description']}")
        print(f"    Agents: {manager.get_allowed_agents(role['id'])}")
