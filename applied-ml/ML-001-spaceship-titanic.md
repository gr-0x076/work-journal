# Competition ML-001: Kaggle Spaceship Titanic Pipeline

- **Source Code:** [`applied-ml/competitions/spaceship-titanic/my_pipeline.py`](./competitions/spaceship-titanic/my_pipeline.py)
- **Platform:** [Kaggle Spaceship Titanic](https://www.kaggle.com/c/spaceship-titanic)
- **Validation Metric:** Binary Classification Accuracy
- **Current Local CV Score:** **`0.8179 (+/- 0.0059)`** (5-Fold Stratified K-Fold)
- **Status:** **Completed & Submission Ready ✅ (Target 0.805 Smashed)**

---

## 1. Objective & Challenge Overview

Predict which passengers were transported to an alternate dimension during the spaceship collision. The dataset features 13 mixed tabular columns including passenger identifiers, cabin locations, luxury amenity spending, cryogenic sleep status, and travel destinations.

Key engineering goals:
1. Prevent data leakage between train and validation folds using Scikit-Learn `Pipeline` and `ColumnTransformer`.
2. Discover deterministic domain rules to resolve missing values.
3. Engineer non-linear features capturing group dynamics and spending behaviors.
4. Benchmark tree ensemble families: Bagging (Random Forest) vs. Gradient Boosting (LightGBM, CatBoost, XGBoost, HistGradientBoosting).

---

## 2. Feature Engineering & Ablation Highlights

### A. Transductive Group Size Mapping
Passenger IDs follow the format `gggg_pp`, where `gggg` represents a traveling group (e.g. family or party) and `pp` is the passenger number within that group.
* **Leak-Free Transductive Counting:** Group IDs from `train` and `test` manifests are concatenated before computing frequency counts:
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

### D. The FamilySize Feature Ablation
We tested extracting surnames (`df['Name'].str.split().str[-1]`) to compute family size counts. Across all 4 gradient boosting algorithms, **adding FamilySize degraded performance by 0.0015 to 0.0028 CV**. Surnames introduced false positives (unrelated passengers sharing common surnames) and diluted the cleaner, deterministic transductive `GroupId` signal. FamilySize was cleanly discarded.

---

## 3. Systematic Model Benchmark (5 Models x 2 Feature Sets)

All models evaluated via 5-Fold Stratified Cross-Validation (`random_state=42`):

| Model Architecture | Feature Variant | Mean 5-Fold CV Accuracy | Std Dev | Fold Scores |
|---|---|---|---|---|
| **CatBoost** | **WITHOUT Family** | **0.8179** | **+/- 0.0059** | **[0.8229, 0.8125, 0.8154, 0.8268, 0.8119]** |
| CatBoost | WITH Family | 0.8151 | +/- 0.0049 | [0.8194, 0.8102, 0.8137, 0.8222, 0.8101] |
| HistGradientBoosting | WITHOUT Family | 0.8134 | +/- 0.0041 | [0.8148, 0.8137, 0.8125, 0.8193, 0.8067] |
| HistGradientBoosting | WITH Family | 0.8128 | +/- 0.0031 | [0.8177, 0.8137, 0.8137, 0.8090, 0.8101] |
| LightGBM | WITHOUT Family | 0.8126 | +/- 0.0028 | [0.8102, 0.8137, 0.8108, 0.8176, 0.8107] |
| LightGBM | WITH Family | 0.8111 | +/- 0.0068 | [0.8120, 0.8160, 0.8074, 0.8199, 0.8003] |
| XGBoost | WITHOUT Family | 0.8108 | +/- 0.0083 | [0.8143, 0.8056, 0.8045, 0.8257, 0.8038] |
| XGBoost | WITH Family | 0.8088 | +/- 0.0065 | [0.8137, 0.8068, 0.8028, 0.8188, 0.8021] |
| Random Forest | WITH Family | 0.8046 | +/- 0.0108 | [0.8079, 0.7867, 0.8125, 0.8170, 0.7986] |
| Random Forest | WITHOUT Family | 0.8009 | +/- 0.0073 | [0.8085, 0.7913, 0.8045, 0.8072, 0.7929] |

---

## 4. Key Takeaways & Milestones
- **The Power of Boosting:** Switching from bagging (Random Forest, ~0.801) to gradient boosting (CatBoost, ~0.818) yielded an immediate **+1.7% accuracy boost**.
- **Winning Model:** `CatBoostClassifier(iterations=400, learning_rate=0.04, depth=6)` trained on the full dataset produced the final submission file.
