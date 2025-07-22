from typing import Dict, Any
from agents.gemini_agent import fetch_property_data  # Your Gemini data aggregator

class GreenlightGateEvaluation:
    def __init__(self, property_input: Dict[str, Any]):
        self.raw_input = property_input
        self.verified_data = None
        self.criteria_results = {}
        self.tier_score = 0.0
        self.tier_fails = {"Tier_1_Critical": 0}
        self.verdict = ""
        self.notes = ""

        # Define tier weights based on your config
        self.tier_weights = {
            "Tier_1_Critical": {
                "tax_below_10k": 2.0,
                "20pct_down_breakeven_under_5k": 2.0,
                "room_rental_supports_2k+": 2.0,
            },
            "Tier_2_Important": {
                "price_per_sqft_under_350": 1.0,
                "sqft_verified_1000+": 1.0,
            },
            "Tier_3_Bonus": {
                "has_basement_with_entry": 0.5,
                "no_hoa": 0.5,
            }
        }

    def run(self):
        # Step 1: Use Gemini agent to get verified property data
        self.verified_data = fetch_property_data(self.raw_input["address"])

        # Step 2: Combine input and verified data for evaluation
        data = {**self.raw_input, **self.verified_data}

        # Step 3: Evaluate criteria
        self.evaluate_criteria(data)

        # Step 4: Calculate tier score
        self.calculate_tier_score()

        # Step 5: Determine verdict & notes
        self.determine_verdict()

        # Step 6: Prepare output
        return self.format_output()

    def evaluate_criteria(self, data: Dict[str, Any]):
        # Has basement with entry
        self.criteria_results["has_basement_with_entry"] = bool(data.get("has_basement_entry", False))

        # Price per sqft under $350
        price = data.get("price", 0)
        sqft = data.get("sqft", 1)  # prevent division by zero
        price_per_sqft = price / sqft
        self.criteria_results["price_per_sqft_under_350"] = price_per_sqft < 350

        # Taxes below $10k annually
        taxes = data.get("taxes_annual", 999999)
        self.criteria_results["tax_below_10k"] = taxes < 10000

        # 20% down breakeven under $5k/mo (Estimate)
        # P&I estimate, tax, insurance approximated
        loan_amount = price * 0.8
        # Rough P&I monthly payment for loan at ~7.25%
        # Use simplified mortgage formula or fixed P&I (could be enhanced)
        monthly_pi = loan_amount * 0.00725 / 12  # very rough monthly interest only approx
        monthly_tax = taxes / 12
        insurance = data.get("insurance_estimate", 150)
        total_monthly = monthly_pi + monthly_tax + insurance
        self.criteria_results["20pct_down_breakeven_under_5k"] = total_monthly < 5000

        # Room rental supports $2,000+ monthly (expected rent input)
        expected_rent = data.get("expected_rent", 0)
        self.criteria_results["room_rental_supports_2k+"] = expected_rent >= 2000

        # Sqft verified ≥ 1,000
        self.criteria_results["sqft_verified_1000+"] = sqft >= 1000

        # No HOA or condo
        self.criteria_results["no_hoa"] = not data.get("has_hoa", False)

    def calculate_tier_score(self):
        score = 0.0
        tier_1_fails = 0

        for tier, crits in self.tier_weights.items():
            for crit, weight in crits.items():
                passed = self.criteria_results.get(crit, False)
                if passed:
                    score += weight
                else:
                    if tier == "Tier_1_Critical":
                        tier_1_fails += 1
        self.tier_score = score
        self.tier_fails["Tier_1_Critical"] = tier_1_fails

    def determine_verdict(self):
        tier_1_fails = self.tier_fails["Tier_1_Critical"]

        if self.tier_score >= 6.0 and tier_1_fails == 0:
            self.verdict = "✅ GREENLIGHT"
        elif 4.0 <= self.tier_score < 6.0 or tier_1_fails == 1:
            self.verdict = "🟡 YELLOW LIGHT"
        else:
            self.verdict = "🔴 RED LIGHT"

        # Compose notes
        notes = []
        if tier_1_fails > 0:
            notes.append(f"{tier_1_fails} Tier 1 fail(s)")

        failed_criteria = [crit for crit, passed in self.criteria_results.items() if not passed]
        if failed_criteria:
            notes.append(f"Failed criteria: {', '.join(failed_criteria)}")

        # Highlight strong points (optional)
        passed_criteria = [crit for crit, passed in self.criteria_results.items() if passed]
        notes.append(f"Passed criteria: {', '.join(passed_criteria)}")

        self.notes = ". ".join(notes)

    def format_output(self):
        return {
            "address": self.raw_input["address"],
            "greenlight_gate": self.criteria_results,
            "tier_score": round(self.tier_score, 2),
            "summary": {
                "verdict": self.verdict,
                "notes": self.notes
            }
        }


# Example usage:
if __name__ == "__main__":
    sample_property = {
        "address": "54 Biltmore Avenue, Elmont, NY 11003",
        # Minimal inputs if available
        # Note: fetch_property_data will enrich with verified info
    }
    evaluator = GreenlightGateEvaluation(sample_property)
    result = evaluator.run()
    print(result)

