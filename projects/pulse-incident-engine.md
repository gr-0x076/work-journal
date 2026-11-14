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
    SHA-256 Fingerprint Deduplication Gate
              │
              ▼
    Deterministic Finite State Machine (FSM)
    [FIRED] ──> [ACKNOWLEDGED] ──> [INVESTIGATING] ──> [MITIGATED] ──> [RESOLVED] ──> [CLOSED]
       │                               ▲                     
       └──────────────> [ESCALATED] ───┘
              │
              ▼
    Real-Time Broadcast (Socket.IO) ──> TanStack Query Frontend Cache
```

1. **Deterministic Lifecycle Transitions (`constants.js`):** Enforces strict state transitions via `VALID_TRANSITIONS` and `TRANSITION_GUARDS`. An incident cannot transition arbitrarily; for instance, transitioning to `MITIGATED` requires a `mitigationSummary`, and transitioning to `RESOLVED` enforces `rootCauseCategory` and `rootCauseDescription`.
2. **SHA-256 Alert Deduplication (`webhook.service.js`):** Computes a SHA-256 hash across `source`, normalized `service`, and `title`. If an active incident matching this fingerprint is currently in an unclosed state (`FIRED`, `ACKNOWLEDGED`, `INVESTIGATING`, `ESCALATED`), the incoming alert is linked to the existing incident rather than spawning duplicate tickets.
3. **Real-Time Synchronization:** Uses Socket.IO organization rooms to push state changes, timeline notes, and escalation events to connected responders without client polling.
4. **Role-Based Access Control (RBAC):** Restricts high-impact actions (escalation, post-mortem publishing) to designated roles (`ADMIN`, `INCIDENT_COMMANDER`, `RESPONDER`, `VIEWER`).

---

## 3. Verification & Live Access

- **Live Deployment:** Hosted and operational on Vercel (frontend) and Render (backend).
- **Role Verification:** Configured with test accounts for each RBAC tier to verify permission boundaries.
