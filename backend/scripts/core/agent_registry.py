"""
Agent Registry - Registers and manages all system agents
"""
import sys
import os

# Add project root to Python path for absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.agents.data_agent import DataAgent
from scripts.agents.processing_agent import ProcessingAgent
from scripts.agents.lead_qualification_agent import LeadQualificationAgent
from scripts.controllers.lead_strategy_engine import LeadStrategyEngine
from scripts.intelligence.feedback_analyzer import FeedbackAnalyzer
from scripts.intelligence.pattern_learner import PatternLearner
from scripts.intelligence.learning_optimizer import LearningOptimizer
from scripts.intelligence.market_analyzer import MarketAnalyzer
from scripts.intelligence.competitor_analyzer import CompetitorAnalyzer
from scripts.intelligence.positioning_engine import PositioningEngine
from scripts.intelligence.prediction_engine import PredictionEngine
from scripts.intelligence.celebrity_intelligence_agent import CelebrityIntelligenceAgent


class AgentRegistry:
    """
    Central registry for all AI agents in the system
    """
    
    def __init__(self):
        self.agents = {}
        self._register_all_agents()
    
    def _register_all_agents(self):
        """Register all available agents"""
        self.agents = {
            "data_agent": {
                "name": "Data Agent",
                "description": "Collects raw data from various sources",
                "instance": DataAgent(),
                "category": "data"
            },
            "processing_agent": {
                "name": "Processing Agent",
                "description": "Cleans and normalizes raw data",
                "instance": ProcessingAgent(),
                "category": "processing"
            },
            "scoring_agent": {
                "name": "Lead Scoring Agent",
                "description": "Scores and qualifies leads (RED/ORANGE/BLACK)",
                "instance": LeadQualificationAgent(),
                "category": "analysis"
            },
            "strategy_engine": {
                "name": "Strategy Engine",
                "description": "Generates campaign strategies",
                "instance": LeadStrategyEngine(),
                "category": "strategy"
            },
            "market_analyzer": {
                "name": "Market Analyzer",
                "description": "Analyzes market trends and pain points",
                "instance": MarketAnalyzer(),
                "category": "intelligence"
            },
            "competitor_analyzer": {
                "name": "Competitor Analyzer",
                "description": "Analyzes competition and saturation",
                "instance": CompetitorAnalyzer(),
                "category": "intelligence"
            },
            "positioning_engine": {
                "name": "Positioning Engine",
                "description": "Generates positioning angles",
                "instance": PositioningEngine(),
                "category": "strategy"
            },
            "prediction_engine": {
                "name": "Prediction Engine",
                "description": "Predicts campaign success",
                "instance": PredictionEngine(),
                "category": "intelligence"
            },
            "feedback_analyzer": {
                "name": "Feedback Analyzer",
                "description": "Analyzes results and outcomes",
                "instance": FeedbackAnalyzer(),
                "category": "learning"
            },
            "pattern_learner": {
                "name": "Pattern Learner",
                "description": "Discovers success patterns",
                "instance": PatternLearner(),
                "category": "learning"
            },
            "learning_optimizer": {
                "name": "Learning Optimizer",
                "description": "Optimizes scoring weights",
                "instance": LearningOptimizer(),
                "category": "learning"
            },
            "celebrity_intelligence_agent": {
                "name": "Celebrity Intelligence Agent",
                "description": "Analyzes celebrities/influencers for market strategy",
                "instance": CelebrityIntelligenceAgent(),
                "category": "intelligence"
            }
        }
    
    def get_agent(self, name: str):
        """
        Get agent instance by name
        """
        agent_info = self.agents.get(name)
        if agent_info:
            return agent_info["instance"]
        return None
    
    def list_agents(self) -> list:
        """
        List all registered agents
        """
        return [
            {
                "name": key,
                "display_name": info["name"],
                "description": info["description"],
                "category": info["category"]
            }
            for key, info in self.agents.items()
        ]
    
    def get_agents_by_category(self, category: str) -> list:
        """
        Get agents by category
        """
        return [
            key for key, info in self.agents.items()
            if info["category"] == category
        ]
    
    def is_valid_agent(self, name: str) -> bool:
        """
        Check if agent name is valid
        """
        return name in self.agents


# Example usage
if __name__ == "__main__":
    registry = AgentRegistry()
    
    print("Registered Agents:")
    for agent in registry.list_agents():
        print(f"  - {agent['name']}: {agent['description']}")
