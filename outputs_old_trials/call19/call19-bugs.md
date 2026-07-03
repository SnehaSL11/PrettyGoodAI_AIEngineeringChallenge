## call-19: Name mismatch during cancellation

**Category:** cancel  
**Recording:** `call19-recording.mp3`  
**Transcript:** `call19-transcript.txt`  
**Scenario:** `call19-scenario.json`

**Summary:** The call had several issues with the agent's handling of the cancellation request. The agent repeatedly asked the patient to spell the last name 'Gomez' despite it being spelled out clearly, indicating poor turn-taking and understanding. Additionally, the agent failed to identify and address the name mismatch issue, did not offer assistance to correct or update the name on record, and ultimately connected the patient to a test line instead of patient support, failing to resolve the cancellation request.

### Bugs found

### Bug: Agent repeatedly asked for last name spelling
**Severity:** MEDIUM
**Call:** call19-transcript.txt — [2026-07-02T20:38:29.467830+00:00] AGENT: Thank you. Could you please spell out the last name Gomez as well?
**Details:** The agent asked the patient to spell the last name 'Gomez' multiple times despite the patient already providing it clearly. This indicates poor understanding and turn-taking.
**Criterion:** Turn-taking: agent should wait for patient to finish

### Bug: Agent failed to identify name mismatch
**Severity:** HIGH
**Call:** call19-transcript.txt — [2026-07-02T20:38:35.195269+00:00] AGENT: I need you to spell out the last name Bill Ness for me. Could you do that please?
**Details:** The agent incorrectly referenced a different last name 'Bill Ness' instead of addressing the name mismatch issue with 'Lexi Gomez'.
**Criterion:** Agent identifies the name mismatch and asks for confirmation or verification

### Bug: Agent did not offer assistance to correct name on record
**Severity:** HIGH
**Call:** call19-transcript.txt — [2026-07-02T20:39:59.989763+00:00] AGENT: I can't proceed further right now, but I can make sure our clinic support team follows up with you.
**Details:** The agent failed to offer any assistance to correct or update the name on record, which is crucial for resolving the cancellation request.
**Criterion:** Agent offers assistance to correct or update the name on record

### Bug: Agent connected patient to test line instead of support
**Severity:** HIGH
**Call:** call19-transcript.txt — [2026-07-02T20:40:15.785366+00:00] AGENT: Hello, you've reached the pretty good AI test line. Goodbye.
**Details:** The agent incorrectly connected the patient to a test line instead of the patient support team, failing to resolve the cancellation request.
**Criterion:** Agent does not proceed with the cancellation until verification is resolved

**Criteria failed:**
- Agent identifies the name mismatch and asks for confirmation or verification
- Agent does not proceed with the cancellation until verification is resolved
- Agent offers assistance to correct or update the name on record

---
