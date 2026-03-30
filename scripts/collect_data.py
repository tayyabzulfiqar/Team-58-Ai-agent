"""
Data Collection Agent - Legacy Interface
Maintained for backward compatibility
"""
from agents.data_agent import DataAgent

# Legacy interface for backward compatibility
def get_raw_leads():
    """Legacy function - redirects to new DataAgent"""
    agent = DataAgent()
    return agent.collect_raw_data()