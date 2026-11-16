# OSS-004: seaborn — Fix Phantom Points on Duplicate Indices with Missing Data

- **Entry ID:** OSS-004
- **Date:** November 16, 2026
- **Category:** Open Source
- **Repository:** [`mwaskom/seaborn`](https://github.com/mwaskom/seaborn)
- **Issue:** [#4036](https://github.com/mwaskom/seaborn/issues/4036)
- **Pull Request:** [#4040](https://github.com/mwaskom/seaborn/pull/4040)
- **Status:** In Review 🚀 (Passing all CI checks)
- **Reviewed by:** Pending maintainer review

---

## 1. Problem

When using `seaborn.scatterplot` (or other relational plotters based on `VectorPlotter`) on a pandas DataFrame with duplicate index labels where some rows contained missing values (`NaN`/`None`), Seaborn plotted phantom data points.

Missing coordinate values in one row were silently filled from other rows sharing the same index label, fabricating data points that did not exist in the original input data.

---

## 2. Concepts Involved

- **Pandas Index Alignment vs. Positional Placement:**
  Pandas aligns values by index label rather than physical row position during Series insertion or assignment into a DataFrame. If an index contains duplicate labels, inserting a shorter Series broadcasts values across all rows that share that label.
- **Coordinate Conversion & Missing Data Handling:**
  Seaborn drops missing values per converter group (`orig.dropna()`) before passing data to unit converters and transformations, ensuring invalid values do not break transformation functions.
- **Defensive Positional Re-indexing (`pd.RangeIndex`):**
  Temporarily assigning a unique 0-indexed integer range (`pd.RangeIndex(len(df))`) forces pandas to align values strictly by row position rather than index labels, restoring the original index once assembly is complete.

---

## 3. Root Cause

In `seaborn/_base.py` (`VectorPlotter.comp_data`):
```python
parts = []
grouped = self.plot_data[var].groupby(self.converters[var], sort=False)
for converter, orig in grouped:
    orig = orig.mask(orig.isin([np.inf, -np.inf]), np.nan)
    orig = orig.dropna()
    ...
    parts.append(pd.Series(transform(comp), orig.index, name=orig.name))
if parts:
    comp_col = pd.concat(parts)
...
comp_data.insert(0, var, comp_col)
```

Because `orig.dropna()` removes missing entries, `comp_col` contains fewer rows than `comp_data` when missing values exist. When `comp_data.insert(0, var, comp_col)` is executed:
- If `comp_data` has unique indices, pandas fills missing rows with `NaN`.
- If `comp_data` has duplicate index labels, pandas matches by label and broadcasts surviving values across all rows sharing that label, inventing points for rows where the coordinate was actually missing.

---

## 4. Implementation

In `seaborn/_base.py`:
1. Preserved `orig_index = comp_data.index`.
2. Temporarily assigned unique integer indices `pd.RangeIndex(len(comp_data))` to `comp_data`, `col`, and `converters` prior to grouping and coordinate transformation.
3. Because the grouped slices (`orig`) retain the unique positional index, `comp_col` concatenates with unique integer positions.
4. During `comp_data.insert(0, var, comp_col)`, pandas aligns strictly by row position. Rows with dropped NaNs are accurately populated with `NaN`.
5. Restored `comp_data.index = orig_index` upon completion so downstream user code sees the original DataFrame index.

---

## 5. Verification & Tests

Added regression test `test_scatterplot_duplicate_index_with_na` in `tests/test_relational.py`:
- Constructed a DataFrame with duplicate index labels (`[0, 0, 1, 1]`) and missing values in specific rows.
- Verified that `scatterplot` renders only the authentic coordinate pairs without fabricating markers from duplicate-indexed sibling rows.
- Verified test suite passes:
  - `pytest tests/test_relational.py` (121 passed, 0 failed).
  - `pytest tests/test_base.py` (165 passed, 0 failed).

---

## 6. What I Learned

1. **The Danger of Non-Unique Index Labels in Pandas:** Duplicate indices make index-based alignment ambiguous. Any operation that shrinks a Series (like `dropna()`) and tries to insert it back into a DataFrame with duplicate labels will broadcast values unexpectedly.
2. **Positional Isolation Pattern:** When transforming columns elementwise with intermediate filtering, always operate on a positional index (`RangeIndex` or `reset_index`) to preserve row identity, and restore the user's index at the exit boundary.
3. **Transparent AI Collaboration:** Followed upstream contribution norms by providing a clear AI disclosure in the PR description, transparently detailing tool usage and human verification.
