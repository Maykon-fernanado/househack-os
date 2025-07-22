from typing import Dict, Any, List


def create_conditional_memo(simulation_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Phase 4: Create Conditional Memo based on confidence score and simulation success rate.
    
    Input example:
    {
      "confidence_score": 63,
      "simulation_analysis": {
        "success_rate": 0.55,
        ...
      }
    }
    
    Returns a dict:
    {
      "confidence_score": 63,
      "status": "✅ Proceed" or "❌ Do Not Proceed Unless Conditions Met",
      "conditions": []
    }
    """
    confidence_score = simulation_input.get("confidence_score", 0)
    simulation_analysis = simulation_input.get("simulation_analysis", {})
    success_rate = simulation_analysis.get("success_rate", 0)

    if confidence_score >= 65 and success_rate > 0.6:
        status = "✅ Proceed"
        conditions: List[str] = []
    else:
        status = "❌ Do Not Proceed Unless Conditions Met"
        conditions = [
            "Signed contractor quote <$60K",
            "Pre-close zoning permit or holdback",
            "DSCR refi model + rent roll",
            "$25K liquidity buffer",
            "25% tax hike modeled",
        ]

    return {
        "confidence_score": confidence_score,
        "status": status,
        "conditions": conditions,
    }


def final_decision_gate(conditional_memo: Dict[str, Any]) -> bool:
    """
    Phase 5: Final Decision Firewall
    
    If status is "✅ Proceed", return True (allow execution to continue).
    Otherwise, return False (block execution).
    
    Input example:
    {
      "confidence_score": 63,
      "status": "❌ Do Not Proceed Unless Conditions Met",
      "conditions": [...]
    }
    """
    status = conditional_memo.get("status", "")
    if status == "✅ Proceed":
        # Allow further pipeline execution (e.g. trigger escrow)
        return True
    else:
        # Block further execution due to unsatisfied conditions
        return False


# Example usage
if __name__ == "__main__":
    sample_input = {
        "confidence_score": 63,
        "simulation_analysis": {
            "success_rate": 0.55,
            "downside_loss_rate": 0.22,
            "most_likely_outcome": "mild cash flow stress, no refi"
        }
    }

    memo = create_conditional_memo(sample_input)
    print("Conditional Memo:", memo)

    proceed = final_decision_gate(memo)
    print("Allowed to proceed?" , proceed)

