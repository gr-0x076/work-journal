# OSS-003: SciPy — Fix Out-of-Bounds Memory Read in `ndimage` `NI_FILTER_GOTO`

- **Entry ID:** OSS-003
- **Date:** November 13, 2026
- **Category:** Open Source
- **Repository:** [`scipy/scipy`](https://github.com/scipy/scipy)
- **Issue:** [#26663](https://github.com/scipy/scipy/issues/26663)
- **Pull Request:** [#26674](https://github.com/scipy/scipy/pull/26674)
- **Status:** Merged into `main` (SciPy 2.0.0)
- **Reviewed by:** `tylerjereddy` (SciPy Maintainer / Release Manager)

---

## 1. Problem

When applying multi-dimensional morphological operations or filters in `scipy.ndimage` (such as `binary_erosion`, `grey_dilation`, or generic rank filters) using a structuring element (footprint) larger than the input array along a given axis, the underlying C iterator calculated an invalid pointer offset.

This caused:
- Memory reads outside the allocated footprint buffer.
- Inconsistent calculation results depending on memory layout.
- Potential segmentation faults on certain memory boundaries.

---

## 2. Concepts Involved

- **Multi-dimensional Image Processing (`scipy.ndimage`):** Computes neighborhood filters on N-dimensional arrays by traversing coordinate spaces with an internal C iterator (`NI_FilterIterator`).
- **Filter Neighborhood Partitioning:** The iterator divides each 1D coordinate axis into three regions:
  1. Left boundary region (`_pp < b1`), where filter elements extend past the low boundary.
  2. Interior region (`b1 <= _pp <= b2`), where the filter is completely inside the array.
  3. Right boundary region (`_pp > b2`), where filter elements extend past the high boundary.
- **Degenerate Geometries:** When the filter/footprint size is strictly greater than the input array dimension, an interior region cannot physically exist, meaning `b2 < b1`.

---

## 3. Root Cause

In `scipy/ndimage/src/ni_support.h`, the macro `NI_FILTER_GOTO` updates coordinate offsets along axis `_ii`:

```c
#define NI_FILTER_GOTO(_iterator, _offset) \
...
if (_pp < b1) { \
    _jj = _pp; \
} else if (_pp > b2 && b2 >= b1) { \
    _jj = b1 + 1 + _pp - b2; \
} else { \
    _jj = b1; \
}
```

When `b2 < b1` (footprint larger than input) and `_pp >= b1`:
- The first branch `_pp < b1` evaluated to `false`.
- The second branch `(_pp > b2 && b2 >= b1)` evaluated to `false` because `b2 >= b1` is false.
- The macro fell through to `else { _jj = b1; }`.

Assigning `_jj = b1` when `b2 < b1` caused the iterator to set the filter offset past the valid bounds of the filter offsets buffer.

---

## 4. Implementation

Restructured the branch conditions in `scipy/ndimage/src/ni_support.h` so that when no interior region exists (`b2 < b1`), the iterator directly maps `_jj = _pp`:

```c
if (b2 < b1) { \
    _jj = _pp; \
} else if (_pp < b1) { \
    _jj = _pp; \
} else if (_pp > b2) { \
    _jj = b1 + 1 + _pp - b2; \
} else { \
    _jj = b1; \
}
```

This ensures that every coordinate in a degenerate boundary case is mapped correctly without jumping to an out-of-bounds offset.

---

## 5. Verification & Tests

Added a regression test in `scipy/ndimage/tests/test_morphology.py`:
- Configured a 1D/2D array with small dimensions (e.g., shape `(3, 3)`) and a footprint larger than the input (e.g., size 5 or 7).
- Verified that morphological filtering completes cleanly and returns expected binary arrays without segfaults or memory sanitizer warnings.
- Verified test suite pass across all 60 SciPy multi-platform CI runners.

---

## 6. What I Learned

1. **C Macro Debugging in Numerical Libraries:** Complex C macros like `NI_FILTER_GOTO` handle critical hot paths in image filtering. A single boundary flaw in coordinate arithmetic can corrupt calculations silently across all higher-level functions (`ndimage.morphology`, `ndimage.filters`).
2. **Edge Cases in Spatial Algorithms:** Algorithms that partition space into boundary/interior zones must explicitly account for cases where the boundary condition consumes the entire domain.
3. **Core Review Standards:** Having a pull request reviewed and merged by a longtime SciPy release manager (`tylerjereddy`) reinforced the importance of minimal, surgical C patches accompanied by strict regression tests.
