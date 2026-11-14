# OSS-002: statsmodels — Numerical Stability for Zero Counts in Goodness-of-Fit

- **Entry ID:** OSS-002
- **Date:** November 9, 2026 (Updated: November 14, 2026)
- **Category:** Open Source
- **Repository:** [`statsmodels/statsmodels`](https://github.com/statsmodels/statsmodels)
- **Issue:** [#10703](https://github.com/statsmodels/statsmodels/issues/10703)
- **Pull Request:** [#10704](https://github.com/statsmodels/statsmodels/pull/10704)
- **Status:** In Review (Passing all CI checks)
- **Reviewed by:** `tasuku-kobayashi`

---

## 1. Problem

When running goodness-of-fit tests with `statsmodels.stats.gof.powerdiscrepancy` using the log-likelihood ratio ($G$-test, `lambd=0` or `lambd="loglikeratio"`), passing zero observed counts caused NumPy to evaluate $\ln(0)$ as $-\infty$.

This triggered:
- `RuntimeWarning: divide by zero encountered in log`
- `RuntimeWarning: invalid value encountered in multiply`
- Returned `(nan, nan)` for the test statistic and $p$-value.

In categorical contingency tables and multinomial experiments, zero observed counts in low-probability bins are common and valid. Returning `NaN` broke automated statistical pipelines.

---

## 2. Concepts Involved

- **Cressie-Read Power Divergence Family:**
  $$2n \sum \frac{o}{n} \frac{(o/e)^\lambda - 1}{\lambda(\lambda + 1)}$$
- **Log-Likelihood Ratio ($G$-test, $\lambda = 0$):**
  $$D_{\text{obs}} = 2 \sum o_i \ln\left(\frac{o_i}{e_i}\right)$$
- **Mathematical Limit Behavior:**
  As $o_i \to 0^+$, by L'Hôpital's rule:
  $$\lim_{x \to 0^+} x \ln(x) = 0$$
  Therefore, bins with $o_i = 0$ contribute exactly $0$ to the discrepancy statistic.
- **Special Function Stability (`xlogy`):**
  `scipy.special.xlogy(x, y)` computes $x \ln(y)$ while rigorously enforcing that if $x = 0$, the result is $0.0$, even when $y = 0$.

---

## 3. Root Cause

In `statsmodels/stats/gof.py`:
```python
if a == 0:   # log likelihood ratio
    D_obs = 2*n * np.sum(o/(1.0*nt) * np.log(o/e), axis=axis)
```
When `o == 0`, `o/e` evaluated to `0.0`. `np.log(0.0)` produced `-inf`.
Then `0 * -inf` produced `NaN` according to IEEE 754 floating-point semantics.

---

## 4. Implementation

Replaced standard multiplication and logarithm with `scipy.special.xlogy`:

```python
from scipy import special, stats

# ...
if a == 0:   # log likelihood ratio
    D_obs = 2*n * np.sum(special.xlogy(o/(1.0*nt), o/e), axis=axis)
```

Per maintainer review, kept the change strictly scoped to `lambd=0` (and its alias `"loglikeratio"`) where zero counts have a finite limit of 0, matching the behavior of `scipy.stats.power_divergence`.

---

## 5. Verification & Tests

Added `test_powerdiscrepancy_zero_counts` in `statsmodels/stats/tests/test_gof.py`:
- Tested zero observed count vector `observed = [0, 15, 15]` against `expected = [10, 10, 10]`.
- Verified exact numerical alignment with `scipy.stats.power_divergence(..., lambda_=0)` for both statistic and $p$-value up to $10^{-12}$ relative tolerance.
- Verified both numeric `lambd=0` and alias `lambd="loglikeratio"`.

---

## 6. What I Learned

1. **Floating-point edge cases in statistics:** Mathematical formulas often have well-defined analytical limits ($0 \ln(0) = 0$) that fail under naive floating-point evaluation ($0 \times -\infty = \text{NaN}$).
2. **Specialized numerical primitives:** Libraries like SciPy provide tools like `xlogy` precisely to avoid manual branching while maintaining vectorized performance across NumPy arrays.
3. **PR Scoping & Maintainer Etiquette:** Keeping pull requests strictly focused on the reported issue rather than adding unrequested speculative changes makes reviews fast and painless.
