from backend.agents.campaign_agent import CampaignAgent
from backend.agents.data_agent import DataAgent
from backend.agents.research_agent import ResearchAgent
from backend.memory.store import save_run
from backend.memory.store import store_outcome
from backend.tools.objective_detector import detect_objective


def run_system(input_data):
    objective = detect_objective(input_data)
    research = ResearchAgent().run(input_data)
    data = DataAgent().run(research)
    if isinstance(data, dict):
        data["original_input"] = input_data
        data["objective"] = objective
    campaign = CampaignAgent().run(data)
    if isinstance(campaign, dict):
        decision = campaign.get("decision_meta", {})
        if isinstance(decision, dict):
            store_outcome(
                input_data,
                decision.get("selected_strategy", ""),
                decision.get("confidence", 50)
            )
    save_run({
        "input": input_data,
        "output": data
    })
    return campaign
