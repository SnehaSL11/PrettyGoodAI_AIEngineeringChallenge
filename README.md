# Pretty Good AI — Patient Voice Bot

Automated patient simulator that calls the Pretty Good AI test line (`+1-805-439-8008`), runs natural voice conversations, and produces recordings, transcripts, and bug reports.

See [ARCHITECTURE.md](ARCHITECTURE.md) for system design.

## Project structure

```
PrettyGoodAI_AIEngineeringChallenge/
├── app/                  # FastAPI server (webhooks, media stream)
├── planning/             # LLM orchestrator + scenario generator
├── telephony/            # Twilio outbound calls + recording
├── voice/                # Audio bridge (mulaw ↔ PCM16)
├── patient/              # Realtime patient agent + models
├── analysis/             # Whisper transcription + bug evaluator
├── scenarios/seeds/      # Optional debug scenarios only
├── outputs/              # Recordings, transcripts, bug reports
├── config.py             # Settings from .env
├── main.py               # Start FastAPI server
└── runner.py             # CLI for batch/single calls
```

## Setup

### 1. Prerequisites

- Python 3.11+
- [Twilio](https://www.twilio.com/) account with a US phone number
- [OpenAI](https://platform.openai.com/) API key with Realtime API access
- [ngrok](https://ngrok.com/) (for local webhook testing)

### 2. Install dependencies

```bash
cd PrettyGoodAI_AIEngineeringChallenge
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in:

| Variable | Description |
|----------|-------------|
| `TWILIO_ACCOUNT_SID` | From Twilio console |
| `TWILIO_AUTH_TOKEN` | From Twilio console |
| `TWILIO_PHONE_NUMBER` | Your Twilio number (E.164) — used as caller ID |
| `OPENAI_API_KEY` | OpenAI API key |
| `PUBLIC_BASE_URL` | ngrok HTTPS URL (no trailing slash) |

### 4. Verify setup

```bash
# Check config loads (requires .env filled in)
python runner.py status

# Start server
python main.py

# In another terminal, expose webhooks
ngrok http 8000
# Copy the https URL into PUBLIC_BASE_URL in .env, restart server

# Health check
curl http://localhost:8000/health
```

## Run (coming in later phases)

```bash
# Batch: generate scenarios + call + analyze
python runner.py batch --count 12

# Preview generated scenarios without calling
python runner.py generate --count 5

# Single call from saved scenario
python runner.py call --scenario outputs/scenarios/call-01.json
```

## Implementation status

| Phase | Status | Contents |
|-------|--------|----------|
| 1 | Done | Config, .gitignore, folder structure, health endpoint |
| 2 | Pending | Orchestrator, scenario generator, validator |
| 3 | Pending | Twilio webhooks + media stream (no Realtime yet) |
| 4 | Pending | OpenAI Realtime patient agent + audio bridge |
| 5 | Pending | Post-call transcription + bug evaluator |
| 6 | Pending | Full `runner.py batch` integration |

## Submission artifacts

After a full batch run, `outputs/` will contain:

- `recordings/call-NN.mp3` — full call audio
- `transcripts/call-NN.txt` — Whisper transcript
- `scenarios/call-NN.json` — generated test scenario
- `bug_report.md` — issues found

## Security

- Never commit `.env` — it is in `.gitignore`
- Only call `+1-805-439-8008` (enforced in code)
