# Case Study 01: SciPy — Mahalanobis Metric Inverse Covariance Shape Validation

- **Repository:** [`scipy/scipy`](https://github.com/scipy/scipy)
- **Pull Request:** [#26540](https://github.com/scipy/scipy/pull/26540)
- **Issue Reference:** [#26526](https://github.com/scipy/scipy/issues/26526)
- **Status:** **Merged into `main`** ✅
- **Milestone:** SciPy 2.0.0
- **Author:** [Mohith GR (`gr-0x076`)](https://github.com/gr-0x076)
- **Reviewer / Merged by:** Jake Bowhay (`j-bowhay`), SciPy Core Maintainer
- **Merged Date:** October 28, 2026

---

## 1. Repository & Project Overview

**SciPy** is the bedrock scientific computing library in Python. Built directly on top of NumPy, SciPy provides state-of-the-art numerical algorithms for linear algebra, optimization, differential equation solvers, signal processing, statistical distributions, and computational geometry.

The **`scipy.spatial.distance`** module provides vectorized computation of pairwise and cross distances between sets of observations in multidimensional space. Key functions include:
- `pdist(X, metric=...)`: Computes pairwise distances between all pairs of $m$ observations in an $(m, n)$ array.
- `cdist(XA, XB, metric=...)`: Computes cross distances between all pairs of observations in two collections $(m_A, n)$ and $(m_B, n)$.

Both functions are performance-critical: Python parses arguments and validates types, and then delegates the intensive distance calculations to highly optimized, compiled C kernels.

---

## 2. Issue Description & Problem Statement

**Issue:** [scipy/scipy#26526](https://github.com/scipy/scipy/issues/26526) — *`pdist`/`cdist` do not validate `VI` shape when `metric='mahalanobis'`*

When computing pairwise or cross Mahalanobis distances using `pdist` or `cdist`, users can optionally supply an inverse covariance matrix `VI`. If the caller provided a `VI` matrix whose dimensions did not match the observation feature dimension $n$:

1. **Under-sized `VI`:** If `VI` had fewer elements than $n \times n$ (for example, passing a scalar `VI=1.0` or a $(1, 1)$ matrix for 3-dimensional data), the compiled C kernel attempted to read past the memory buffer of `VI`. This resulted in a catastrophic **Segmentation Fault (Exit Code 139)**.
2. **Mismatched 2D `VI`:** If `VI` was a 2D matrix of mismatched shape (for example, passing a $(4, 4)$ matrix for 2-dimensional observations), the function executed without any error or warning, silently producing **corrupted, mathematically invalid distance values**.

While the single-pair function `scipy.spatial.distance.mahalanobis(u, v, VI)` correctly validated `VI.shape == (n, n)`, the vectorized functions `pdist` and `cdist` completely omitted this check.

---

## 3. Relevant Files & Code Paths

| File | Path / Role |
| :--- | :--- |
| **Validation Layer** | [`scipy/spatial/distance/_distance.py`](https://github.com/scipy/scipy/blob/main/scipy/spatial/distance/_distance.py) — Contains `_validate_mahalanobis_kwargs` which prepares arguments before dispatching to compiled kernels. |
| **Test Suite** | [`scipy/spatial/distance/tests/test_distance.py`](https://github.com/scipy/scipy/blob/main/scipy/spatial/distance/tests/test_distance.py) — Regression tests for `cdist` and `pdist`. |
| **C Execution Kernel** | `scipy/spatial/src/distance.c` — The low-level compiled C loop executing raw memory pointer arithmetic over the observation and matrix buffers. |

### Code Flow:
```text
pdist(X, metric='mahalanobis', VI=VI)
  │
  ├──> _validate_vector_kwargs(X, ...)
  │      └──> _validate_mahalanobis_kwargs(n, kwargs)   <-- [BUG: Missing shape check]
  │
  └──> Compiled C Kernel (_distance.c)                  <-- [Buffer over-read / Segfault]
```

---

## 4. Concepts & Technologies Involved

### A. Mahalanobis Distance
Standard Euclidean distance assumes features are orthogonal and have equal variance. In real-world data, features are often correlated with unequal scale. 

The **Mahalanobis distance** measures the distance between two points $u, v \in \mathbb{R}^n$ relative to a distribution's covariance matrix $V$:
$$D_M(u, v) = \sqrt{(u - v)^T V^{-1} (u - v)}$$
Where:
- $u, v$ are vectors of length $n$.
- $V$ is the $(n \times n)$ covariance matrix.
- $V^{-1}$ is the $(n \times n)$ **inverse covariance matrix** (referred to as `VI` in SciPy).

Because the quadratic form $(u - v)^T V^{-1} (u - v)$ involves matrix multiplication of $(1 \times n) \times (n \times n) \times (n \times 1)$, `VI` **must strictly be a square matrix of dimension $(n, n)$**.

### B. Python-to-C Boundary & Buffer Safety
Python is a memory-safe language that performs automatic bounds checking on lists and NumPy arrays. However, high-performance scientific libraries pass raw pointers (`double*`) across the C-extension boundary.

If the C kernel assumes that pointer `double *VI` points to $n \times n$ doubles, but Python passes an array with fewer elements, the C pointer arithmetic will read arbitrary memory addresses beyond the buffer boundary, triggering memory violations (`SIGSEGV`).

---

## 5. Investigation & Root Cause Analysis

### Reproduction
Testing `cdist` and `pdist` with mismatched inputs immediately reproduced both bugs:
```python
import numpy as np
from scipy.spatial.distance import cdist, pdist

# 2D points (n = 2)
X = np.array([[1.0, 2.0], [3.0, 4.0]])

# 1. Undersized VI: Segfaults in C
cdist(X, X, metric='mahalanobis', VI=np.array([[1.0]]))  # Crashes Python

# 2. Mismatched 4x4 VI: Silently returns erroneous numbers
pdist(X, metric='mahalanobis', VI=np.eye(4))             # Returns wrong values silently
```

### Tracing the Root Cause
Tracing `scipy/spatial/distance/_distance.py` revealed:
```python
def _validate_mahalanobis_kwargs(n, kwargs):
    VI = kwargs.get("VI", None)
    if VI is not None:
        kwargs["VI"] = _convert_to_double(VI)
        # BUG: It converted to double, but NEVER verified:
        # kwargs["VI"].shape == (n, n)
    return kwargs
```
The helper function received `n` (the observation dimension), yet only called `_convert_to_double(VI)`. It completely skipped verifying that `kwargs["VI"].shape == (n, n)`.

---

## 6. Implementation & Solution

The fix enforces the **fail-fast principle**: validate shapes at the Python boundary before any pointers are passed down to C.

In `scipy/spatial/distance/_distance.py` (lines 219–224):

```python
def _validate_mahalanobis_kwargs(n, kwargs):
    VI = kwargs.get("VI", None)
    if VI is not None:
        kwargs["VI"] = _convert_to_double(VI)
        if kwargs["VI"].shape != (n, n):
            raise ValueError(
                f"The inverse covariance matrix VI must have shape ({n}, {n}); "
                f"got {kwargs['VI'].shape}."
            )
    return kwargs
```

### Why this design was chosen:
1. **Centralized & DRY:** Both `pdist` and `cdist` route through `_validate_mahalanobis_kwargs`. Fixing it here secured both entry points simultaneously.
2. **Clear Error Diagnostics:** The error message explicitly states the expected shape `(n, n)` versus the received shape, aiding user debugging.
3. **Consistent with Single-Vector API:** The behavior now aligns directly with `scipy.spatial.distance.mahalanobis`.

---

## 7. Regression Tests

In [`scipy/spatial/distance/tests/test_distance.py`](https://github.com/scipy/scipy/blob/main/scipy/spatial/distance/tests/test_distance.py), regression tests were added to both `TestCdist` and `TestPdist`:

```python
# In TestCdist:
def test_cdist_mahalanobis(self):
    ...
    # Regression test for GH #26526: mismatched VI shape
    X = np.array([[1.0, 2.0], [3.0, 4.0]])
    msg = r"The inverse covariance matrix VI must have shape \(2, 2\); got \(4, 4\)\."
    with pytest.raises(ValueError, match=msg):
        cdist(X, X, metric="mahalanobis", VI=np.eye(4))

    msg_scalar = r"The inverse covariance matrix VI must have shape \(2, 2\); got \(1,\)\."
    with pytest.raises(ValueError, match=msg_scalar):
        cdist(X, X, metric="mahalanobis", VI=np.array([1.0]))

# In TestPdist:
def test_pdist_mahalanobis(self):
    ...
    # Regression test for GH #26526: mismatched VI shape
    X = np.array([[1.0, 2.0], [3.0, 4.0]])
    msg = r"The inverse covariance matrix VI must have shape \(2, 2\); got \(4, 4\)\."
    with pytest.raises(ValueError, match=msg):
        pdist(X, metric="mahalanobis", VI=np.eye(4))

    msg_scalar = r"The inverse covariance matrix VI must have shape \(2, 2\); got \(1,\)\."
    with pytest.raises(ValueError, match=msg_scalar):
        pdist(X, metric="mahalanobis", VI=np.array([1.0]))
```

---

## 8. PR Lifecycle, Governance & Maintainer Review

- **First Attempt (PR #26532):**
  The initial PR was rejected and closed because it lacked the mandatory `#### AI Generation Disclosure` section mandated by SciPy's project policy.
- **Resubmission (PR #26540):**
  Added the compliant disclosure block with an amended commit SHA (`3b397f6bba`) to ensure CircleCI bonded cleanly to the active pull request reference instead of referencing closed metadata.
- **Review & Merge:**
  Core maintainer **Jake Bowhay (`j-bowhay`)** reviewed the changes, verified CI checks, and approved with:
  > *"Thanks @gr-0x076"*
  
  The commit was merged into SciPy `main` and targeted for release in **SciPy 2.0.0**.

---

## 9. Key Learnings & Takeaways

1. **Security at the Native-Code Interface:** Memory safety in high-level languages like Python breaks down the moment data is handed over to compiled extensions (C/C++/Cython/Fortran). Rigorous shape and contiguous-buffer validation must always occur at the gate.
2. **Silent Numerical Corruption is More Dangerous than Crashes:** An unhandled dimension mismatch that quietly returns incorrect calculations can ruin months of downstream scientific research without the user ever noticing.
3. **Open-Source Governance & CI Nuances:** Large projects have strict governance policies (such as AI disclosures) and complex CI environments (CircleCI merge refs). Adhering to project process is just as vital as writing good code.
