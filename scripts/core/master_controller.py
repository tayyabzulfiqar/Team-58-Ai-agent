"""
Master Controller - Central orchestration system
Manages full pipeline and single agent execution with session isolation
"""
import sys
import os

# Add project root to Python path for absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.core.session_manager import SessionManager
from scripts.core.agent_registry import AgentRegistry
from scripts.core.role_manager import RoleManager
from typing import Dict, Any, List, Optional


class MasterController:
    """
    Master control system for campaign intelligence platform
    """
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.agent_registry = AgentRegistry()
        self.role_manager = RoleManager()
        
    def run_full_pipeline(self, input_data: Dict, role: str = "admin") -> Dict[str, Any]:
        """
        Run complete campaign pipeline in isolated session
        """
        # Verify role permission
        if not self.role_manager.can_run_pipeline(role, "full_pipeline"):
            return {
                "error": "Insufficient permissions for full pipeline",
                "role": role,
                "allowed": self.role_manager.get_allowed_agents(role)
            }
        
        # Create isolated session
        session_id = self.session_manager.create_session({
            "mode": "full_pipeline",
            "role": role,
            "input_lead_count": len(input_data.get("leads", []))
        })
        
        # Save input
        self.session_manager.save_input(input_data)
        
        results = {
            "session_id": session_id,
            "mode": "full_pipeline",
            "steps_completed": [],
            "errors": []
        }
        
        try:
            # Step 1: Data Processing (if raw data)
            leads = input_data.get("leads", [])
            if leads and isinstance(leads[0], dict) and "pain_points" in leads[0]:
                # Already processed leads
                processed_leads = leads
            else:
                # Need to process
                processing_agent = self.agent_registry.get_agent("processing_agent")
                processed_leads = processing_agent.process_batch(leads) if processing_agent else leads
            
            self.session_manager.save_step("processing", {"processed_count": len(processed_leads)})
            results["steps_completed"].append("processing")
            
            # Step 2: Scoring
            scoring_agent = self.agent_registry.get_agent("scoring_agent")
            scored_leads = []
            for lead in processed_leads:
                try:
                    scored = scoring_agent.qualify_lead(lead) if scoring_agent else lead
                    scored_leads.append(scored)
                except Exception as e:
                    results["errors"].append(f"Scoring error: {str(e)}")
            
            self.session_manager.save_step("scoring", {"scored_leads": scored_leads})
            results["steps_completed"].append("scoring")
            
            # Step 3: Strategy Generation
            strategy_engine = self.agent_registry.get_agent("strategy_engine")
            strategies = []
            for lead in scored_leads:
                try:
                    strategy = strategy_engine.generate_strategy(lead) if strategy_engine else {}
                    strategies.append(strategy)
                except Exception as e:
                    results["errors"].append(f"Strategy error: {str(e)}")
            
            self.session_manager.save_step("strategy", {"strategies": strategies})
            results["steps_completed"].append("strategy")
            
            # Step 4: Market Analysis
            market_analyzer = self.agent_registry.get_agent("market_analyzer")
            market_insights = market_analyzer.analyze(processed_leads) if market_analyzer else {}
            self.session_manager.save_step("market", market_insights)
            results["steps_completed"].append("market_analysis")
            
            # Step 5: Competitor Analysis
            competitor_analyzer = self.agent_registry.get_agent("competitor_analyzer")
            competitor_insights = competitor_analyzer.analyze(market_insights, processed_leads) if competitor_analyzer else {}
            self.session_manager.save_step("competitor", competitor_insights)
            results["steps_completed"].append("competitor_analysis")
            
            # Step 6: Positioning
            positioning_engine = self.agent_registry.get_agent("positioning_engine")
            positioning_results = []
            for i, (lead, strategy) in enumerate(zip(scored_leads[:3], strategies[:3])):
                if strategy.get("color") != "BLACK":
                    pos = positioning_engine.generate(strategy, market_insights, competitor_insights) if positioning_engine else {}
                    positioning_results.append(pos)
            
            self.session_manager.save_step("positioning", {"positioning": positioning_results})
            results["steps_completed"].append("positioning")
            
            # Step 7: Prediction
            prediction_engine = self.agent_registry.get_agent("prediction_engine")
            patterns = {"top_patterns": [], "weak_patterns": []}
            predictions = []
            for lead, strategy, pos in zip(scored_leads[:3], strategies[:3], positioning_results):
                if strategy.get("color") != "BLACK":
                    pred = prediction_engine.predict(lead, patterns, market_insights, competitor_insights, pos) if prediction_engine else {}
                    predictions.append(pred)
            
            self.session_manager.save_step("prediction", {"predictions": predictions})
            results["steps_completed"].append("prediction")
            
            # Step 8: Learning System
            feedback_analyzer = self.agent_registry.get_agent("feedback_analyzer")
            if feedback_analyzer and strategies:
                feedback = feedback_analyzer.analyze(scored_leads, strategies)
                self.session_manager.save_step("feedback", feedback)
                
                pattern_learner = self.agent_registry.get_agent("pattern_learner")
                if pattern_learner:
                    patterns = pattern_learner.analyze(feedback)
                    self.session_manager.save_step("patterns", patterns)
                    
                    learning_optimizer = self.agent_registry.get_agent("learning_optimizer")
                    if learning_optimizer:
                        optimization = learning_optimizer.update(patterns)
                        self.session_manager.save_step("optimization", optimization)
            
            results["steps_completed"].append("learning")
            
            # Build summary
            summary = self._build_summary(scored_leads, strategies, predictions)
            
            # Final output
            final_output = {
                "session_id": session_id,
                "mode": "full_pipeline",
                "summary": summary,
                "market_insights": market_insights,
                "competitor_insights": competitor_insights,
                "positioning": positioning_results,
                "predictions": predictions,
                "steps_completed": results["steps_completed"],
                "errors": results["errors"] if results["errors"] else None
            }
            
            self.session_manager.save_final_output(final_output)
            
            return final_output
            
        except Exception as e:
            error_output = {
                "session_id": session_id,
                "mode": "full_pipeline",
                "status": "error",
                "error": str(e),
                "steps_completed": results["steps_completed"]
            }
            self.session_manager.save_final_output(error_output)
            return error_output
    
    def run_single_agent(self, agent_name: str, input_data: Any, role: str = "admin") -> Dict[str, Any]:
        """
        Run single agent in isolated session
        """
        # Verify agent exists
        if not self.agent_registry.is_valid_agent(agent_name):
            return {
                "error": f"Unknown agent: {agent_name}",
                "available_agents": self.agent_registry.list_agents()
            }
        
        # Verify role permission
        if not self.role_manager.can_run_agent(role, agent_name):
            return {
                "error": f"Role '{role}' cannot access agent '{agent_name}'",
                "role": role,
                "allowed_agents": self.role_manager.get_allowed_agents(role)
            }
        
        # Create isolated session
        session_id = self.session_manager.create_session({
            "mode": "single_agent",
            "agent": agent_name,
            "role": role
        })
        
        # Save input
        self.session_manager.save_input({"agent": agent_name, "input": input_data})
        
        try:
            # Get agent instance
            agent = self.agent_registry.get_agent(agent_name)
            
            # Run agent based on type
            result = self._execute_agent(agent_name, agent, input_data)
            
            # Save result
            self.session_manager.save_step("output", result)
            
            final_output = {
                "session_id": session_id,
                "mode": "single_agent",
                "agent": agent_name,
                "result": result
            }
            
            self.session_manager.save_final_output(final_output)
            return final_output
            
        except Exception as e:
            error_output = {
                "session_id": session_id,
                "mode": "single_agent",
                "agent": agent_name,
                "status": "error",
                "error": str(e)
            }
            self.session_manager.save_final_output(error_output)
            return error_output
    
    def _execute_agent(self, agent_name: str, agent, input_data: Any) -> Any:
        """
        Execute specific agent with input data
        """
        if agent_name == "scoring_agent":
            return agent.qualify_lead(input_data) if hasattr(agent, 'qualify_lead') else input_data
        
        elif agent_name == "strategy_engine":
            return agent.generate_strategy(input_data) if hasattr(agent, 'generate_strategy') else input_data
        
        elif agent_name == "market_analyzer":
            return agent.analyze(input_data) if hasattr(agent, 'analyze') else input_data
        
        elif agent_name == "competitor_analyzer":
            # Competitor needs market insights too
            market = input_data.get("market", {})
            leads = input_data.get("leads", [])
            return agent.analyze(market, leads) if hasattr(agent, 'analyze') else input_data
        
        elif agent_name == "positioning_engine":
            strategy = input_data.get("strategy", {})
            market = input_data.get("market", {})
            competitor = input_data.get("competitor", {})
            return agent.generate(strategy, market, competitor) if hasattr(agent, 'generate') else input_data
        
        elif agent_name == "prediction_engine":
            lead = input_data.get("lead", {})
            patterns = input_data.get("patterns", {})
            market = input_data.get("market", {})
            competitor = input_data.get("competitor", {})
            positioning = input_data.get("positioning", {})
            return agent.predict(lead, patterns, market, competitor, positioning) if hasattr(agent, 'predict') else input_data
        
        elif agent_name == "celebrity_intelligence_agent":
            celebrity_data = input_data.get("celebrity", input_data)
            target_market = input_data.get("target_market", "Dubai")
            return agent.analyze(celebrity_data, target_market) if hasattr(agent, 'analyze') else input_data
        
        else:
            # Generic execution
            return {"agent": agent_name, "data": input_data, "note": "Agent executed"}
    
    def _build_summary(self, scored_leads: List, strategies: List, predictions: List) -> Dict:
        """
        Build summary statistics
        """
        red_count = sum(1 for s in scored_leads if 'RED' in s.get('color', ''))
        orange_count = sum(1 for s in scored_leads if 'ORANGE' in s.get('color', ''))
        yellow_count = sum(1 for s in scored_leads if 'YELLOW' in s.get('color', ''))
        black_count = sum(1 for s in scored_leads if 'BLACK' in s.get('color', ''))
        
        avg_score = sum(s.get('score', 0) for s in scored_leads) / len(scored_leads) if scored_leads else 0
        
        return {
            "total_leads": len(scored_leads),
            "red": red_count,
            "orange": orange_count,
            "yellow": yellow_count,
            "black": black_count,
            "average_score": round(avg_score, 1),
            "predictions_generated": len(predictions)
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get overall system status
        """
        return {
            "system": "operational",
            "agents_registered": len(self.agent_registry.list_agents()),
            "roles_defined": len(self.role_manager.list_roles()),
            "active_sessions": len(self.session_manager.list_all_sessions()),
            "capabilities": [
                "full_pipeline",
                "single_agent",
                "session_isolation",
                "role_based_access"
            ]
        }


# Example usage
if __name__ == "__main__":
    controller = MasterController()
    
    # Test system status
    print("System Status:", controller.get_system_status())
