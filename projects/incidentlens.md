# Project: IncidentLens — SRE Post-Mortem Memory Agent

- **Repository:** [`gr-0x076/incidentlens`](https://github.com/gr-0x076/incidentlens)
- **Technologies:** Python 3.10+, FastAPI, Hindsight (Agent Memory), Groq API, pytest
- **Status:** Functional Prototype

---

## 1. Objective

During active production incidents, on-call engineers often repeat failed mitigation steps because past incident post-mortems and tribal knowledge are trapped in disparate documents or chat logs.

IncidentLens provides a memory-augmented SRE copilot that indexes historical incident post-mortems and queries them in real time to recommend proven mitigation pathways.

---

## 2. Architecture & Implementation

```text
Incident Stack Trace / Symptoms
              │
              ▼
    FastAPI Ingestion Endpoint
              │
              ▼
   Hindsight Memory Retrieval
   (Searches historical post-mortems & past mitigation attempts)
              │
              ▼
   Groq LPU Inference (LLM reasoning grounded in historical incident context)
              │
              ▼
   Grounded Triage Recommendations + Past Failure Warnings
```

1. **Persistent Incident Memory (Hindsight):** Rather than standard naive vector chunking, IncidentLens utilizes Hindsight's structured memory model to associate root causes with specific past remediations and known failure modes.
2. **Low-Latency LLM Inference:** Queries the Groq API for rapid inference during time-sensitive incident triage.
3. **Structured API:** Built as a standard FastAPI microservice with defined request/response Pydantic schemas.

---

## 3. Verification & Limitations

- **Testing:** Unit tests in `tests/` validating memory ingestion, query parsing, and API endpoints.
- **Documented Limitations (`LIMITATIONS.md`):**
  - **Cold Start:** The system requires a corpus of documented historical incidents before its recommendations become reliable.
  - **Environment Drift:** Remediations from six months ago may fail if upstream architecture or dependencies have changed.
