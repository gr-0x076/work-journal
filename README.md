# Work Journal

A minimalist engineering log of my open-source contributions, technical investigations, and systems projects.

---

## Open-Source Contributions

Detailed records of upstream bug fixes, numerical investigations, and code reviews:

| ID | Repository | Area / Topic | Status | Log |
| :--- | :--- | :--- | :---: | :---: |
| **OSS-001** | [`scipy/scipy`](https://github.com/scipy/scipy) | `spatial.distance`: `VI` shape validation in Mahalanobis distance | **Merged** ✅ (SciPy 2.0.0) | [Notes](./open-source/scipy/OSS-001-mahalanobis-validation.md) |
| **OSS-002** | [`statsmodels/statsmodels`](https://github.com/statsmodels/statsmodels) | `stats.gof`: Zero count numerical stability in `powerdiscrepancy` | **Merged** ✅ (Statsmodels 0.15.1) | [Notes](./open-source/statsmodels/OSS-002-zero-counts-gof.md) |
| **OSS-003** | [`scipy/scipy`](https://github.com/scipy/scipy) | `ndimage`: Out-of-bounds filter offset in `NI_FILTER_GOTO` | **Merged** ✅ (SciPy 2.0.0) | [Notes](./open-source/scipy/OSS-003-ndimage-filter-bounds.md) |
| **OSS-004** | [`mwaskom/seaborn`](https://github.com/mwaskom/seaborn) | `_base`: Fix phantom points on duplicate indices with missing data | **In Review** 🚀 ([#4040](https://github.com/mwaskom/seaborn/pull/4040)) | [Notes](./open-source/seaborn/OSS-004-duplicate-index-nan.md) |

---

## Projects

Technical summaries, architecture notes, and retrospectives for primary projects:

| Project | Focus | Implementation Highlights | Notes |
| :--- | :--- | :--- | :---: |
| **[ProofGraph](https://github.com/gr-0x076/proofgraph)** | AI Attribution & Auditing | Headless browser extraction, entity ambiguity gate, discrete evidence tiers | [Notes](./projects/proofgraph.md) |
| **[IncidentLens](https://github.com/gr-0x076/incidentlens)** | SRE Memory Agent | Agent memory integration (Hindsight), Groq inference, structured FastAPI backend | [Notes](./projects/incidentlens.md) |
| **[Pulse Incident Engine](https://github.com/gr-0x076/pulse-incident-engine)** | Real-Time Systems | Finite state machine lifecycle, SHA-256 alert deduplication, WebSockets | [Notes](./projects/pulse-incident-engine.md) |

---

*Maintained by [Mohith GR](https://github.com/gr-0x076)*
