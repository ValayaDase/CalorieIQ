import os
import sys
import json

# Ensure backend directory is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS
from ml.predict import predict_fitness, predict_food

# ============================================================
# APP SETUP
# ============================================================

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
METRICS_JSON_PATH = os.path.join(BASE_DIR, "models", "model_metrics.json")


# ============================================================
# HOME & HEALTH
# ============================================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "message": "CalorieIQ Machine Learning API is active and ready",
        "version": "2.0.0",
        "models": [
            {
                "id": "food_model",
                "name": "Food Calorie Multivariate Linear Regression",
                "target": "calories_kcal"
            },
            {
                "id": "fitness_model",
                "name": "Fitness Activity & Burn Model (Multivariate Linear Regression Pipeline)",
                "target": "calories_burned_kcal"
            }
        ],
        "endpoints": [
            "/api/model-info",
            "/predict/food",
            "/predict/fitness",
            "/api/presets"
        ]
    })


# ============================================================
# MODEL INFORMATION & METRICS
# ============================================================

@app.route("/api/model-info", methods=["GET"])
def model_info():
    """
    Returns rich performance metrics, confusion matrices, feature weights,
    and metadata for both machine learning models.
    """
    try:
        if os.path.exists(METRICS_JSON_PATH):
            with open(METRICS_JSON_PATH, "r", encoding="utf-8") as f:
                metrics_data = json.load(f)
            return jsonify({
                "success": True,
                "data": metrics_data
            })
        else:
            return jsonify({
                "success": False,
                "error": "Model metrics file not found. Please run backend/ml/train.py first."
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================
# PRESETS FOR DEMO / FAST INPUT
# ============================================================

@app.route("/api/presets", methods=["GET"])
def presets():
    """
    Returns quick-load presets for food intake and workout routines.
    """
    return jsonify({
        "success": True,
        "food_presets": [
            {
                "name": "High-Protein Salmon & Quinoa",
                "protein": 34.0,
                "carbohydrates": 28.5,
                "fat": 14.2,
                "fiber": 4.5,
                "sugar": 2.1,
                "category": "High Protein"
            },
            {
                "name": "Avocado Chicken Salad",
                "protein": 28.0,
                "carbohydrates": 12.0,
                "fat": 18.5,
                "fiber": 6.8,
                "sugar": 3.0,
                "category": "Low Carb"
            },
            {
                "name": "Oatmeal with Berries & Honey",
                "protein": 11.5,
                "carbohydrates": 54.0,
                "fat": 5.2,
                "fiber": 7.4,
                "sugar": 16.0,
                "category": "Energy Fuel"
            },
            {
                "name": "Chocolate Peanut Butter Shake",
                "protein": 42.0,
                "carbohydrates": 38.0,
                "fat": 21.0,
                "fiber": 5.0,
                "sugar": 19.5,
                "category": "Mass Gainer"
            }
        ],
        "fitness_presets": [
            {
                "name": "Morning 5K Outdoor Run",
                "activity_type": "Running",
                "duration_min": 35,
                "heart_rate_avg": 152,
                "weight_kg": 68.0,
                "age": 26,
                "gender": "Female",
                "steps": 7500,
                "sleep_hours": 7.8
            },
            {
                "name": "High-Intensity HIIT Session",
                "activity_type": "HIIT",
                "duration_min": 40,
                "heart_rate_avg": 162,
                "weight_kg": 74.0,
                "age": 30,
                "gender": "Male",
                "steps": 5200,
                "sleep_hours": 6.8
            },
            {
                "name": "Evening City Cycling",
                "activity_type": "Cycling",
                "duration_min": 55,
                "heart_rate_avg": 136,
                "weight_kg": 72.0,
                "age": 34,
                "gender": "Other",
                "steps": 3800,
                "sleep_hours": 8.0
            },
            {
                "name": "Mindful Yoga & Mobility",
                "activity_type": "Yoga",
                "duration_min": 60,
                "heart_rate_avg": 98,
                "weight_kg": 62.0,
                "age": 29,
                "gender": "Female",
                "steps": 2200,
                "sleep_hours": 8.2
            },
            {
                "name": "Power Strength Training",
                "activity_type": "Strength Training",
                "duration_min": 50,
                "heart_rate_avg": 128,
                "weight_kg": 80.0,
                "age": 31,
                "gender": "Male",
                "steps": 4100,
                "sleep_hours": 7.4
            }
        ]
    })


# ============================================================
# FITNESS PREDICTION
# ============================================================

@app.route("/predict/fitness", methods=["POST"])
def fitness_prediction():
    try:
        data = request.get_json(force=True, silent=True) or {}
        
        # Validations with alias support
        duration = data.get("duration_min") or data.get("active_minutes") or data.get("duration")
        if duration is None:
            return jsonify({
                "success": False,
                "error": "Workout duration in minutes is required."
            }), 400

        result = predict_fitness(data)
        
        return jsonify({
            "success": True,
            "prediction": result
        })
        
    except Exception as error:
        return jsonify({
            "success": False,
            "error": str(error)
        }), 400


# ============================================================
# FOOD PREDICTION
# ============================================================

@app.route("/predict/food", methods=["POST"])
def food_prediction():
    try:
        data = request.get_json(force=True, silent=True) or {}

        # Extract macronutrients with support for common alias variations
        protein = data.get("protein", data.get("protein_g"))
        carbohydrates = data.get("carbohydrates", data.get("carbohydrates_g", data.get("carbs")))
        fat = data.get("fat", data.get("fat_g"))
        fiber = data.get("fiber", data.get("fiber_g", 0.0))
        sugar = data.get("sugar", data.get("sugar_g", 0.0))

        if None in (protein, carbohydrates, fat):
            return jsonify({
                "success": False,
                "error": "Protein, carbohydrates, and fat values are required."
            }), 400

        result = predict_food(
            float(protein),
            float(carbohydrates),
            float(fat),
            float(fiber if fiber is not None else 0.0),
            float(sugar if sugar is not None else 0.0)
        )

        return jsonify({
            "success": True,
            "prediction": result
        })

    except Exception as error:
        return jsonify({
            "success": False,
            "error": str(error)
        }), 400


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)