# Project: Pulse — Incident Triage & Response Engine

- **Repository:** [`gr-0x076/pulse-incident-engine`](https://github.com/gr-0x076/pulse-incident-engine)
- **Deployment:** Live on Vercel / Render
- **Technologies:** Node.js, Express, React 18, MongoDB, Socket.IO, TanStack Query, Tailwind CSS
- **Status:** Completed & Deployed

---

## 1. Objective

Engineering incident management requires coordination between on-call responders, automated monitoring systems, and leadership. Ad-hoc tracking in chat channels leads to duplicate efforts and missed SLAs.

Pulse is a centralized incident command center engineered for deterministic lifecycle transitions, alert deduplication, and real-time state synchronization across responders.

---

## 2. Core Technical Components

```text
Monitoring Webhooks / Alerts
              │
              ▼
    SHA-256 Alert Deduplication Gate
              │
              ▼
    Deterministic State Machine (FSM)
    [OPEN] ──> [INVESTIGATING] ──> [IDENTIFIED] ──> [MONITORING] ──> [RESOLVED]
              │
              ▼
    Real-Time Broadcast (Socket.IO) ──> TanStack Query Frontend Cache
```

1. **Deterministic Lifecycle Transitions:** Enforces explicit state changes via a finite state machine. Incidents cannot jump directly from `OPEN` to `RESOLVED` without entering an active investigation state.
2. **SHA-256 Alert Deduplication:** Computes hashes over incoming alert payloads (service, error code, affected endpoint) within a sliding time window to collapse alert storms into a single actionable incident.
3. **Real-Time Synchronization:** Uses Socket.IO rooms to push state changes, timeline notes, and escalation events to connected responders without client polling.
4. **Role-Based Access Control (RBAC):** Restricts high-impact actions (escalation, post-mortem publishing) to designated roles (Admin, Incident Commander, Responder, Viewer).

---

## 3. Verification & Live Access

- **Live Deployment:** Hosted and operational on Vercel (frontend) and Render (backend).
- **Role Verification:** Configured with test accounts for each RBAC tier to verify permission boundaries.
