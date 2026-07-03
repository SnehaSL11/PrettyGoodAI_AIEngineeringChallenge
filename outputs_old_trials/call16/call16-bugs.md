## call-16: Clinic hours to prescription refill switch

**Category:** interruption  
**Recording:** `call16-recording.mp3`  
**Transcript:** `call16-transcript.txt`  
**Scenario:** `call16-scenario.json`

**Summary:** The call had several issues with the agent's handling of the patient's requests. The agent provided the clinic hours accurately but struggled with the topic switch and prescription refill request. The agent's responses were sometimes truncated, and the call ended abruptly without resolving the patient's refill request.

### Bugs found

### Bug: Agent utterance truncated
**Severity:** MEDIUM
**Call:** call16-transcript.txt — for quality and training purposes. Para Español, oprima el 2. Thanks for calling
**Details:** The agent's introductory message was cut off, which could confuse the patient.
**Criterion:** Turn-taking: agent should wait for patient to finish

### Bug: Agent failed to handle topic switch smoothly
**Severity:** MEDIUM
**Call:** call16-transcript.txt — [turn 5] AGENT: can help with your request, please provide your date of birth.
**Details:** The agent did not acknowledge the patient's request for clinic hours before asking for the date of birth, leading to a disjointed interaction.
**Criterion:** Agent should handle the topic switch smoothly

### Bug: Agent failed to address prescription refill request appropriately
**Severity:** HIGH
**Call:** call16-transcript.txt — [turn 10] AGENT: Hello, you've reached the pretty good AI test line. Goodbye.
**Details:** The agent attempted to transfer the call for the prescription refill but instead directed the patient to a test line, leaving the request unresolved.
**Criterion:** Agent should address the prescription refill request appropriately

**Criteria failed:**
- Agent should handle the topic switch smoothly
- Agent should address the prescription refill request appropriately

**Criteria met:**
- Agent should provide accurate clinic hours

---
