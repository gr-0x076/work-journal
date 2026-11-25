import os
import pandas as pd
import numpy as np

from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import StratifiedKFold, cross_val_score

# ==========================================
# 1. LOAD DATA
# ==========================================
DATA_DIR = "/home/mohith/.gemini/antigravity/scratch/ai-ml-training-system/competitions/spaceship-titanic/data"
train_raw = pd.read_csv(os.path.join(DATA_DIR, "train.csv"))
test_raw = pd.read_csv(os.path.join(DATA_DIR, "test.csv"))

# ==========================================
# 2. GLOBAL TRANSDUCTIVE GROUP MAPPING
# ==========================================
all_passengers = pd.concat([train_raw['PassengerId'], test_raw['PassengerId']], ignore_index=True)
all_groups = all_passengers.str.split('_').str[0]
group_size_map = all_groups.value_counts()

# ==========================================
# 3. FEATURE ENGINEERING
# ==========================================
def engineer_feature(df, group_size_map):
    df = df.copy()

    # Cabin information
    cabin_split = df['Cabin'].str.split('/', expand=True)
    df['Deck'] = cabin_split[0]
    df['CabinNum'] = pd.to_numeric(cabin_split[1], errors='coerce')
    df['Side'] = cabin_split[2]

    # Group information
    df['GroupId'] = df['PassengerId'].str.split('_').str[0]
    df['GroupSize'] = df['GroupId'].map(group_size_map)
    df['IsAlone'] = (df['GroupSize'] == 1).astype(int)

    # Spending features
    amenities = ['RoomService', 'FoodCourt', 'ShoppingMall', 'Spa', 'VRDeck']
    df['TotalSpend'] = df[amenities].fillna(0).sum(axis=1)
    df['NoSpend'] = (df['TotalSpend'] == 0).astype(int)

    # CryoSleep domain inference
    df.loc[(df['CryoSleep'].isna()) & (df['TotalSpend'] > 0), 'CryoSleep'] = False
    df.loc[(df['CryoSleep'].isna()) & (df['TotalSpend'] == 0), 'CryoSleep'] = True

    # Spending ratios
    for col in amenities:
        df[col + '_Ratio'] = df[col] / (df['TotalSpend'] + 1)

    # Cabin interaction
    df['Deck_Side'] = df['Deck'].fillna('Unknown').astype(str) + '_' + df['Side'].fillna('Unknown').astype(str)

    return df

train = engineer_feature(train_raw, group_size_map)
test = engineer_feature(test_raw, group_size_map)

# ==========================================
# 4. FEATURES AND TARGET
# ==========================================
X = train.drop(columns=['Transported', 'PassengerId', 'Cabin', 'Name', 'GroupId'])
y = train['Transported'].astype(int)
X_test = test.drop(columns=['PassengerId', 'Cabin', 'Name', 'GroupId'])

# ==========================================
# 5. PREPROCESSING PIPELINE
# ==========================================
numerical_features = [
    'Age', 'RoomService', 'FoodCourt', 'ShoppingMall', 'Spa', 'VRDeck',
    'TotalSpend', 'GroupSize', 'NoSpend', 'IsAlone', 'CabinNum',
    'RoomService_Ratio', 'FoodCourt_Ratio', 'ShoppingMall_Ratio', 'Spa_Ratio', 'VRDeck_Ratio'
]
categorical_features = ['HomePlanet', 'CryoSleep', 'Destination', 'VIP', 'Deck', 'Side', 'Deck_Side']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ]), numerical_features),
        ('cat', Pipeline([
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ]), categorical_features)
    ]
)

# ==========================================
# 6. MODEL PIPELINE (WINNING CATBOOST)
# ==========================================
model = Pipeline([
    ('prep', preprocessor),
    ('clf', CatBoostClassifier(iterations=400, learning_rate=0.04, depth=6, random_state=42, verbose=0, thread_count=4))
])

# ==========================================
# 7. CROSS VALIDATION
# ==========================================
print("Running 5-Fold Stratified Cross-Validation on CatBoost Pipeline...")
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(model, X, y, cv=cv, scoring='accuracy', n_jobs=1)

print(f"Mean CV Accuracy: {scores.mean():.4f}")
print(f"Standard Deviation: {scores.std():.4f}")
print(f"Fold Scores: {[round(s, 4) for s in scores]}")

# ==========================================
# 8. TRAIN ON FULL DATA & GENERATE SUBMISSION
# ==========================================
print("\nTraining on full dataset and generating submission...")
model.fit(X, y)
test_preds = model.predict(X_test)

sub_dir = "/home/mohith/.gemini/antigravity/scratch/ai-ml-training-system/competitions/spaceship-titanic/submissions"
os.makedirs(sub_dir, exist_ok=True)
sub_path = os.path.join(sub_dir, f"submission_catboost_{scores.mean():.4f}.csv")

submission = pd.DataFrame({
    'PassengerId': test_raw['PassengerId'],
    'Transported': test_preds.astype(bool)
})
submission.to_csv(sub_path, index=False)
print(f"Saved submission file to: {sub_path}")
