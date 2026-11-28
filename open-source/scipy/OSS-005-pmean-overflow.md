# OSS-005: SciPy — Prevent Overflow and Underflow in `stats.pmean`

- **Entry ID:** OSS-005
- **Date:** November 28, 2026
- **Category:** Open Source
- **Repository:** [`scipy/scipy`](https://github.com/scipy/scipy)
- **Issue:** [#26854](https://github.com/scipy/scipy/issues/26854)
- **Pull Request:** [#26868](https://github.com/scipy/scipy/pull/26868)
- **Status:** In Review 🚀 (Passing all CI checks)

---

## 1. Problem

`scipy.stats.pmean` calculates the generalized (Hölder / power) mean:

$$M_p(x) = \left( \frac{1}{n} \sum_{i=1}^n x_i^p \right)^{1/p}$$

The previous implementation computed intermediate powers directly:

```python
return _xp_mean(a**float(p), axis=axis, weights=weights)**(1/p)
```

When $|p|$ is moderately large (e.g., $p = 600$) or when values in $a$ are large (e.g., $x \sim 10^{200}$ for $p = 2$), the intermediate term $a^p$ overflows IEEE 754 float64 ($> 1.79 \times 10^{308}$) to `inf`, or underflows to `0.0` (for large negative powers), returning `inf` or `0.0` even though the true mathematical power mean is well within standard floating-point range:

```python
stats.pmean([1, 2, 4], 600)      # Returned: inf (Expected: ~3.9927)
stats.pmean([100., 200.], 150)   # Returned: inf (Expected: ~199.078)
stats.pmean([1e200, 2e200], 2)   # Returned: inf (Expected: ~1.5811e200)
stats.pmean([1e-3, 2e-3], -150)  # Returned: 0.0 (Expected: ~1.0046e-3)
```

---

## 2. Mathematical Concept & Solution

By the homogeneity of degree 1 of the power mean:

$$M_p(c \cdot x) = c \cdot M_p(x) \iff M_p(x) = c \cdot M_p\left( \frac{x}{c} \right)$$

for any positive scalar $c > 0$.

We choose the scaling factor $c$ based on the sign of $p$:
1. **For $p > 0$**: Let $c = \max(x)$ along the reduction axis.
   - For all elements, $0 \le x_i / c \le 1$.
   - Consequently, $(x_i / c)^p \in [0, 1]$ can **never overflow**, and the maximum term is exactly $1^p = 1$.
2. **For $p < 0$**: Let $c = \min(x)$ along the reduction axis.
   - For all positive elements, $x_i / c \ge 1$.
   - Consequently, $(x_i / c)^p = (x_i / c)^{-|p|} \in (0, 1]$ can **never overflow**, and the minimum term is exactly $1^p = 1$.
3. **Restoration**: Multiply the reduced result by $c$.

---

## 3. Implementation

In `scipy/stats/_stats_py.py`:

```python
with np.errstate(divide='ignore', invalid='ignore'):
    if p > 0:
        c = xp.max(a, axis=axis)
        c_keepdims = xp.max(a, axis=axis, keepdims=True)
    else:
        c = xp.min(a, axis=axis)
        c_keepdims = xp.min(a, axis=axis, keepdims=True)

    finite_nonzero = xp.isfinite(c_keepdims) & (c_keepdims != 0)
    scale = xp.where(finite_nonzero, c_keepdims, xp.ones_like(c_keepdims))

    scaled_a = a / scale
    return c * (_xp_mean(scaled_a**float(p), axis=axis, weights=weights)**(1/p))
```

Edge cases handled:
- $c = 0$ (all elements zero for $p > 0$, or at least one zero for $p < 0$): avoids division by zero, returns `0.0`.
- $c = \infty$: avoids $\infty / \infty$, returns `inf`.
- Preserves full compatibility with the Python Array API standard (`xp`) and masked array wrappers.

---

## 4. Verification

Added regression tests to `TestPMean` in `scipy/stats/tests/test_stats.py`:
- 1D scalar and weighted arrays with large $|p|$ and large magnitudes compared against high-precision `mpmath` ground truth.
- 2D multi-axis reductions (`axis=0`, `axis=1`, `axis=None`).
- All 28 `TestPMean` tests and 23 `test_axis_nan_policy` tests pass clean.
