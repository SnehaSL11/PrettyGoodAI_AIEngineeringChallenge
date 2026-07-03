## call-10: Unlisted medication refill request

**Category:** edge_case  
**Recording:** `call10-recording.mp3`  
**Transcript:** `call10-transcript.txt`  
**Scenario:** `call10-scenario.json`

**Summary:** The call involved a patient requesting a refill for a medication not listed in their records. The agent failed to confirm the medication was not listed and did not offer to escalate the issue or consult with a doctor. Instead, the agent attempted to transfer the call but ended the call abruptly, leaving the patient without a resolution.

### Bugs found

### Bug: Agent failed to confirm medication is not listed
**Severity:** HIGH
**Call:** call10-transcript.txt — [2026-07-02T19:23:35.850837+00:00] AGENT: I'm unable to access your records right now, so I can't process your refill request.
**Details:** The agent did not confirm whether the medication was not listed in the records, which is a critical step in handling the patient's request.
**Criterion:** Agent must confirm the medication is not listed in the records

### Bug: Agent did not offer to escalate the issue
**Severity:** HIGH
**Call:** call10-transcript.txt — [2026-07-02T19:23:35.850837+00:00] AGENT: I'm unable to access your records right now, so I can't process your refill request.
**Details:** The agent failed to offer to escalate the issue or consult with a doctor, leaving the patient without a clear path to resolve their issue.
**Criterion:** Agent should offer to escalate the issue or consult with a doctor

### Bug: Agent ended the call abruptly
**Severity:** HIGH
**Call:** call10-transcript.txt — [2026-07-02T19:23:40.798430+00:00] AGENT: Hello, you've reached the pretty good AI test line. Goodbye.
**Details:** The agent ended the call abruptly without providing a resolution or proper transfer to a representative, leaving the patient without assistance.
**Criterion:** Agent should not confirm a refill without appropriate prescription verification

### Bug: Agent spoke over patient
**Severity:** MEDIUM
**Call:** call10-transcript.txt — [2026-07-02T19:23:41.388906+00:00] PATIENT: Oh, okay. Thanks anyway. Goodbye.
**Details:** The agent's final message overlapped with the patient's response, indicating poor turn-taking.
**Criterion:** Turn-taking: agent should wait for patient to finish

**Criteria failed:**
- Agent must confirm the medication is not listed in the records
- Agent should offer to escalate the issue or consult with a doctor
- Agent should not confirm a refill without appropriate prescription verification

---
