import os
import sys
import pandas as pd
import numpy as np

# Allow importing preprocess.py
sys.path.append(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

from preprocess import load_csv


# ============================================================
# PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "random_fitness_dataset.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading dataset...")

df = load_csv(DATA_PATH)

print("Dataset loaded successfully!")


# ============================================================
# BASIC INFORMATION
# ============================================================

print("\n==========================================")
print("DATASET INFORMATION")
print("==========================================")

print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

print("\nData Types:")
print(df.dtypes)


# ============================================================
# MISSING VALUES
# ============================================================

print("\n==========================================")
print("MISSING VALUES")
print("==========================================")

missing = df.isnull().sum()

print(missing)


# ============================================================
# DUPLICATES
# ============================================================

print("\n==========================================")
print("DUPLICATES")
print("==========================================")

print(
    "Duplicate rows:",
    df.duplicated().sum()
)


# ============================================================
# NUMERIC COLUMNS
# ============================================================

numeric_df = df.select_dtypes(
    include=np.number
)


print("\n==========================================")
print("NUMERIC COLUMNS")
print("==========================================")

print(
    numeric_df.columns.tolist()
)


# ============================================================
# DESCRIPTIVE STATISTICS
# ============================================================

print("\n==========================================")
print("DESCRIPTIVE STATISTICS")
print("==========================================")

print(
    numeric_df.describe()
)


# ============================================================
# CORRELATION WITH CALORIES
# ============================================================

print("\n==========================================")
print("CORRELATION WITH CALORIES BURNED")
print("==========================================")

correlation = (
    numeric_df
    .corr()["calories_burned"]
    .sort_values(
        ascending=False
    )
)

print(correlation)


# ============================================================
# CORRELATION WITH DISTANCE (IF PRESENT)
# ============================================================

if "distance_km" in numeric_df.columns:
    print("\n==========================================")
    print("CORRELATION WITH DISTANCE")
    print("==========================================")

    distance_correlation = (
        numeric_df
        .corr()["distance_km"]
        .sort_values(
            ascending=False
        )
    )

    print(distance_correlation)


# ============================================================
# CALORIES CORRELATION STRENGTH
# ============================================================

print("\n==========================================")
print("CALORIES CORRELATION STRENGTH")
print("==========================================")

calories_corr = (
    numeric_df
    .corr()["calories_burned"]
    .drop("calories_burned")
    .abs()
    .sort_values(
        ascending=False
    )
)

for feature, value in calories_corr.items():

    print(
        f"{feature:25} : {value:.4f}"
    )


# ============================================================
# TARGET STATISTICS
# ============================================================

print("\n==========================================")
print("TARGET STATISTICS")
print("==========================================")

print(
    "\nCalories Burned:"
)

print(
    df["calories_burned"].describe()
)


if "distance_km" in df.columns:
    print(
        "\nDistance:"
    )
    print(
        df["distance_km"].describe()
    )


# ============================================================
# CATEGORICAL INFORMATION
# ============================================================

categorical_columns = df.select_dtypes(
    include=["object", "category"]
).columns


print("\n==========================================")
print("CATEGORICAL FEATURES")
print("==========================================")


for column in categorical_columns:

    print(
        f"\n{column}:"
    )

    print(
        df[column]
        .value_counts()
        .head(10)
    )


# ============================================================
# END
# ============================================================

print("\n==========================================")
print("ANALYSIS COMPLETED")
print("==========================================")