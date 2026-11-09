# Open-Source Contributions

This directory documents my contributions to major upstream open-source software libraries. Each entry contains a complete technical case study detailing:
- The underlying mathematics and systems concepts
- Root cause analysis of bugs
- Architectural trade-offs and implementation choices
- Test design and regression suites
- Upstream review feedback, governance policies, and lessons learned

---

## 📜 Contribution Log

### 1. SciPy — Mahalanobis Metric Inverse Covariance Shape Validation
- **Repository:** [`scipy/scipy`](https://github.com/scipy/scipy)
- **Status:** **Merged** (PR [#26540](https://github.com/scipy/scipy/pull/26540))
- **Milestone:** SciPy 2.0.0
- **Summary:** Fixed buffer over-read (segmentation fault) and silent arithmetic corruption in compiled C distance kernels by strictly validating the covariance matrix shape $(n, n)$ against observation dimensionality.
- **Deep Dive:** [Read Case Study](./01-scipy-mahalanobis-vi-shape-validation.md)

---

### 2. statsmodels — Numerical Limit Handling for Zero Counts in Goodness-of-Fit Tests
- **Repository:** [`statsmodels/statsmodels`](https://github.com/statsmodels/statsmodels)
- **Status:** **In Review** (PR [#10704](https://github.com/statsmodels/statsmodels/pull/10704))
- **Summary:** Fixed numerical instability where empty observation categories in multinomial data produced `RuntimeWarning: divide by zero encountered in log` and `NaN` test statistics in the $G$-test by replacing naive multiplication with `scipy.special.xlogy`.
- **Deep Dive:** *(Coming upon PR merge)*
