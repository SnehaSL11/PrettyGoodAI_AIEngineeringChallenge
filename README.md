# Pretty Good AI — Patient Voice Bot

Automated patient simulator for the [Pretty Good AI Engineering Challenge](https://prettygoodai.com). The bot places outbound phone calls to the test line (`+1-805-439-8008`), conducts natural voice conversations as a simulated patient, and produces recordings, transcripts, and bug reports.

## What it does

1. **Generates test scenarios** — An LLM orchestrator invents diverse patient personas, goals, behavior rules, and success criteria (no hardcoded dialogue scripts).
2. **Places real phone calls** — Twilio dials the Pretty Good AI agent; our FastAPI server receives the media stream.
3. **Speaks as the patient** — OpenAI Realtime drives the patient voice over the phone, guided by a scenario-specific system prompt.
4. **Analyzes each call** — Whisper transcribes the recording; GPT-4o evaluates the clinic agent against the scenario’s success criteria and writes structured bug findings.

For system design details, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Project structure

```
├── app/              # FastAPI server (Twilio webhooks, media stream WebSocket)
├── planning/         # LLM orchestrator + scenario generator
├── telephony/        # Twilio outbound calls + recording download
├── voice/            # Audio bridge (Twilio mulaw ↔ OpenAI PCM16) + turn-taking
├── patient/          # Realtime patient agent prompt + scenario models
├── analysis/         # Whisper transcription + bug evaluator + overlap detection
├── outputs/          # Per-call folders (call01/, call02/, …) + bug_report.md
├── config.py         # Settings from .env
├── main.py           # Start FastAPI server
└── runner.py         # CLI — generate, call, batch, analyze
```

## Prerequisites

- Python 3.11+
- [Twilio](https://www.twilio.com/) account with a US phone number
- [OpenAI](https://platform.openai.com/) API key with Realtime API access
- [ngrok](https://ngrok.com/) (local development — Twilio needs a public HTTPS webhook URL)

## Setup

### 1. Install dependencies

```bash
cd PrettyGoodAI_AIEngineeringChallenge
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set:

| Variable | Description |
|----------|-------------|
| `TWILIO_ACCOUNT_SID` | Twilio Account SID |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token |
| `TWILIO_PHONE_NUMBER` | Your Twilio number (E.164), used as caller ID |
| `OPENAI_API_KEY` | OpenAI API key |
| `PUBLIC_BASE_URL` | Public HTTPS URL (ngrok URL, no trailing slash) |
| `OUTPUT_DIR` | Root output folder (default: `outputs`) |

`TARGET_PHONE_NUMBER` defaults to `+18054398008` (Pretty Good AI test line).

### 3. Verify configuration

```bash
python runner.py status
```

### 4. Start the server and expose webhooks

**Terminal 1** — FastAPI server:

```bash
python main.py
```

**Terminal 2** — ngrok tunnel:

```bash
ngrok http 8000
```

Copy the ngrok `https://` URL into `PUBLIC_BASE_URL` in `.env`, then **restart** `python main.py` so Twilio webhooks resolve correctly.

Health check:

```bash
curl http://localhost:8000/health
```

## Run

Once setup is complete and both `main.py` and ngrok are running, use a **single command** to generate scenarios, place calls, transcribe recordings, and produce bug reports:

```bash
python runner.py batch --count 12
```

This runs the full pipeline: generate → call → analyze for each scenario. All artifacts are written under `OUTPUT_DIR` (default `outputs/`), one folder per call.

### Other useful commands

```bash
# Generate scenarios only (no phone calls)
python runner.py generate --count 3

# Place one call with post-call analysis
python runner.py call --scenario outputs/call01/call01-scenario.json --analyze

# Re-run analysis on an existing recording
python runner.py analyze --call call-01

# Analyze all completed calls that have recordings
python runner.py analyze --all
```

## Outputs

Each call gets its own folder under `OUTPUT_DIR`. Call IDs like `call-01` map to folder names like `call01` (no hyphen).

```
outputs/
├── bug_report.md              # Aggregated bugs across all analyzed calls
├── call_history.json          # Index of generated and completed calls
├── call01/
│   ├── call01-scenario.json       # Patient persona, goal, success criteria
│   ├── call01-recording.mp3       # Twilio call recording
│   ├── call01-transcript.txt      # Readable transcript (turns + Whisper)
│   ├── call01-transcript-full.json
│   ├── call01-session.json        # Session metadata
│   ├── call01-events.json         # Twilio + bridge event log
│   └── call01-bugs.md             # Bug findings for this call
├── call02/
│   └── ...
└── call29/
    └── ...
```

| File | Description |
|------|-------------|
| `callNN-scenario.json` | Scenario definition saved before the call runs |
| `callNN-recording.mp3` | MP3 recording downloaded after hangup |
| `callNN-transcript.txt` | Speaker-labeled turns merged with Whisper text |
| `callNN-transcript-full.json` | Structured transcript JSON |
| `callNN-session.json` | Call metadata (Twilio SID, scenario path, bridge mode) |
| `callNN-events.json` | Real-time event log from the voice bridge |
| `callNN-bugs.md` | Per-call bug report from the GPT evaluator |
| `bug_report.md` | Combined markdown report (all calls) |
| `call_history.json` | Run index with status, timestamps, and bug counts |

Nothing is split across separate `scenarios/`, `recordings/`, `transcripts/`, or `logs/` folders — everything for a call lives in that call’s folder.

> **Note:** `output_old_trials/` contains all earlier trial runs (flat layout and per-call copies) and remains **valid to review** for recordings, transcripts, and bug reports.

## How the voice pipeline works

1. `runner.py` tells Twilio to dial the target number.
2. Twilio hits `/voice/outbound` on the FastAPI server and opens a bidirectional media stream.
3. `voice/realtime_bridge.py` connects that stream to OpenAI Realtime.
4. `patient/prompt_builder.py` builds the patient system prompt from the scenario JSON.
5. Audio flows both ways: clinic agent speech → OpenAI (patient listens), patient speech → Twilio (clinic agent hears).
6. On hangup, Twilio posts the recording URL; `analysis/pipeline.py` transcribes, evaluates, and writes results into `outputs/callNN/` plus the root `bug_report.md`.

Turn-taking is controlled in `voice/turn_state.py` and `voice/realtime_bridge.py` (server VAD, agent cooldown, playback hold) to reduce the patient talking over the clinic agent.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Call connects but patient is silent | Check OpenAI API quota; confirm Realtime API access on your key |
| Twilio webhook errors | Ensure `PUBLIC_BASE_URL` matches ngrok and the server was restarted after updating `.env` |
| `429 insufficient_quota` | Add billing/credits at [platform.openai.com/account/billing](https://platform.openai.com/account/billing) |
| Recording missing after call | Wait a few seconds; Twilio posts the recording URL asynchronously |

## License

Assessment submission for Pretty Good AI Engineering Challenge.
