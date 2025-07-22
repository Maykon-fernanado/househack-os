import json

# Import your agents and core logic modules
from agents import gemini_agent, claude_agent, chatgpt_agent, deepseek_agent
from agents import adversarial_agents  # For adversarial philosophy layer
from core import greenlight_logic, monte_carlo_engine, conditional_decision

def run_full_pipeline(property_data: dict, investor_profile: dict) -> dict:
    """
    Run the full multi-agent house hacker property screening and decision pipeline.
    Inputs:
      - property_data: dict with property details (address, sqft, price, taxes, etc.)
      - investor_profile: dict with investor preferences, risk appetite, etc.
    Returns:
      - Final structured memo and decision output
    """

    # 1. Gemini Agent - Aggregate and validate data
    gemini_snapshot = gemini_agent.get_property_snapshot(property_data["address"])
    
    # 2. Claude Agent - Fact check & clean Gemini data
    claude_validated = claude_agent.fact_check_market_snapshot(gemini_snapshot)
    
    # 3. Greenlight Gate Evaluation (deterministic screening)
    greenlight_result = greenlight_logic.evaluate_property(claude_validated)
    
    # 4. ChatGPT Agent - Strategy Architect (bull/base/bear thesis)
    strategy_thesis = chatgpt_agent.build_investment_thesis(claude_validated, investor_profile)
    
    # 5. DeepSeek Agent - Adversarial Critique of thesis
    critique = deepseek_agent.run_deepseek_task("adversarial_thesis", {"thesis": strategy_thesis})
    
    # 6. Claude Agent - Synthesis Engine (combine thesis and critique)
    synthesis = claude_agent.synthesize_thesis_and_critique(strategy_thesis, critique)
    
    # 7. Claude Agent - Simplifier + Translator for buyer-friendly memo
    simplified_memo = claude_agent.simplify_and_translate_memo(synthesis)
    
    # 8. Monte Carlo Simulation Engine - Run scenario simulation
    simulation_results = monte_carlo_engine.run_simulation(claude_validated, investor_profile)
    
    # 9. Conditional Decision Memo - Phase 4
    conditional_memo = conditional_decision.create_conditional_memo({
        "confidence_score": synthesis.get("confidence_score", 50),
        "simulation_analysis": simulation_results
    })
    
    # 10. Final Decision Gate - Phase 5
    proceed_flag = conditional_decision.final_decision_gate(conditional_memo)
    
    # 11. Assemble final output memo
    final_output = {
        "property": property_data["address"],
        "greenlight_gate": greenlight_result,
        "strategy_thesis": strategy_thesis,
        "adversarial_critique": critique,
        "synthesis": synthesis,
        "simplified_memo": simplified_memo,
        "simulation": simulation_results,
        "conditional_memo": conditional_memo,
        "final_decision": "Proceed" if proceed_flag else "Blocked",
    }
    
    return final_output


if __name__ == "__main__":
    # Example property and investor profile (replace with real input source)
    property_data_example = {
        "address": "18 Robert Avenue, Elmont, NY 11003",
        "sqft": 1300,
        "taxes_annual": 9500,
        "insurance_estimate": 150,
        "price": 575000,
        "expected_rent": 2600,
        "has_hoa": False,
        "has_basement_entry": True
    }
    
    investor_profile_example = {
        "risk_appetite": "conservative",
        "timeline_months": 24,
        "max_monthly_budget": 5000,
        "experience_level": "first_time"
    }
    
    result = run_full_pipeline(property_data_example, investor_profile_example)
    
    print(json.dumps(result, indent=2))

