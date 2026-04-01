"""
Core Package - Central orchestration system
"""
__version__ = "1.0.0"

from .master_controller import MasterController
from .agent_registry import AgentRegistry
from .role_manager import RoleManager
from .session_manager import SessionManager

__all__ = [
    "MasterController",
    "AgentRegistry", 
    "RoleManager",
    "SessionManager"
]
