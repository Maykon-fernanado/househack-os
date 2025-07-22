# =============================
# 🧑‍💼 Investor Profile Config
# =============================

investor_profile:
  name: House Hacker Tier 1 (FHA Starter)
  profile_type: fha_house_hacker # other options: conventional_investor, dscr_buyer, cash_buyer
  risk_appetite: balanced        # conservative | balanced | aggressive
  timeline: 1–3 years          # <1 year | 1–3 years | 5+ years

financials:
  buyer_income: 115000
  co_signer:
    active: true
    income: 85000
    will_be_co_borrower: true

  credit_score_tier: 660+      # 580–620 | 620–660 | 660+ | 720+
  down_payment_pct: 3.5
  liquid_assets: 32000
  max_monthly_budget: 4600      # optional cap for greenlight filter

preferences:
  wants_to_house_hack: true
  will_owner_occupy: true
  fha_user: true
  wants_adu_conversion: true
  avoids_hoa: true
  needs_basement_unit: preferred  # required | preferred | ignore
  must_be_legal_two_family: false
  prefers_walkable_area: true

adjust_firewall_rules: true      # ⚙️ Turn this on to auto-adjust greenlight_gate + tier_weights

# Optional overrides (if you want manual control instead of auto-adjustment)
manual_tier_weights:
  Tier_1_Critical:
    tax_below_10k: 2.0
    20pct_down_breakeven_under_5k: 2.0
    room_rental_supports_2k+: 2.0
  Tier_2_Important:
    price_per_sqft_under_350: 1.0
    sqft_verified_1000+: 1.0
  Tier_3_Bonus:
    has_basement_with_entry: 0.5
    no_hoa: 0.5


DEFINE System

  FUNCTION GreenlightGateEvaluation(property):
    INIT criteria_results = {}

    criteria_results.has_basement_with_entry = CHECK(property.has_basement_entry)
    criteria_results.price_per_sqft_under_350 = property.price_per_sqft < 350
    criteria_results.tax_below_10k = property.annual_taxes < 10000
    criteria_results.20pct_down_breakeven_under_5k = ESTIMATE_BREAKEVEN(property, down_payment=0.20) < 5000
    criteria_results.room_rental_supports_2k+ = ESTIMATE_ROOM_RENT(property) >= 2000
    criteria_results.sqft_verified_1000+ = property.verified_sqft >= 1000
    criteria_results.no_hoa = property.hoa == false

    RETURN criteria_results

  FUNCTION CalculateTierScore(criteria_results):
    score = 0.0

    # Tier 1 (Critical)
    IF criteria_results.tax_below_10k == true:
      score += 2.0
    IF criteria_results.20pct_down_breakeven_under_5k == true:
      score += 2.0
    IF criteria_results.room_rental_supports_2k+ == true:
      score += 2.0

    # Tier 2 (Important)
    IF criteria_results.price_per_sqft_under_350 == true:
      score += 1.0
    IF criteria_results.sqft_verified_1000+ == true:
      score += 1.0

    # Tier 3 (Bonus)
    IF criteria_results.has_basement_with_entry == true:
      score += 0.5
    IF criteria_results.no_hoa == true:
      score += 0.5

    RETURN score

  FUNCTION DetermineVerdict(score, criteria_results):
    num_failed_tier1 = COUNT_FALSE([
      criteria_results.tax_below_10k,
      criteria_results.20pct_down_breakeven_under_5k,
      criteria_results.room_rental_supports_2k+
    ])

    IF score >= 6.0 AND num_failed_tier1 == 0:
      RETURN "✅ GREENLIGHT"
    ELSE IF score >= 4.0 OR num_failed_tier1 == 1:
      RETURN "🟡 YELLOW LIGHT"
    ELSE:
      RETURN "🔴 RED LIGHT"

  FUNCTION GeminiAgent(property):
    RETURN {
      property_value_trends,
      comps,
      rental_comps,
      DOM_data,
      tax_history,
      zoning,
      ADU_legality,
      market_velocity
    }

  FUNCTION ClaudeFactChecker(gemini_data):
    corrected_data = CORRECT_OR_ESTIMATE(gemini_data)
    flagged_items = FLAG_UNREALISTIC_OR_MISSING(corrected_data)
    RETURN corrected_data, flagged_items

  FUNCTION ChatGPTStrategy(property, corrected_data):
    RETURN {
      Bull: {
        assumptions,
        rent,
        refi,
        appreciation
      },
      Base: {
        assumptions,
        PITI,
        FHA_terms,
        shared_room_rent
      },
      Bear: {
        assumptions,
        negative_carry,
        denied_permits
      },
      CostStack: {
        acquisition_costs,
        monthly_breakeven,
        reserve_needs
      }
    }

  FUNCTION DeepSeekCritique(chatgpt_thesis):
    RETURN {
      Bull: list_of_unrealistic_assumptions,
      Base: list_of_overlooked_costs,
      Bear: risk_factors,
      Timeline: sequencing_warnings,
      Financing: DTI_or_PMI_concerns
    }

  FUNCTION ClaudeSynthesisEngine(chatgpt_thesis, deepseek_critique):
    RETURN {
      summary: {
        Bull, Base, Bear summary
      },
      decision_tree: {
        value_unlocks: [permits, refi],
        risk_triggers: [tax_jump, low_appraisal]
      },
      probability_weights: {
        Bull: %, Base: %, Bear: %
      }
    }

  FUNCTION ClaudeSimplifier(synthesized_report):
    RETURN {
      short_answer: "Is this a good deal?",
      pros: [...],
      cons: [...],
      checklist: [...],
      traffic_light: [🔴 / 🟡 / ✅],
      analogies: [
        "You’ll pay ~$500/month to live here for a year, then could refinance."
      ]
    }

  FUNCTION RunFullPipeline(address_list):
    FOR address IN address_list:
      raw_data = GeminiAgent(address)
      corrected_data, flagged = ClaudeFactChecker(raw_data)

      criteria = GreenlightGateEvaluation(corrected_data)
      score = CalculateTierScore(criteria)
      verdict = DetermineVerdict(score, criteria)

      thesis = ChatGPTStrategy(address, corrected_data)
      critique = DeepSeekCritique(thesis)
      synthesis = ClaudeSynthesisEngine(thesis, critique)
      memo = ClaudeSimplifier(synthesis)

      PRINT {
        "address": address,
        "greenlight_gate": criteria,
        "tier_score": score,
        "verdict": verdict,
        "notes": memo.short_answer,
        "flagged_issues": flagged
      }

END
# =============================
  # 🧠 Phase 2: Adversarial Stress Test
  # =============================
  FUNCTION RunAdversarialAgents(property_memo):
    OUTPUT = {}
    OUTPUT.socrates = INTERROGATE(property_memo)
    OUTPUT.bayes = APPLY_PROBABILISTIC_SCRUB(property_memo)
    OUTPUT.murphy = SIMULATE_FAILURE_CASE(property_memo)
    OUTPUT.machiavelli = DETECT_HUMAN_BIAS(property_memo)

    RETURN OUTPUT

  FUNCTION ScoreConfidenceFromStressTest(agent_output):
    fragilities = COUNT_TOTAL_FLAGS(agent_output)
    RETURN 100 - fragilities * 5  # crude penalty model

# =============================
# 🧠 Phase 3: Agentic Monte Carlo
# =============================

FUNCTION RunMonteCarlo(property, assumptions, investor_profile, N=1000):
    INIT simulations = []
    FOR i IN RANGE(N):
        agent = INIT_INVESTOR_AGENT(investor_profile)
        sim_result = SIMULATE_WITH_AGENT(property, assumptions, agent)
        simulations.APPEND(sim_result)

    RETURN simulations


FUNCTION SIMULATE_WITH_AGENT(property, assumptions, agent):
    INIT timeline = []
    INIT state = INIT_PROPERTY_STATE(property, assumptions)

    FOR month IN RANGE(24):
        UPDATE_STATE_WITH_MARKET_NOISE(state, assumptions)

        # Agent makes decisions based on current state
        agent_decision = agent.evaluate(state)

        APPLY_AGENT_DECISION_TO_STATE(state, agent_decision)
        timeline.APPEND(CAPTURE_STATE(state))

        IF state.cash_balance < agent.bailout_threshold:
            state.bailout_used = True
            BREAK

        IF state.trigger_refi_conditions_met:
            state.refinanced = True
            BREAK

    RETURN {
        final_balance: state.cash_balance,
        refinanced: state.refinanced,
        bailout_used: state.bailout_used,
        timeline: timeline,
        outcome: DETERMINE_OUTCOME(state)
    }


    }

  # =============================
  # 📋 Phase 4: Greenlight With Conditions
  # =============================
  FUNCTION CreateConditionalMemo(confidence_score, simulation_analysis):
    INIT memo = {}
    memo.confidence_score = confidence_score

    IF confidence_score >= 65 AND simulation_analysis.success_rate > 0.6:
      memo.status = "✅ Proceed"
      memo.conditions = []
    ELSE:
      memo.status = "❌ Do Not Proceed Unless Conditions Met"
      memo.conditions = [
        "Signed contractor quote <$60K",
        "Pre-close zoning permit or holdback",
        "DSCR refi model + rent roll",
        "$25K liquidity buffer",
        "25% tax hike modeled"
      ]

    RETURN memo

  # =============================
  # 🚦 Phase 5: Decision Firewall
  # =============================
  FUNCTION FinalDecisionGate(conditional_memo):
    IF conditional_memo.status == "✅ Proceed":
      TRIGGER_ESCROW_SEQUENCE()
    ELSE:
      BLOCK_EXECUTION()

  # =============================
  # 🔁 Phase 6: Feedback Loop
  # =============================
  FUNCTION LearnFromOutcome(closed_deal):
    UPDATE_PRIORS(closed_deal.outcome_data)
    STORE_TO_MODEL_HISTORY(closed_deal)
