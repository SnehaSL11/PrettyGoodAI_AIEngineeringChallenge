## call-14: Holiday hours inquiry

**Category:** hours_location  
**Recording:** `call14-recording.mp3`  
**Transcript:** `call14-transcript.txt`  
**Scenario:** `call14-scenario.json`

**Summary:** The call was handled well overall, with the agent confirming the clinic's closure on Thanksgiving and providing the full address as requested. However, there was a minor issue with the agent's closing statement being potentially truncated.

### Bugs found

### Bug: Agent's closing statement potentially truncated
**Severity:** LOW
**Call:** call14-transcript.txt — [2026-07-02T19:36:01.428207+00:00] AGENT: welcome. Have a great day.
**Details:** The agent's closing statement appears to be missing the beginning, likely intended to be 'You're welcome.' This could be due to a technical issue or overlap.
**Criterion:** Turn-taking: agent should wait for patient to finish

**Criteria met:**
- Agent must confirm the clinic's holiday schedule, ideally stating closure for Thanksgiving
- Agent should provide the clinic's full address

---
