import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.model_selection import RandomizedSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.impute import KNNImputer
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier

# -------------------------------
# LOAD DATASET
# -------------------------------
data = pd.read_csv("dataset/water_potability.csv")

# -------------------------------
# SPLIT FEATURES & TARGET
# -------------------------------
X = data.drop("Potability", axis=1)
print(X.columns)
y = data["Potability"]

# -------------------------------
# HANDLE MISSING VALUES (KNN)
# -------------------------------
imputer = KNNImputer(n_neighbors=5)
X = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)

# -------------------------------
# OUTLIER CLIPPING (VERY IMPORTANT)
# -------------------------------
for col in X.columns:
    lower = X[col].quantile(0.01)
    upper = X[col].quantile(0.99)
    X[col] = X[col].clip(lower, upper)

# -------------------------------
# TRAIN TEST SPLIT
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -------------------------------
# FEATURE SCALING
# -------------------------------
scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# -------------------------------
# HANDLE CLASS IMBALANCE
# -------------------------------
pos_weight = len(y[y == 0]) / len(y[y == 1])

# -------------------------------
# BASE MODEL
# -------------------------------
xgb = XGBClassifier(eval_metric='logloss')

param_dist = {
    'n_estimators': [200, 300, 500, 700],
    'max_depth': [3, 4, 5, 6, 8],
    'learning_rate': [0.01, 0.03, 0.05, 0.1],
    'subsample': [0.7, 0.8, 0.9, 1.0],
    'colsample_bytree': [0.7, 0.8, 0.9, 1.0],
    'gamma': [0, 0.1, 0.2],
    'reg_lambda': [1, 1.5, 2]
}

random_search = RandomizedSearchCV(
    xgb,
    param_distributions=param_dist,
    n_iter=20,   # try 20 combinations
    scoring='accuracy',
    cv=3,
    verbose=1,
    n_jobs=-1,
    random_state=42
)

random_search.fit(X_train, y_train)

best_model = random_search.best_estimator_

print("Best Params:", random_search.best_params_)

# -------------------------------
# CROSS VALIDATION SCORE
# -------------------------------
cv_scores = cross_val_score(best_model, X_train, y_train, cv=5, scoring='accuracy')
print("\n📊 Cross Validation Accuracy:", cv_scores.mean())

# -------------------------------
# EVALUATION
# -------------------------------
y_pred = best_model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print("\n✅ Test Accuracy:", accuracy)

print("\n📊 Classification Report:\n")
print(classification_report(y_test, y_pred))

# -------------------------------
# FEATURE IMPORTANCE
# -------------------------------
importances = best_model.feature_importances_
features = X.columns

feature_importance = sorted(
    zip(features, importances),
    key=lambda x: x[1],
    reverse=True
)

print("\n📊 Feature Importance Ranking:\n")
for feature, score in feature_importance:
    print(f"{feature}: {score:.4f}")

# -------------------------------
# PLOT FEATURE IMPORTANCE
# -------------------------------
plt.figure(figsize=(8,5))
plt.barh([f[0] for f in feature_importance], [f[1] for f in feature_importance])
plt.gca().invert_yaxis()
plt.title("Feature Importance Ranking")
plt.xlabel("Importance Score")
plt.ylabel("Features")
plt.tight_layout()
plt.show()

# -------------------------------
# SAVE MODEL & SCALER
# -------------------------------
pickle.dump(best_model, open("models/xgboost.sav", "wb"))
pickle.dump(scaler, open("models/scaler.sav", "wb"))

print("\n✅ Model and Scaler saved successfully!")