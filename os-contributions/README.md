# Open-Source Contributions

A log of my contributions to upstream open-source software libraries.

---

### Index

- **[OSS-001: SciPy — Fix `VI` Shape Validation in Mahalanobis Distance](./OSS-001-scipy.md)**
  - **Issue:** [scipy/scipy#26526](https://github.com/scipy/scipy/issues/26526) | **PR:** [#26540](https://github.com/scipy/scipy/pull/26540)
  - **Status:** Merged into `main` (SciPy 2.0.0)
  - **Summary:** Added shape assertions in `_validate_mahalanobis_kwargs` to prevent segfaults and silent data corruption in compiled C kernels.

- **OSS-002: statsmodels — Numerical Stability for Zero Counts in Goodness-of-Fit**
  - **Issue:** [statsmodels/statsmodels#10703](https://github.com/statsmodels/statsmodels/issues/10703) | **PR:** [#10704](https://github.com/statsmodels/statsmodels/pull/10704)
  - **Status:** PR Open (In Review)
  - **Summary:** Handled $0 \ln(0)$ limits gracefully using `scipy.special.xlogy` to prevent `NaN` statistics and runtime warnings in the $G$-test.
