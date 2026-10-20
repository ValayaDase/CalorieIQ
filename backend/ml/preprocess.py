import pandas as pd
# pyrefly: ignore [missing-import]
import numpy as np


# ============================================================
# GENERIC DATA LOADER
# ============================================================

def load_dataset(file_path):
    """
    Loads a CSV file into a pandas DataFrame, normalizing column names
    and dropping duplicate rows.
    """
    df = pd.read_csv(file_path)

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    df = df.drop_duplicates()

    df = df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    return df


# Alias for backward compatibility
def load_csv(file_path):
    return load_dataset(file_path)


# ============================================================
# FITNESS DATA CLEANING
# ============================================================

def clean_fitness_data(df):
    """
    Cleans and prepares the fitness workout dataset.
    Supports columns from the new Kaggle random fitness dataset:
    activity_type, duration_min, heart_rate_avg, steps, sleep_hours, weight_kg, age, gender, calories_burned.
    Also handles common aliases (e.g. workout_type -> activity_type, active_minutes -> duration_min).
    """
    column_mapping = {}
    for col in df.columns:
        c = col.lower().strip()
        if c in ["workout_type", "activity", "activity_type", "exercise_type", "exercise"]:
            column_mapping[col] = "activity_type"
        elif c in ["active_minutes", "duration", "duration_min", "duration_minutes"]:
            column_mapping[col] = "duration_min"
        elif c in ["heart_rate", "heart_rate_avg", "hr", "avg_hr"]:
            column_mapping[col] = "heart_rate_avg"
        elif c in ["steps", "step_count"]:
            column_mapping[col] = "steps"
        elif c in ["sleep_hours", "sleep", "sleep_duration"]:
            column_mapping[col] = "sleep_hours"
        elif c in ["weight_kg", "weight"]:
            column_mapping[col] = "weight_kg"
        elif c in ["age", "user_age"]:
            column_mapping[col] = "age"
        elif c in ["gender", "sex"]:
            column_mapping[col] = "gender"
        elif c in ["calories_burned", "calories", "burn", "calorie_burn", "calories_kcal"]:
            column_mapping[col] = "calories_burned"

    df = df.rename(columns=column_mapping)

    required_features = [
        "activity_type",
        "duration_min",
        "heart_rate_avg",
        "steps",
        "sleep_hours",
        "weight_kg",
        "age",
        "gender"
    ]

    missing = [c for c in required_features if c not in df.columns]
    if missing:
        raise ValueError(f"Fitness dataset missing required columns: {missing}")

    numeric_columns = [
        "duration_min",
        "heart_rate_avg",
        "steps",
        "sleep_hours",
        "weight_kg",
        "age"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    categorical_columns = ["activity_type", "gender"]
    for col in categorical_columns:
        df[col] = df[col].fillna("Unknown").astype(str).str.strip().str.title()

    if "calories_burned" in df.columns:
        df["calories_burned"] = pd.to_numeric(df["calories_burned"], errors="coerce")
        df = df.dropna(subset=["calories_burned"] + numeric_columns)
    else:
        df = df.dropna(subset=numeric_columns)

    # Sanity bounds
    df = df[
        (df["duration_min"] > 0) & (df["duration_min"] <= 300) &
        (df["heart_rate_avg"] >= 40) & (df["heart_rate_avg"] <= 220) &
        (df["weight_kg"] >= 20) & (df["weight_kg"] <= 250) &
        (df["age"] >= 10) & (df["age"] <= 100)
    ]

    return df


# ============================================================
# FOOD DATA CLEANING
# ============================================================

def clean_food_data(df):
    """
    Cleans and prepares the food calorie prediction dataset.
    Supports columns: protein_g, carbohydrates_g, fat_g, fiber_g, sugar_g, calories_kcal
    with flexible alias resolution.
    """
    column_mapping = {}
    for col in df.columns:
        c = col.lower().strip()
        if c in ["protein_g", "protein"]:
            column_mapping[col] = "protein_g"
        elif c in ["carbohydrates_g", "carbohydrates", "carbs", "carb"]:
            column_mapping[col] = "carbohydrates_g"
        elif c in ["fat_g", "fat", "fats"]:
            column_mapping[col] = "fat_g"
        elif c in ["fiber_g", "fiber"]:
            column_mapping[col] = "fiber_g"
        elif c in ["sugar_g", "sugar", "sugars"]:
            column_mapping[col] = "sugar_g"
        elif c in ["calories_kcal", "calories", "kcal", "calorie"]:
            column_mapping[col] = "calories_kcal"

    df = df.rename(columns=column_mapping)

    required_features = [
        "protein_g",
        "carbohydrates_g",
        "fat_g",
        "fiber_g",
        "sugar_g"
    ]

    for col in required_features:
        if col not in df.columns:
            raise ValueError(f"Food dataset missing required column: {col}")

    all_cols = required_features.copy()
    if "calories_kcal" in df.columns:
        all_cols.append("calories_kcal")

    for col in all_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=all_cols)
    return df