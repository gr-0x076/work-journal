# Open-Source Contributions

A log of my contributions to upstream open-source software libraries.

---

### Index

- **[OSS-001: SciPy — Fix `VI` Shape Validation in Mahalanobis Distance](./scipy/OSS-001-mahalanobis-validation.md)**
  - **Issue:** [scipy/scipy#26526](https://github.com/scipy/scipy/issues/26526) | **PR:** [#26540](https://github.com/scipy/scipy/pull/26540)
  - **Status:** Merged into `main` (SciPy 2.0.0)
  - **Summary:** Added shape assertions in `_validate_mahalanobis_kwargs` to prevent segfaults and silent data corruption in compiled C kernels.

- **[OSS-002: statsmodels — Numerical Stability for Zero Counts in Goodness-of-Fit](./statsmodels/OSS-002-zero-counts-gof.md)**
  - **Issue:** [statsmodels/statsmodels#10703](https://github.com/statsmodels/statsmodels/issues/10703) | **PR:** [#10704](https://github.com/statsmodels/statsmodels/pull/10704)
  - **Status:** Merged into `main` (Statsmodels 0.15.1)
  - **Summary:** Handled $0 \ln(0)$ limits gracefully using `scipy.special.xlogy` to prevent `NaN` statistics and runtime warnings in the $G$-test.

- **[OSS-003: SciPy — Fix Out-of-Bounds Memory Read in `ndimage` `NI_FILTER_GOTO`](./scipy/OSS-003-ndimage-filter-bounds.md)**
  - **Issue:** [scipy/scipy#26663](https://github.com/scipy/scipy/issues/26663) | **PR:** [#26674](https://github.com/scipy/scipy/pull/26674)
  - **Status:** Merged into `main` (SciPy 2.0.0)
  - **Summary:** Fixed coordinate offset calculation in the C macro iterator when footprint size exceeds array dimension along an axis, preventing out-of-bounds reads and segfaults.

- **[OSS-004: seaborn — Fix Phantom Points on Duplicate Indices with Missing Data](./seaborn/OSS-004-duplicate-index-nan.md)**
  - **Issue:** [mwaskom/seaborn#4036](https://github.com/mwaskom/seaborn/issues/4036) | **PR:** [#4040](https://github.com/mwaskom/seaborn/pull/4040)
  - **Status:** In Review (Passing all CI checks)
  - **Summary:** Enforced positional integer indexing during coordinate conversion in `VectorPlotter.comp_data` to prevent pandas label alignment from broadcasting points across duplicate index rows with missing values.

- **[OSS-005: SciPy — Prevent Overflow and Underflow in `stats.pmean`](./scipy/OSS-005-pmean-overflow.md)**
  - **Issue:** [scipy/scipy#26854](https://github.com/scipy/scipy/issues/26854) | **PR:** [#26868](https://github.com/scipy/scipy/pull/26868)
  - **Status:** In Review 🚀 (Passing all CI checks)
  - **Summary:** Factored out an extrema scaling factor ($c = \max$ for $p>0$, $c = \min$ for $p<0$) along the reduction axis to guarantee intermediate powers stay in $[0, 1]$ and never overflow or underflow.
