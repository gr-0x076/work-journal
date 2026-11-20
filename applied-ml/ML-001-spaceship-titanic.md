# Competition ML-001: Kaggle Spaceship Titanic Pipeline

- **Source Code:** [`applied-ml/competitions/spaceship-titanic/my_pipeline.py`](./competitions/spaceship-titanic/my_pipeline.py)
- **Platform:** [Kaggle Spaceship Titanic](https://www.kaggle.com/c/spaceship-titanic)
- **Validation Metric:** Binary Classification Accuracy
- **Current Local CV Score:** **`0.8011 (+/- 0.0089)`** (5-Fold Stratified K-Fold)
- **Status:** **Active 🔨 (Target: CV > 0.805)**

---

## 1. Objective & Challenge Overview

Predict which passengers were transported to an alternate dimension during the spaceship collision. The dataset features 13 mixed tabular columns including passenger identifiers, cabin locations, luxury amenity spending, cryogenic sleep status, and travel destinations.

Key engineering goals:
1. Prevent data leakage between train and validation folds using Scikit-Learn `Pipeline` and `ColumnTransformer`.
2. Discover deterministic domain rules to resolve missing values.
3. Engineer non-linear features capturing group dynamics and spending behaviors.

---

## 2. Feature Engineering Highlights

### A. Transductive Group Size Mapping
Passenger IDs follow the format `gggg_pp`, where `gggg` represents a traveling group (e.g. family or party) and `pp` is the passenger number within that group.
* **Leak-Free Transductive Counting:** To capture true group sizes without target leakage, group IDs from `train` and `test` manifests are concatenated before computing frequency counts:
  ```python
  all_passengers = pd.concat([train_raw['PassengerId'], test_raw['PassengerId']], ignore_index=True)
  group_size_map = all_passengers.str.split('_').str[0].value_counts()
  df['GroupSize'] = df['GroupId'].map(group_size_map)
  df['IsAlone'] = (df['GroupSize'] == 1).astype(int)
  ```

### B. CryoSleep Structural Invariant
Exploratory data analysis revealed that passengers in cryogenic sleep (`CryoSleep = True`) strictly cannot spend money on amenities (`RoomService`, `FoodCourt`, `ShoppingMall`, `Spa`, `VRDeck`):
* $\text{TotalSpend} > 0 \implies \text{CryoSleep} = \text{False}$
* $\text{TotalSpend} = 0 \land \text{CryoSleep is NaN} \implies \text{CryoSleep} = \text{True}$ (imputed with high empirical certainty)

### C. Luxury Spending Ratios & Deck-Side Interactions
* **Spending Ratios:** Proportional spending across individual amenities relative to total spend:
  $$\text{Amenity\_Ratio} = \frac{\text{Amenity}}{\text{TotalSpend} + 1}$$
* **Binary Zero-Spend Flag:** `NoSpend = (TotalSpend == 0).astype(int)`
* **Deck-Side Interaction:** Capturing localized hull damage patterns:
  $$\text{Deck\_Side} = \text{Deck} + \text{'_'} + \text{Side}$$

---

## 3. Local Cross-Validation Progression

All experiments are evaluated using 5-Fold Stratified Cross-Validation (`random_state=42`):

| Iteration | Pipeline & Features | Local CV Accuracy | Std Dev | Notes |
|---|---|---|---|---|
| **Baseline 1** | Logistic Regression (Basic Preprocessing) | 0.7911 | +/- 0.0099 | Linear baseline |
| **Baseline 2** | Random Forest (Raw Features + Basic Deck/Side) | 0.7979 | +/- 0.0092 | Tree baseline |
| **Iteration 3** | Random Forest + Binary `NoSpend` Indicator | 0.7982 | +/- 0.0112 | Student in driver's seat |
| **Iteration 4** | Transductive `GroupSize` + Spending Ratios + `Deck_Side` | **0.8011** | **+/- 0.0089** | **Broke 0.80 barrier; CV variance dropped** |

Fold scores on current best pipeline:
```text
Fold 0: 0.8074
Fold 1: 0.7890
Fold 2: 0.8074
Fold 3: 0.8101
Fold 4: 0.7917
Mean CV: 0.8011 | Std: 0.0089
```

---

## 4. Next Engineering Steps
- Replace Random Forest with Gradient Boosted Decision Trees (`HistGradientBoostingClassifier`, `LightGBM`, `CatBoost`).
- Out-of-fold probability blending and threshold calibration to break **0.805+**.
