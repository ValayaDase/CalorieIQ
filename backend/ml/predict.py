import os
import joblib
import pandas as pd

# Dynamically resolve absolute paths to the models
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(os.path.dirname(BASE_DIR), "models")

FITNESS_MODEL_PATH = os.path.join(MODELS_DIR, "fitness_model.pkl")
FOOD_MODEL_PATH = os.path.join(MODELS_DIR, "food_model.pkl")
LEGACY_FITNESS_PATH = os.path.join(MODELS_DIR, "multivariate_linear_regression.pkl")

# Cached model instances in memory
_FOOD_MODEL = None
_FITNESS_MODEL = None


def get_food_model():
    """Returns the cached trained food calorie model, loading if necessary."""
    global _FOOD_MODEL
    if _FOOD_MODEL is None:
        if os.path.exists(FOOD_MODEL_PATH):
            _FOOD_MODEL = joblib.load(FOOD_MODEL_PATH)
        else:
            raise FileNotFoundError(f"Food model not found at {FOOD_MODEL_PATH}. Run train.py first.")
    return _FOOD_MODEL


def get_fitness_model():
    """Returns the cached trained fitness pipeline, loading if necessary."""
    global _FITNESS_MODEL
    if _FITNESS_MODEL is None:
        if os.path.exists(FITNESS_MODEL_PATH):
            _FITNESS_MODEL = joblib.load(FITNESS_MODEL_PATH)
        elif os.path.exists(LEGACY_FITNESS_PATH):
            _FITNESS_MODEL = joblib.load(LEGACY_FITNESS_PATH)
        else:
            raise FileNotFoundError(f"Fitness model not found at {FITNESS_MODEL_PATH}. Run train.py first.")
    return _FITNESS_MODEL


def predict_food(protein, carbohydrates, fat, fiber, sugar):
    """
    Predicts calories based on macronutrients using the trained multivariate regression model.
    Also provides nutritional macro caloric distribution and density tier.
    """
    try:
        p = max(0.0, float(protein))
        c = max(0.0, float(carbohydrates))
        f = max(0.0, float(fat))
        fib = max(0.0, float(fiber))
        sug = max(0.0, float(sugar))

        model = get_food_model()
        features_df = pd.DataFrame([[p, c, f, fib, sug]], columns=[
            "protein_g", "carbohydrates_g", "fat_g", "fiber_g", "sugar_g"
        ])

        pred = model.predict(features_df)
        predicted_calories = max(0.0, float(pred[0]))

        # Calculate macro energy breakdown (Atwater standards)
        p_kcal = p * 4.0
        c_kcal = c * 4.0
        f_kcal = f * 9.0
        total_macro_kcal = p_kcal + c_kcal + f_kcal

        if total_macro_kcal > 0:
            protein_pct = round((p_kcal / total_macro_kcal) * 100, 1)
            carbs_pct = round((c_kcal / total_macro_kcal) * 100, 1)
            fat_pct = round((f_kcal / total_macro_kcal) * 100, 1)
        else:
            protein_pct, carbs_pct, fat_pct = 0.0, 0.0, 0.0

        # Density Tier
        if predicted_calories < 180:
            tier = "Low Calorie (<180 kcal)"
            tier_badge = "low"
        elif predicted_calories <= 300:
            tier = "Moderate Calorie (180-300 kcal)"
            tier_badge = "moderate"
        elif predicted_calories <= 450:
            tier = "High Calorie (300-450 kcal)"
            tier_badge = "high"
        else:
            tier = "Very High Calorie (>450 kcal)"
            tier_badge = "very-high"

        return {
            "calories": round(predicted_calories, 2),
            "tier": tier,
            "tier_badge": tier_badge,
            "breakdown": {
                "protein_kcal": round(p_kcal, 1),
                "carbs_kcal": round(c_kcal, 1),
                "fat_kcal": round(f_kcal, 1),
                "protein_pct": protein_pct,
                "carbs_pct": carbs_pct,
                "fat_pct": fat_pct
            }
        }

    except Exception as e:
        print(f"Food Prediction Error: {e}")
        p = float(protein or 0)
        c = float(carbohydrates or 0)
        f = float(fat or 0)
        fallback = max(0.0, (p * 4.0) + (c * 4.0) + (f * 9.0))
        return {
            "calories": round(fallback, 2),
            "tier": "Estimated",
            "tier_badge": "moderate",
            "breakdown": {
                "protein_kcal": round(p * 4.0, 1),
                "carbs_kcal": round(c * 4.0, 1),
                "fat_kcal": round(f * 9.0, 1),
                "protein_pct": 33.3,
                "carbs_pct": 33.3,
                "fat_pct": 33.3
            }
        }


def predict_fitness(data):
    """
    Predicts calories burned in kcal based on fitness workout metrics
    using the trained Ridge Regression Pipeline on the new Kaggle fitness dataset.
    """
    try:
        activity_type = str(data.get("activity_type") or data.get("workout_type") or "Running").strip().title()
        gender = str(data.get("gender") or "Female").strip().title()
        if gender not in ["Female", "Male", "Other"]:
            gender = "Other"

        duration_min = float(data.get("duration_min") or data.get("active_minutes") or 45.0)
        heart_rate_avg = float(data.get("heart_rate_avg") or data.get("heart_rate") or 135.0)
        steps = float(data.get("steps") or 5000.0)
        sleep_hours = float(data.get("sleep_hours") or data.get("sleep") or 7.5)
        weight_kg = float(data.get("weight_kg") or data.get("weight") or 70.0)
        age = float(data.get("age") or 28.0)

        # Enforce reasonable bounds
        duration_min = max(1.0, min(duration_min, 300.0))
        heart_rate_avg = max(40.0, min(heart_rate_avg, 220.0))
        steps = max(0.0, steps)
        sleep_hours = max(0.0, min(sleep_hours, 24.0))
        weight_kg = max(20.0, min(weight_kg, 250.0))
        age = max(10.0, min(age, 100.0))

        model = get_fitness_model()

        input_df = pd.DataFrame([{
            "duration_min": duration_min,
            "heart_rate_avg": heart_rate_avg,
            "steps": steps,
            "sleep_hours": sleep_hours,
            "weight_kg": weight_kg,
            "age": age,
            "activity_type": activity_type,
            "gender": gender
        }])

        prediction = model.predict(input_df)
        calories_kcal = max(10.0, float(prediction[0]))

        # Burn Intensity classification based on actual kcal burned
        if calories_kcal < 200:
            intensity = "Light Burn (<200 kcal)"
            intensity_badge = "light"
        elif calories_kcal <= 380:
            intensity = "Moderate Burn (200-380 kcal)"
            intensity_badge = "moderate"
        else:
            intensity = "High Intensity Burn (>380 kcal)"
            intensity_badge = "intense"

        burn_rate = round(calories_kcal / max(1.0, duration_min), 2)

        # Realistic estimated workout distance (km) for cardio activities
        distance_rates = {
            "Running": 0.16,
            "Walking": 0.08,
            "Cycling": 0.32,
            "Swimming": 0.035,
            "Hiit": 0.05,
            "Strength Training": 0.02,
            "Yoga": 0.01
        }
        dist_factor = distance_rates.get(activity_type, 0.05)
        estimated_distance = round(duration_min * dist_factor, 2)

        return {
            "calories_burned": round(calories_kcal, 1),
            "calories_burned_kcal": round(calories_kcal, 1),
            "burn_rate_per_min": burn_rate,
            "distance_km": estimated_distance,
            "intensity": intensity,
            "intensity_badge": intensity_badge,
            "activity_type": activity_type,
            "duration_min": round(duration_min, 1)
        }

    except Exception as e:
        print(f"Fitness Prediction Error: {e}")
        duration = float(data.get("duration_min") or data.get("active_minutes") or 45.0)
        heart_rate = float(data.get("heart_rate_avg") or 130.0)
        weight = float(data.get("weight_kg") or data.get("weight") or 70.0)
        age = float(data.get("age") or 28.0)
        act = str(data.get("activity_type") or data.get("workout_type") or "Running").strip().title()

        # Keytel standard physiological fallback
        fallback_kcal = max(50.0, (duration * (0.6309 * heart_rate + 0.1988 * weight + 0.2017 * age - 55.0969) / 4.184))
        
        return {
            "calories_burned": round(fallback_kcal, 1),
            "calories_burned_kcal": round(fallback_kcal, 1),
            "burn_rate_per_min": round(fallback_kcal / max(1.0, duration), 2),
            "distance_km": round(duration * 0.12, 2),
            "intensity": "Estimated Burn",
            "intensity_badge": "moderate",
            "activity_type": act,
            "duration_min": duration
        }