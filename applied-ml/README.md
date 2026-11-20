# Applied Machine Learning & First-Principles Engineering

A technical repository of from-scratch mathematical derivations, competitive ML pipelines, and production data science systems.

---

## Directory Structure

```text
applied-ml/
├── drills/
│   └── drill_01_linear_regression.py     # Pure NumPy Normal Equations & Vectorized GD
├── competitions/
│   └── spaceship-titanic/
│       └── my_pipeline.py                # Leak-free ColumnTransformer & Stratified CV (0.8011)
├── DRL-001-linear-regression.md          # Technical notes & verification benchmarks
└── ML-001-spaceship-titanic.md           # Domain feature engineering & CV logs
```

---

## Core Focus Areas

1. **First-Principles Implementations:** Implementing core algorithms from raw NumPy (normal equations, SVD/PCA, coordinate descent, backpropagation) and verifying convergence against analytical solutions and reference libraries.
2. **Competitive Modeling & Leak-Free Rigor:** Developing disciplined validation schemes (Stratified K-Fold, Group K-Fold), transductive manifest mapping, and modern gradient boosting (LightGBM, CatBoost) on competitive platforms (Kaggle).
3. **Reproducibility:** Pinned seeds, modular `Pipeline` structures, and strict separation between train and evaluation splits.
