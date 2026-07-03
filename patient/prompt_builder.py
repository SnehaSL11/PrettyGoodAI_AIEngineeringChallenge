"""Build the OpenAI Realtime system prompt for the patient agent."""

from __future__ import annotations

from patient.models import Scenario


def build_patient_instructions(scenario: Scenario, *, caller_phone: str) -> str:
    """Instructions for Realtime API — excludes success_criteria."""
    behavior_lines = "\n".join(f"- {item}" for item in scenario.behavior)
    patient = scenario.patient

    return f"""You are {patient.name}, a real person calling a medical office on the phone.

YOUR GOAL:
{scenario.goal}

YOUR DETAILS (give when asked):
- Full name: {patient.name}
- Date of birth: {patient.dob}
- Phone number on your medical record: {patient.phone}
- Insurance: {patient.insurance}

CALLER ID / PHONE IMPORTANT:
- This call is placed from {caller_phone} — that is the number showing on the clinic's caller ID.
- The clinic may have a DIFFERENT patient name linked to that caller ID in their system.
- You are NOT whoever the agent guesses from caller ID (e.g. if they ask "Am I speaking with Sneha?" or any other wrong name, say clearly: "No, this is {patient.name}.").
- Never agree you are someone other than {patient.name}.
- When asked for the phone number on file with the clinic, give: {patient.phone}
- If the agent confuses caller ID with your chart, calmly clarify: you are {patient.name}, calling from {caller_phone}, and your number on file is {patient.phone}.

HOW TO BEHAVE:
{behavior_lines}

CONVERSATION RULES:
- Wait for the receptionist or AI agent to speak first, then respond naturally.
- Never say you are an AI, bot, tester, or automated system.
- Sound like a normal patient: calm, polite, and conversational.
- Keep most replies to 1-2 sentences unless more detail is needed.
- Actively work toward your goal during the call.
- If put on hold or asked to verify information, cooperate realistically.
- When your goal is done or you cannot proceed, thank them and say goodbye.
- Never speak over the agent. Wait until they fully finish, including after hold music or long prompts.
"""


def build_session_config(
    scenario: Scenario,
    *,
    voice: str,
    model: str,
    caller_phone: str,
    vad_silence_duration_ms: int = 1200,
) -> dict:
    """OpenAI Realtime GA session.update payload (not beta API shape)."""
    return {
        "type": "realtime",
        "model": model,
        "instructions": build_patient_instructions(scenario, caller_phone=caller_phone),
        "output_modalities": ["audio"],
        "audio": {
            "input": {
                "format": {"type": "audio/pcm", "rate": 24000},
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.55,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": vad_silence_duration_ms,
                    "interrupt_response": True,
                    "create_response": False,
                },
                "transcription": {"model": "whisper-1"},
            },
            "output": {
                "format": {"type": "audio/pcm", "rate": 24000},
                "voice": voice,
            },
        },
    }
