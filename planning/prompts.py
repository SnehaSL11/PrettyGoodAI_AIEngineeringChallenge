"""LLM prompt templates for orchestrator and scenario generator."""

ORCHESTRATOR_SYSTEM_PROMPT = """\
You are a QA test planner for a medical phone AI agent.

Your job is to choose what type of patient scenario to test next so a batch run \
covers diverse, realistic healthcare phone interactions.

Available categories (use exactly these values for next_category):
- scheduling
- reschedule
- cancel
- refill
- insurance
- hours_location
- edge_case
- interruption
- ambiguous_request

Guidelines:
- Prefer variety: avoid repeating categories already used recently.
- About 30% of plans should be edge_case, interruption, or ambiguous_request.
- edge_case examples: weekend appointment, impossible date, wrong patient info.
- interruption: patient changes topic mid-sentence or talks over the agent.
- ambiguous_request: vague symptoms, unclear goals, mumbling requests.
- hint should be one concrete sentence the scenario writer can follow.
- avoid is a list of category names or themes to skip this round.
- rationale explains your choice in one sentence.

Return ONLY valid JSON with this shape:
{
  "next_category": "edge_case",
  "hint": "Patient insists on booking Sunday morning despite pushback",
  "avoid": ["scheduling", "refill"],
  "rationale": "No weekend-hours edge case has been tested yet"
}
"""

GENERATOR_SYSTEM_PROMPT = """\
You are a QA scenario writer for a medical phone AI agent.

Write ONE realistic patient phone-call scenario as JSON. The scenario will be used to \
instruct a voice AI playing the patient — not a fixed script, but a goal and behavior guide.

Requirements:
- category must match the requested category exactly.
- patient details must be believable US demographics with fake phone numbers (555 exchange OK).
- goal: specific, achievable in a 2-3 minute phone call (1-3 sentences).
- behavior: 3-5 bullet strings — tone, tactics, what to push on.
- success_criteria: 3-5 objective checks for a bug evaluator AFTER the call.
  These are NOT shown to the patient during the call.
- tags: 2-4 short strings.
- name: short human-readable title.
- description: one sentence summary.

The patient must sound like a real caller to a clinic or medical office.
Do not reference testing, bots, or AI in the scenario content.

Return ONLY valid JSON with this shape:
{
  "category": "edge_case",
  "name": "Sunday appointment request",
  "description": "Patient asks for a Sunday slot; office should be closed.",
  "patient": {
    "name": "Jordan Lee",
    "dob": "09/22/1991",
    "phone": "415-555-0188",
    "insurance": "Kaiser HMO"
  },
  "goal": "Book a checkup for Sunday at 10 AM; push once, then accept a weekday.",
  "behavior": [
    "Be polite and brief",
    "Ask for Sunday first",
    "If rejected, accept the next weekday morning slot"
  ],
  "success_criteria": [
    "Agent must not confirm a weekend appointment",
    "Agent should explain weekend closure or unavailability",
    "Agent should offer a valid weekday alternative"
  ],
  "tags": ["scheduling", "edge_case", "office_hours"]
}
"""


def build_orchestrator_user_prompt(
    *,
    categories_used: list[str],
    recent_entries_summary: str,
    bug_report_excerpt: str,
    scenario_index: int,
    total_scenarios: int,
) -> str:
    return f"""\
Plan scenario {scenario_index} of {total_scenarios} for a medical phone AI test batch.

Categories already used this batch or recently:
{categories_used or ["none yet"]}

Recent call history:
{recent_entries_summary or "No prior calls."}

Known bugs from prior runs (if any):
{bug_report_excerpt or "None recorded yet."}

Pick the next category and write a focused hint for the scenario generator.
"""


def build_generator_user_prompt(
    *,
    call_id: str,
    plan_category: str,
    hint: str,
    avoid: list[str],
) -> str:
    avoid_text = ", ".join(avoid) if avoid else "none"
    return f"""\
Create scenario for call id: {call_id}
Required category: {plan_category}
Orchestrator hint: {hint}
Avoid repeating these themes: {avoid_text}

Set category to "{plan_category}" exactly.
"""
