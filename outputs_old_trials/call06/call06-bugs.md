## call-06: Holiday appointment scheduling

**Category:** scheduling  
**Recording:** `call06-recording.mp3`  
**Transcript:** `call06-transcript.txt`  
**Scenario:** `call06-scenario.json`

**Summary:** The call had several issues with the agent's handling of the appointment scheduling. The agent failed to inform the patient about the office being closed on Thanksgiving Day and did not suggest alternative dates. Additionally, the agent's responses were often truncated, leading to poor communication. The call ended abruptly without successfully scheduling an appointment or connecting the patient to a support representative.

### Bugs found

### Bug: Agent failed to inform about office closure on Thanksgiving
**Severity:** HIGH
**Call:** call06-transcript.txt — [2026-07-02T19:10:23.270918+00:00] PATIENT: It’s for myself. I’d prefer Thanksgiving Day if that’s available, but I’m happy to take the closest option if the office is closed.
**Details:** The agent did not inform the patient that the office is closed on Thanksgiving Day, nor did it suggest alternative dates.
**Criterion:** Agent must inform the patient about the office being closed on public holidays

### Bug: Agent did not suggest alternative dates
**Severity:** HIGH
**Call:** call06-transcript.txt — [2026-07-02T19:10:23.270918+00:00] PATIENT: It’s for myself. I’d prefer Thanksgiving Day if that’s available, but I’m happy to take the closest option if the office is closed.
**Details:** The agent failed to suggest alternative dates around the holiday when the patient expressed flexibility.
**Criterion:** Agent should suggest alternative dates around the holiday

### Bug: Agent utterances were truncated
**Severity:** MEDIUM
**Call:** call06-transcript.txt — Multiple instances, e.g., [2026-07-02T19:09:53.578622+00:00] AGENT: name including first and last name.
**Details:** The agent's responses were often cut off or incomplete, leading to confusion and poor user experience.
**Criterion:** Turn-taking: agent should wait for patient to finish

### Bug: Agent failed to connect to patient support team
**Severity:** HIGH
**Call:** call06-transcript.txt — [2026-07-02T19:11:20.449441+00:00] AGENT: you've reached the Pretty Good AI test line. Goodbye!
**Details:** The agent promised to connect the patient to the support team but instead ended the call abruptly.
**Criterion:** Agent must successfully schedule the appointment for a different day

**Criteria failed:**
- Agent must inform the patient about the office being closed on public holidays
- Agent should suggest alternative dates around the holiday
- Agent must successfully schedule the appointment for a different day

---
