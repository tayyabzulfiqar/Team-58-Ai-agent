"""
Processing Agent - Legacy Interface
Maintained for backward compatibility
"""
from agents.processing_agent import ProcessingAgent

# Legacy interface for backward compatibility
def process_lead(lead):
    """Legacy function - redirects to new ProcessingAgent"""
    agent = ProcessingAgent()
    processed_data = agent.process_raw_data([lead])
    return processed_data[0] if processed_data else lead