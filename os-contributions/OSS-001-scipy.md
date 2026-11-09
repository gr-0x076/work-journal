# OSS-001: SciPy — Fix `VI` Shape Validation in Mahalanobis Distance

- **Entry ID:** OSS-001
- **Date:** October 28, 2026
- **Category:** Open Source
- **Repository:** [`scipy/scipy`](https://github.com/scipy/scipy)
- **Issue:** [#26526](https://github.com/scipy/scipy/issues/26526)
- **Pull Request:** [#26540](https://github.com/scipy/scipy/pull/26540)
- **Status:** Merged into `main` (Milestone: SciPy 2.0.0)
- **Reviewed by:** `j-bowhay` (SciPy Maintainer)

---

## 1. Problem

When using `scipy.spatial.distance.pdist` or `cdist` with `metric='mahalanobis'`, the caller can pass an inverse covariance matrix `VI`.

If `VI` had mismatched dimensions:
- An undersized `VI` (e.g. A scalar or smaller matrix) caused a **Segmentation Fault** (exit code 139) because the underlying C kernel read past the allocated buffer.
- A mismatched 2D matrix (e.g. Shape $(4, 4)$ for 2D points) computed silently without errors, producing mathematically garbage results.

While the single-pair function `mahalanobis(u, v, VI)` validated that `VI.shape == (n, n)`, the vectorized `pdist` and `cdist` functions skipped this check.

---

## 2. Concepts Involved

- **Mahalanobis Distance:** $D(u, v) = \sqrt{(u - v)^T V^{-1} (u - v)}$. For points in $\mathbb{R}^n$, the inverse covariance matrix $V^{-1}$ must be square with shape $(n, n)$.
- **Python / C Boundary:** Python validates types and arguments before passing raw pointers (`double*`) into compiled C extensions (`scipy/spatial/src/distance.c`). If Python doesn't check array bounds, the C kernel performs out-of-bounds pointer arithmetic.

---

## 3. Root Cause

In [`scipy/spatial/distance/_distance.py`](https://github.com/scipy/scipy/blob/main/scipy/spatial/distance/_distance.py), the helper `_validate_mahalanobis_kwargs` converted `VI` to `float64` via `_convert_to_double(VI)`, but never asserted that `kwargs["VI"].shape == (n, n)`.

---

## 4. Implementation

Added an explicit shape check in `_validate_mahalanobis_kwargs` before arguments are dispatched to the C kernel:

```python
kwargs["VI"] = _convert_to_double(VI)
if kwargs["VI"].shape != (n, n):
    raise ValueError(
        f"The inverse covariance matrix VI must have shape ({n}, {n}); "
        f"got {kwargs['VI'].shape}."
    )
return kwargs
```

This enforces fail-fast error reporting and protects both `pdist` and `cdist` at a single entry point.

---

## 5. Verification & Tests

Added regression tests to `scipy/spatial/distance/tests/test_distance.py`:
- In `TestCdist.test_cdist_mahalanobis`: Assert that passing a $(4, 4)$ `VI` for 2D inputs or a scalar `VI=1.0` raises `ValueError` with the expected shape message.
- In `TestPdist.test_pdist_mahalanobis`: Same assertions for pairwise distances.

Ran `pytest scipy/spatial/distance/tests/test_distance.py` — all passed cleanly.

---

## 6. What I Learned

1. **Memory Safety at Language Boundaries:** Python protects against memory corruption, but the moment data crosses into C/C++ extensions via pointers, bounds validation is entirely up to Python input validators.
2. **Silent Corruption vs Crashes:** Silent arithmetic errors are often worse than crashes because they go unnoticed in scientific workflows.
3. **Open-Source PR Governance:** SciPy strictly requires an `#### AI Generation Disclosure` in the PR body. My first PR (#26532) was closed for missing it; adding the disclosure and amending the commit SHA allowed PR #26540 to pass CI and get merged.
