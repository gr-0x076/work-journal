# Project: ProofGraph — AI Citation & Source Attribution Auditor

- **Repository:** [`gr-0x076/proofgraph`](https://github.com/gr-0x076/proofgraph)
- **Role:** Co-developer (Team AltF4)
- **Technologies:** Python 3.10+, Playwright/Chromium, NetworkX, pytest
- **Status:** Completed / Stable

---

## 1. Objective

Large Language Models (LLMs) frequently attach web citations to factual claims. However, up to 30% of cited links fail verification: the URL may be valid, but the target page does not state the claimed fact, or contradicts it (citation hallucination).

ProofGraph was built to independently audit citations by fetching target URLs, checking entity alignment, and evaluating whether cited text genuinely supports the claim.

---

## 2. Architecture & Pipeline

```text
Claim + Cited URL
      │
      ▼
1. Web Extraction (Playwright / Chromium headless browser)
      │
      ▼
2. Entity Ambiguity Gate (Mononym & underspecified entity detection)
      │
      ▼
3. Context Alignment & Overlap Gate (Filters unrelated page sections)
      │
      ▼
4. Categorical Evidence Tier Assignment
   (STRONG | MODERATE | WEAK | UNDERSPECIFIED | CONFLICTING)
```

1. **Web Extraction:** Renders the cited URL via a headless browser to retrieve full dynamic content (bypassing simple JS-rendered scrapers) and extracts clean markdown paragraphs.
2. **Entity Ambiguity Gate:** Detects isolated common given names (e.g., "Peter", "William") lacking distinguishing titles or surnames. Flags them as `ENTITY_UNDERSPECIFIED` rather than misattributing claims to unrelated public figures.
3. **Context Alignment Gate:** Uses source-entity overlap checks to eliminate distractor paragraphs and ensure the evaluation runs against relevant page sections.
4. **Discrete Evaluation Tiers:** Avoids arbitrary percentage confidence scores (e.g. `67.5%`) in favor of discrete qualitative tiers: `STRONG`, `MODERATE`, `WEAK`, `UNDERSPECIFIED`, and `CONFLICTING`.

---

## 3. Verification & Testing

- **Automated Tests:** Comprehensive unit test suite in `tests/` covering entity ambiguity gating, URL rendering, and tier classification (`pytest`).
- **Evaluation Scripts:** `evaluate.py` and `evaluate_live.py` run automated sweeps against benchmark claim/citation pairs.
- **Reproducibility:** Pinned dependencies managed via `requirements-lock.txt`.

---

## 4. Engineering Tradeoffs & Limitations

- **Headless Browser Overhead:** Rendering dynamic pages with Chromium adds latency (~1–3s per URL) compared to raw HTTP GET requests, but is necessary for single-page applications (SPAs).
- **Paywalls & Cloudflare:** URLs behind aggressive bot detection or paywalls cannot be fetched without session credentials.
