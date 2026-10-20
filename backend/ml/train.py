import os
import sys
import json
import joblib
import numpy as np
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

# Allow local module import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from preprocess import load_dataset, clean_fitness_data, clean_food_data

# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")

FITNESS_PATH = os.path.join(DATA_DIR, "random_fitness_dataset.csv")
FOOD_PATH = os.path.join(DATA_DIR, "food_calorie_prediction_dataset.csv")

FITNESS_MODEL_PATH = os.path.join(MODEL_DIR, "fitness_model.pkl")
FOOD_MODEL_PATH = os.path.join(MODEL_DIR, "food_model.pkl")
LEGACY_FITNESS_PATH = os.path.join(MODEL_DIR, "multivariate_linear_regression.pkl")
METRICS_JSON_PATH = os.path.join(MODEL_DIR, "model_metrics.json")

os.makedirs(MODEL_DIR, exist_ok=True)

print("=" * 70)
print("CALORIEIQ - MODEL TRAINING & METRICS GENERATION")
print("=" * 70)


# ============================================================
# 1. MODEL 1: FITNESS WORKOUT BURN (KAGGLE FITNESS DATASET)
# ============================================================

print("\n--- Training Model 1: Fitness Workout Burn (New Kaggle Dataset) ---")
if not os.path.exists(FITNESS_PATH):
    raise FileNotFoundError(f"Fitness dataset not found at {FITNESS_PATH}")

fitness_raw = load_dataset(FITNESS_PATH)
fitness_df = clean_fitness_data(fitness_raw)
print(f"Loaded {len(fitness_df):,} cleaned fitness records from {os.path.basename(FITNESS_PATH)}.")

fitness_numeric = ["duration_min", "heart_rate_avg", "steps", "sleep_hours", "weight_kg", "age"]
fitness_categorical = ["activity_type", "gender"]
fitness_features = fitness_numeric + fitness_categorical
fitness_target = "calories_burned"

X_fit = fitness_df[fitness_features]
y_fit = fitness_df[fitness_target]

X_fit_train, X_fit_test, y_fit_train, y_fit_test = train_test_split(
    X_fit, y_fit, test_size=0.20, random_state=42
)

fitness_preprocessor = ColumnTransformer(
    transformers=[
        ("numeric", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ]), fitness_numeric),
        ("categorical", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
        ]), fitness_categorical)
    ]
)

best_fitness_name = "Multivariate Linear Regression Pipeline"
best_fitness_pipeline = Pipeline(steps=[
    ("preprocessor", fitness_preprocessor),
    ("model", LinearRegression())
])
best_fitness_pipeline.fit(X_fit_train, y_fit_train)
best_fit_preds = best_fitness_pipeline.predict(X_fit_test)
best_fit_mae = float(mean_absolute_error(y_fit_test, best_fit_preds))

print(f"Selected Fitness Model: {best_fitness_name} (MAE: {best_fit_mae:.2f} kcal)")

# Fitness Performance Scores (Accurate kcal!)
fit_cal_actual = y_fit_test.values
fit_cal_pred = best_fit_preds

fit_mae_cal = float(mean_absolute_error(fit_cal_actual, fit_cal_pred))
fit_mse_cal = float(mean_squared_error(fit_cal_actual, fit_cal_pred))
fit_rmse_cal = float(np.sqrt(fit_mse_cal))
fit_r2_cal = float(r2_score(fit_cal_actual, fit_cal_pred))

# Confusion Metrics (Threshold: 300 kcal for high-intensity workout burn)
burn_threshold = 300.0
fit_true_bin = (fit_cal_actual >= burn_threshold).astype(int)
fit_pred_bin = (fit_cal_pred >= burn_threshold).astype(int)

fit_cm = confusion_matrix(fit_true_bin, fit_pred_bin)
if fit_cm.shape == (2, 2):
    tn_fit, fp_fit, fn_fit, tp_fit = fit_cm.ravel()
else:
    tn_fit, fp_fit, fn_fit, tp_fit = 0, int(len(fit_true_bin)), 0, 0

fit_acc = float(accuracy_score(fit_true_bin, fit_pred_bin))
fit_prec = float(precision_score(fit_true_bin, fit_pred_bin, zero_division=0))
fit_rec = float(recall_score(fit_true_bin, fit_pred_bin, zero_division=0))
fit_f1 = float(f1_score(fit_true_bin, fit_pred_bin, zero_division=0))

print(f"Fitness Model: TP={tp_fit}, TN={tn_fit}, FP={fp_fit}, FN={fn_fit}")
print(f"Fitness Scores: Accuracy={fit_acc:.4f}, Precision={fit_prec:.4f}, Recall={fit_rec:.4f}, F1={fit_f1:.4f}, R2={fit_r2_cal:.4f}, MAE={fit_mae_cal:.2f} kcal, RMSE={fit_rmse_cal:.2f} kcal")


# ============================================================
# 2. MODEL 2: FOOD CALORIE PREDICTION
# ============================================================

print("\n--- Training Model 2: Food Calorie Prediction ---")
food_raw = load_dataset(FOOD_PATH)
food_df = clean_food_data(food_raw)
print(f"Loaded {len(food_df):,} food records.")

food_features = ["protein_g", "carbohydrates_g", "fat_g", "fiber_g", "sugar_g"]
food_target = "calories_kcal"

X_food = food_df[food_features]
y_food = food_df[food_target]

X_food_train, X_food_test, y_food_train, y_food_test = train_test_split(
    X_food, y_food, test_size=0.20, random_state=42
)

food_model = LinearRegression()
food_model.fit(X_food_train, y_food_train)
food_preds = food_model.predict(X_food_test)

# Food Regression Performance Scores
food_actual = y_food_test.values
food_mae = float(mean_absolute_error(food_actual, food_preds))
food_mse = float(mean_squared_error(food_actual, food_preds))
food_rmse = float(np.sqrt(food_mse))
food_r2 = float(r2_score(food_actual, food_preds))

# Food Confusion Metrics (Standard 250 kcal meal energy threshold: High vs Normal/Low)
calorie_threshold = 250.0
food_true_bin = (food_actual >= calorie_threshold).astype(int)
food_pred_bin = (food_preds >= calorie_threshold).astype(int)

food_cm = confusion_matrix(food_true_bin, food_pred_bin)
tn_food, fp_food, fn_food, tp_food = food_cm.ravel()

food_acc = float(accuracy_score(food_true_bin, food_pred_bin))
food_prec = float(precision_score(food_true_bin, food_pred_bin, zero_division=0))
food_rec = float(recall_score(food_true_bin, food_pred_bin, zero_division=0))
food_f1 = float(f1_score(food_true_bin, food_pred_bin, zero_division=0))

print(f"Food Model: TP={tp_food}, TN={tn_food}, FP={fp_food}, FN={fn_food}")
print(f"Food Scores: Accuracy={food_acc:.4f}, Precision={food_prec:.4f}, Recall={food_rec:.4f}, F1={food_f1:.4f}, R2={food_r2:.4f}, MAE={food_mae:.4f}")


# ============================================================
# 3. SAVE MODELS & CLEAN METRICS JSON
# ============================================================

joblib.dump(food_model, FOOD_MODEL_PATH)
joblib.dump(best_fitness_pipeline, FITNESS_MODEL_PATH)
joblib.dump(best_fitness_pipeline, LEGACY_FITNESS_PATH)

metrics_payload = {
    "timestamp": datetime.now().isoformat(),
    "food_model": {
        "name": "Food Calorie Prediction Model",
        "algorithm": "Multivariate Linear Regression",
        "dataset": "food_calorie_prediction_dataset.csv",
        "total_samples": int(len(food_df)),
        "test_samples": int(len(X_food_test)),
        "confusion_metrics": {
            "TP": int(tp_food),
            "TN": int(tn_food),
            "FP": int(fp_food),
            "FN": int(fn_food),
            "threshold": f"{calorie_threshold} kcal"
        },
        "performance_scores": {
            "accuracy": round(food_acc, 4),
            "precision": round(food_prec, 4),
            "recall": round(food_rec, 4),
            "f1_score": round(food_f1, 4),
            "r2_score": round(food_r2, 4),
            "mae": round(food_mae, 4),
            "rmse": round(food_rmse, 4),
            "mse": round(food_mse, 4)
        }
    },
    "fitness_model": {
        "name": "Fitness Activity & Burn Model",
        "algorithm": best_fitness_name,
        "dataset": "random_fitness_dataset.csv",
        "total_samples": int(len(fitness_df)),
        "test_samples": int(len(X_fit_test)),
        "confusion_metrics": {
            "TP": int(tp_fit),
            "TN": int(tn_fit),
            "FP": int(fp_fit),
            "FN": int(fn_fit),
            "threshold": f"{calorie_threshold if burn_threshold is None else burn_threshold} kcal"
        },
        "performance_scores": {
            "accuracy": round(fit_acc, 4),
            "precision": round(fit_prec, 4),
            "recall": round(fit_rec, 4),
            "f1_score": round(fit_f1, 4),
            "r2_score": round(fit_r2_cal, 4),
            "mae": round(fit_mae_cal, 2),
            "rmse": round(fit_rmse_cal, 2),
            "mse": round(fit_mse_cal, 2),
            "calories_burned_mae": round(fit_mae_cal, 2),
            "calories_burned_rmse": round(fit_rmse_cal, 2)
        }
    }
}

with open(METRICS_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(metrics_payload, f, indent=2)

print(f"\nMetrics saved to {METRICS_JSON_PATH}")
print("Training and evaluation completed successfully!")