# Engineering Projects

Architectural summaries, implementation details, and retrospectives for primary projects.

---

### Index

- **[ProofGraph — AI Citation & Source Attribution Auditor](./proofgraph.md)**
  - **Focus:** LLM hallucination auditing, entity resolution, web extraction.
  - **Stack:** Python, Playwright/Chromium, NetworkX.
  - **Summary:** Audits LLM-generated claims against cited URLs by extracting source paragraphs, verifying entity alignment, and assigning discrete evidence tiers.

- **[IncidentLens — SRE Post-Mortem Memory Agent](./incidentlens.md)**
  - **Focus:** Agent memory, incident troubleshooting, FastAPI.
  - **Stack:** Python, FastAPI, Hindsight, Groq API.
  - **Summary:** Memory-augmented triage service that indexes past incident post-mortems to provide context-aware troubleshooting advice for active outages.

- **[Pulse Incident Engine — Real-Time Incident Response Platform](./pulse-incident-engine.md)**
  - **Focus:** Real-time state machines, alert deduplication, full-stack systems.
  - **Stack:** Node.js, Express, React, MongoDB, Socket.IO, TanStack Query.
  - **Summary:** Operational command center for incident triage featuring deterministic FSM lifecycle transitions and SHA-256 alert deduplication.
