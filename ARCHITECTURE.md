# Architecture

## Overview

This system is an automated **patient simulator** that places outbound phone calls to Pretty Good AI's test line (`+1-805-439-8008`), conducts natural voice conversations, and produces recordings, transcripts, and bug reports.

The architecture has two phases:

1. **Pre-call planning** — An Orchestrator and Scenario Generator (LLM) invent diverse, realistic patient test cases at runtime. No hardcoded dialogue scripts.
2. **Call execution + analysis** — Twilio handles telephony; FastAPI bridges audio to OpenAI Realtime where the Patient Agent speaks; after hangup, Whisper transcribes and an Evaluator LLM checks results against generated success criteria.

Scenarios are **generated, not hardcoded**, but every generated scenario is **saved to disk** before the call so runs are reproducible and bug reports cite a concrete test definition.

---

## System context

```mermaid
flowchart LR
    subgraph System["Patient Voice Bot"]
        ORCH["Orchestrator"]
        GEN["Scenario Generator"]
        RUN["Scenario Runner"]
        API["FastAPI Server"]
        OUT["outputs/"]
    end

    subgraph External["External APIs"]
        TW["Twilio Voice"]
        OAI["OpenAI\nRealtime · Whisper · GPT"]
    end

    PG["Pretty Good AI Agent\n+1-805-439-8008"]

    ORCH --> GEN
    GEN --> RUN
    RUN --> TW
    RUN --> API
    TW <-->|PSTN| PG
    TW <-->|Media Stream| API
    API <-->|Realtime WS| OAI
    GEN --> OAI
    API --> OAI
    API --> OUT
```

---

## Layered architecture

```mermaid
flowchart TB
    subgraph L1["Layer 1 — Test Planning"]
        ORCH["Orchestrator\n(what to test next)"]
        GEN["Scenario Generator LLM\n(who + goal + criteria)"]
        VAL["Scenario Validator\n(schema + retry)"]
        STORE["outputs/callNN/\ncallNN-scenario.json"]
        ORCH --> GEN --> VAL --> STORE
    end

    subgraph L2["Layer 2 — Call Control"]
        RUN["Scenario Runner CLI"]
        TC["Twilio Call Controller"]
        STORE --> RUN --> TC
    end

    subgraph L3["Layer 3 — Real-Time Voice (FastAPI)"]
        WH["Webhooks\n/voice/outbound · /status · /recording"]
        BR["Media Bridge\nmulaw 8kHz ↔ PCM16 24kHz"]
        SM["Session Manager\nstate · events · timeout"]
        PA["Patient Agent\nRealtime system prompt"]
        WH --> BR --> SM --> PA
    end

    subgraph L4["Layer 4 — AI Voice"]
        RT["OpenAI Realtime API\nLLM + TTS + Server VAD"]
        PA <-->|WebSocket| RT
    end

    subgraph L5["Layer 5 — Post-Call Analysis"]
        REC["Twilio Recording"]
        TR["Whisper Transcriber"]
        MERGE["Transcript Merger"]
        EV["Bug Evaluator LLM"]
        ART["outputs/callNN/\nbug_report.md"]
        REC --> TR --> MERGE --> EV --> ART
    end

    TC --> WH
    TC --> REC
    STORE --> EV
    SM --> MERGE
```

---

## LLM roles (four distinct jobs)

| Agent | Model | When | Input | Output |
|-------|-------|------|-------|--------|
| **Orchestrator** | GPT-4o | Before each call | Call history, categories used, prior bugs | `next_category`, hints, avoid list |
| **Scenario Generator** | GPT-4o | Before each call | Orchestrator hints + constraints | Full scenario JSON |
| **Patient Agent** | Realtime API | During call | Generated scenario → system prompt | Spoken patient audio |
| **Bug Evaluator** | GPT-4o | After call | Scenario JSON + transcript | Structured bug findings |

The Patient Agent never sees `success_criteria` during the call — only persona, goal, and behavior — so it cannot game the test.

---

## Call sequence

```mermaid
sequenceDiagram
    autonumber
    participant R as Scenario Runner
    participant O as Orchestrator
    participant G as Scenario Generator
    participant T as Twilio
    participant F as FastAPI
    participant RT as OpenAI Realtime
    participant A as Athena Agent

    R->>O: What should we test next?
    O->>G: category + hints + avoid list
    G->>G: Validate JSON schema
    G->>R: Save outputs/callNN/callNN-scenario.json

    R->>T: Create outbound call (+18054398008)
    T->>A: Connect PSTN
    T->>F: POST /voice/outbound
    F->>T: TwiML Connect Stream
    T->>F: WS /media/{call_id}

    F->>RT: Open session (patient system prompt)
    loop Conversation 1-3 min
        A->>T: Agent speaks
        T->>F: mulaw audio in
        F->>RT: PCM16 audio in
        RT->>F: PCM16 patient audio out
        F->>T: mulaw audio out
        T->>A: Patient speaks
        F->>F: Log session events
    end

    R->>T: Hangup or 180s timeout
    T->>F: recording callback (MP3 URL)
    F->>F: Whisper → merge transcript → Bug Evaluator
    F->>F: Write outputs/callNN/ artifacts + bug_report.md
    R->>O: Update call history for next iteration
```

---

## Post-call pipeline

```mermaid
flowchart LR
    MP3["Twilio MP3"] --> DL["Download to callNN-recording.mp3"]
    DL --> WH["Whisper API"]
    WH --> TXT["callNN-transcript.txt"]
    LOG["callNN-events.json"] --> MERGE["Transcript Merger"]
    TXT --> MERGE
    MERGE --> JSON["callNN-transcript-full.json"]
    JSON --> EV["Bug Evaluator"]
    SCN["callNN-scenario.json\nsuccess_criteria"] --> EV
    EV --> PER["callNN-bugs.md"]
    EV --> BUG["bug_report.md"]
```

**Per-call folder** (`outputs/call01/`, etc.) holds scenario, recording, transcripts, session log, events, and bugs. Root `outputs/bug_report.md` aggregates all calls.

---

## Repository structure

```
PrettyGoodAI_AIEngineeringChallenge/
├── ARCHITECTURE.md
├── README.md
├── .env.example
├── requirements.txt
├── config.py                       # Settings from .env; per-call output paths
├── main.py                         # uvicorn entry
├── runner.py                       # CLI: batch, call, generate, analyze
│
├── app/
│   ├── main.py                     # FastAPI app + /health
│   ├── session_registry.py         # active CallSession lookup
│   └── routes/
│       └── voice.py                # Twilio webhooks + media stream WS
│
├── planning/
│   ├── planner.py                  # orchestrator → generator → save pipeline
│   ├── orchestrator.py             # LLM: pick next test category
│   ├── generator.py                # LLM: create scenario JSON
│   ├── validator.py                # schema check + retry
│   ├── prompts.py                  # orchestrator + generator system prompts
│   ├── llm.py                      # shared OpenAI client
│   └── history.py                  # call_history.json read/write
│
├── telephony/
│   ├── twilio_client.py            # outbound call, status, recording download
│   └── call_service.py             # place call + wait (CLI workflow)
│
├── voice/
│   ├── realtime_bridge.py          # Twilio WS ↔ OpenAI Realtime WS
│   ├── media_bridge.py             # silent/echo debug bridge (Phase 3)
│   ├── audio_utils.py              # mulaw ↔ PCM16 conversion
│   └── turn_state.py               # turn-taking + cooldown state
│
├── patient/
│   ├── models.py                   # Scenario schema + call history models
│   ├── prompt_builder.py           # Realtime patient system prompt
│   └── agent.py                    # re-exports prompt builder helpers
│
├── analysis/
│   ├── pipeline.py                 # post-call orchestration
│   ├── transcriber.py              # Whisper wrapper
│   ├── transcript_merger.py        # merge session turns + Whisper text
│   ├── overlap_detector.py         # turn-timing overlap signals
│   ├── evaluator.py                # bug detection LLM
│   ├── bug_report.py               # format + append bug_report.md
│   └── models.py                   # EvaluationResult, BugFinding
│
├── scenarios/
│   └── seeds/                      # optional hand-written YAML (debug)
│
├── tests/
│   └── test_phase2_offline.py      # offline schema/history tests
│
└── outputs/                        # OUTPUT_DIR (configurable)
    ├── bug_report.md               # aggregated bugs (all calls)
    ├── call_history.json           # run index
    └── callNN/                     # one folder per call (call01, call02, …)
        ├── callNN-scenario.json
        ├── callNN-recording.mp3
        ├── callNN-transcript.txt
        ├── callNN-transcript-full.json
        ├── callNN-session.json
        ├── callNN-events.json
        └── callNN-bugs.md
```

---

## Key design choices

**1. Generated scenarios, not hardcoded scripts.** The Athena agent asks questions in unpredictable order. A Scenario Generator LLM produces diverse test intent; the Realtime Patient Agent adapts at call time. This finds more bugs than fixed YAML dialogue.

**2. Save every generated scenario before calling.** Dynamic generation does not mean non-reproducible runs. Saved JSON links each bug to a concrete test definition — required for a credible bug report.

**3. Orchestrator separate from Generator.** One LLM decides *what category to test*; another invents *the specific patient story*. Separation keeps batch runs diverse (no 10 scheduling calls in a row) and allows adaptive retesting after bugs are found.

**4. Twilio + Realtime for voice; GPT-4o for planning and evaluation.** Realtime API is used only where latency matters (live conversation). Cheaper Chat Completions handle scenario generation and bug analysis — keeps total cost under $20.

**5. Post-call Whisper on Twilio recording.** One transcription pass on the full two-sided MP3. No duplicate real-time transcription. Session event logs supplement speaker labeling.

**6. Local file artifacts, no database.** Each call’s artifacts live in one folder under `outputs/callNN/`; `bug_report.md` and `call_history.json` sit at the output root.

---

## Turn-taking policy

- OpenAI Realtime **server VAD** detects when the Athena agent finishes speaking.
- Default: no barge-in (patient waits for agent) except in `interruption` category scenarios.
- Optional 300–500 ms response delay if pacing feels too fast in early iterations.
- Max call duration: **180 seconds**; patient prompt warns to wrap up at 150 s.

---

## Deployment

| Environment | Role |
|-------------|------|
| Local + ngrok | Development; `PUBLIC_BASE_URL` for Twilio webhooks |
| Render / Fly.io | Stable URL for batch runs of 10+ calls |

**Runtime (batch):**
```bash
# Terminal 1
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2
ngrok http 8000   # set PUBLIC_BASE_URL in .env

# Terminal 3
python runner.py batch --count 12
```

---

## Failure handling

| Failure | Action |
|---------|--------|
| Invalid generated JSON | Retry generator up to 3×; skip category on persistent failure |
| Twilio call failed | Log to call folder events; do not run post-call; retry once |
| WebSocket drop mid-call | Graceful hangup; save partial session log |
| Recording unavailable | Fall back to session event log; flag in metadata |
| Evaluator finds no issues | Still write entry: "No issues detected against criteria" |

---

## Cost controls

| Item | Estimate (12 calls × 2.5 min) |
|------|-------------------------------|
| Twilio outbound | ~$0.50–1.50 |
| OpenAI Realtime | ~$5–10 |
| Whisper (post-call) | ~$1–2 |
| GPT-4o (orchestrator + generator + evaluator × 12) | ~$1–3 |
| **Total** | **~$8–17** |

- Cap calls at 180 s.
- One Realtime session per call; close WebSocket on hangup.
- No real-time + post-call double transcription.

---

## CLI modes

```bash
python runner.py batch --count 12          # generate + call + analyze (submission run)
python runner.py generate --count 5        # preview scenarios without calling
python runner.py call --scenario outputs/call01/call01-scenario.json --analyze
python runner.py analyze --call call-01    # re-run analysis on existing recording
```
