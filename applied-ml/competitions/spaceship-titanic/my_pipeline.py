
import os
import pandas as pd
import numpy as np

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier


# ==========================================
# 1. LOAD DATA
# ==========================================

DATA_DIR = "/home/mohith/.gemini/antigravity/scratch/ai-ml-training-system/competitions/spaceship-titanic/data"

train_raw = pd.read_csv(os.path.join(DATA_DIR, "train.csv"))
test_raw = pd.read_csv(os.path.join(DATA_DIR, "test.csv"))


# ==========================================
# 2. GLOBAL GROUP MAPPING
# ==========================================

all_passengers = pd.concat([
    train_raw['PassengerId'],
    test_raw['PassengerId']
], ignore_index=True)

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
    df['CabinNum'] = pd.to_numeric(
        cabin_split[1], errors='coerce'
    )
    df['Side'] = cabin_split[2]

    # Group information
    df['GroupId'] = df['PassengerId'].str.split('_').str[0]

    df['GroupSize'] = df['GroupId'].map(group_size_map)

    df['IsAlone'] = (df['GroupSize'] == 1).astype(int)

    # Spending features
    amenities = [
        'RoomService',
        'FoodCourt',
        'ShoppingMall',
        'Spa',
        'VRDeck'
    ]

    df['TotalSpend'] = df[amenities].fillna(0).sum(axis=1)

    df['NoSpend'] = (df['TotalSpend'] == 0).astype(int)

    # CryoSleep inference
    df.loc[
        (df['CryoSleep'].isna()) & (df['TotalSpend'] > 0),
        'CryoSleep'
    ] = False

    df.loc[
        (df['CryoSleep'].isna()) & (df['TotalSpend'] == 0),
        'CryoSleep'
    ] = True

    # Spending ratios
    for col in amenities:
        df[col + '_Ratio'] = (
            df[col] / (df['TotalSpend'] + 1)
        )

    # Cabin interaction
    df['Deck_Side'] = (
        df['Deck'].fillna('Unknown').astype(str)
        + '_'
        + df['Side'].fillna('Unknown').astype(str)
    )

    return df


train = engineer_feature(train_raw, group_size_map)
test = engineer_feature(test_raw, group_size_map)


# ==========================================
# 4. FEATURES AND TARGET
# ==========================================

X = train.drop(
    columns=[
        'Transported',
        'PassengerId',
        'Cabin',
        'Name',
        'GroupId'
    ]
)

y = train['Transported']


# ==========================================
# 5. PREPROCESSING
# ==========================================

numerical_features = [
    'Age',
    'RoomService',
    'FoodCourt',
    'ShoppingMall',
    'Spa',
    'VRDeck',
    'TotalSpend',
    'GroupSize',
    'NoSpend',
    'IsAlone',
    'CabinNum',
    'RoomService_Ratio',
    'FoodCourt_Ratio',
    'ShoppingMall_Ratio',
    'Spa_Ratio',
    'VRDeck_Ratio'
]

categorical_features = [
    'HomePlanet',
    'CryoSleep',
    'Destination',
    'VIP',
    'Deck',
    'Side',
    'Deck_Side'
]


preprocessor = ColumnTransformer(
    transformers=[
        (
            'num',
            Pipeline([
                ('imputer', SimpleImputer(strategy='median')),
                ('scaler', StandardScaler())
            ]),
            numerical_features
        ),
        (
            'cat',
            Pipeline([
                ('imputer', SimpleImputer(strategy='most_frequent')),
                ('onehot', OneHotEncoder(
                    handle_unknown='ignore'
                ))
            ]),
            categorical_features
        )
    ]
)


# ==========================================
# 6. MODEL
# ==========================================

model = Pipeline([
    ('prep', preprocessor),
    ('rf', RandomForestClassifier(
        n_estimators=300,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        max_features='sqrt',
        random_state=42,
        n_jobs=-1
    ))
])


# ==========================================
# 7. CROSS VALIDATION
# ==========================================

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

scores = cross_val_score(
    model,
    X,
    y,
    cv=cv,
    scoring='accuracy',
    n_jobs=-1
)

print(f"Mean CV Accuracy: {scores.mean():.4f}")
print(f"Standard Deviation: {scores.std():.4f}")

print(
    f"Fold Scores: {[round(s, 4) for s in scores]}"
)
