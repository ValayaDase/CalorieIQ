/**
 * CalorieIQ - Bright Mode Interactive Client
 * Shared logic for index.html (Prediction Dashboard) and models.html (Model Information)
 */

const API_BASE = "http://127.0.0.1:5000";

// App State for Dashboard
const state = {
    totalIntake: 0,
    totalBurn: 0,
    history: []
};

// Preset Definitions
const PRESETS = {
    food: {
        salmon: { protein: 34.0, carbs: 28.5, fat: 14.2, fiber: 4.5, sugar: 2.1 },
        salad: { protein: 28.0, carbs: 12.0, fat: 18.5, fiber: 6.8, sugar: 3.0 },
        oats: { protein: 11.5, carbs: 54.0, fat: 5.2, fiber: 7.4, sugar: 16.0 },
        shake: { protein: 42.0, carbs: 38.0, fat: 21.0, fiber: 5.0, sugar: 19.5 }
    },
    fitness: {
        run5k: { activity_type: "Running", duration: 35, hr: 152, weight: 68, age: 26, gender: "Female", steps: 7500, sleep: 7.8 },
        hiit: { activity_type: "HIIT", duration: 40, hr: 162, weight: 74, age: 30, gender: "Male", steps: 5200, sleep: 6.8 },
        cycling: { activity_type: "Cycling", duration: 55, hr: 136, weight: 72, age: 34, gender: "Other", steps: 3800, sleep: 8.0 },
        yoga: { activity_type: "Yoga", duration: 60, hr: 98, weight: 62, age: 29, gender: "Female", steps: 2200, sleep: 8.2 },
        strength: { activity_type: "Strength Training", duration: 50, hr: 128, weight: 80, age: 31, gender: "Male", steps: 4100, sleep: 7.4 }
    }
};

// Initialize Page
document.addEventListener("DOMContentLoaded", () => {
    checkBackendHealth();

    // Check which page is currently loaded
    const isDashboard = document.getElementById("foodCalorieForm") !== null;
    const isModelInfo = document.getElementById("foodTP") !== null;

    if (isDashboard) {
        initDashboard();
    }

    if (isModelInfo) {
        initModelInfo();
    }
});

// ============================================================
// BACKEND HEALTH CHECK
// ============================================================
async function checkBackendHealth() {
    const statusLabel = document.getElementById("backendStatusLabel");
    const statusPill = document.getElementById("backendStatusPill");
    if (!statusLabel || !statusPill) return;

    try {
        const res = await fetch(`${API_BASE}/`);
        if (res.ok) {
            statusLabel.textContent = "Backend Online";
            statusPill.style.background = "#ecfdf5";
            statusPill.style.borderColor = "#a7f3d0";
            statusPill.style.color = "#065f46";
            statusPill.querySelector(".status-dot").style.background = "#10b981";
        } else {
            throw new Error();
        }
    } catch (e) {
        statusLabel.textContent = "Backend Offline (Port 5000)";
        statusPill.style.background = "#fef2f2";
        statusPill.style.borderColor = "#fecaca";
        statusPill.style.color = "#991b1b";
        statusPill.querySelector(".status-dot").style.background = "#ef4444";
    }

    statusPill.addEventListener("click", () => {
        showToast("Re-checking backend connection...", "info");
        checkBackendHealth();
    });
}

// ============================================================
// DASHBOARD LOGIC (index.html)
// ============================================================
function initDashboard() {
    // 1. Presets
    document.querySelectorAll("#foodPresetChips .chip-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const preset = PRESETS.food[btn.dataset.preset];
            if (!preset) return;
            document.getElementById("foodProtein").value = preset.protein;
            document.getElementById("foodCarbs").value = preset.carbs;
            document.getElementById("foodFat").value = preset.fat;
            document.getElementById("foodFiber").value = preset.fiber;
            document.getElementById("foodSugar").value = preset.sugar;
            showToast(`Loaded ${btn.textContent} preset`, "success");
        });
    });

    document.querySelectorAll("#fitnessPresetChips .chip-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const preset = PRESETS.fitness[btn.dataset.preset];
            if (!preset) return;
            if (preset.activity_type && document.getElementById("fitnessActivityType")) {
                document.getElementById("fitnessActivityType").value = preset.activity_type;
            }
            if (preset.duration && document.getElementById("fitnessDuration")) {
                document.getElementById("fitnessDuration").value = preset.duration;
            }
            if (preset.hr && document.getElementById("fitnessHeartRate")) {
                document.getElementById("fitnessHeartRate").value = preset.hr;
            }
            if (preset.weight && document.getElementById("fitnessWeight")) {
                document.getElementById("fitnessWeight").value = preset.weight;
            }
            if (preset.age && document.getElementById("fitnessAge")) {
                document.getElementById("fitnessAge").value = preset.age;
            }
            if (preset.gender && document.getElementById("fitnessGender")) {
                document.getElementById("fitnessGender").value = preset.gender;
            }
            if (preset.steps && document.getElementById("fitnessSteps")) {
                document.getElementById("fitnessSteps").value = preset.steps;
            }
            if (preset.sleep && document.getElementById("fitnessSleep")) {
                document.getElementById("fitnessSleep").value = preset.sleep;
            }
            showToast(`Loaded ${btn.textContent} preset`, "success");
        });
    });

    // 2. Context toggle
    const toggleBtn = document.getElementById("toggleContextBtn");
    const contextGrid = document.getElementById("contextGrid");
    const arrow = document.getElementById("contextArrow");
    if (toggleBtn && contextGrid) {
        toggleBtn.addEventListener("click", () => {
            contextGrid.classList.toggle("hidden");
            arrow.style.transform = contextGrid.classList.contains("hidden") ? "rotate(0deg)" : "rotate(180deg)";
        });
    }

    // 3. Food Form Submission
    const foodForm = document.getElementById("foodCalorieForm");
    foodForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const btn = document.getElementById("btnPredictFood");
        const origHTML = btn.innerHTML;
        btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Processing...`;
        btn.disabled = true;

        const protein = parseFloat(document.getElementById("foodProtein").value) || 0;
        const carbs = parseFloat(document.getElementById("foodCarbs").value) || 0;
        const fat = parseFloat(document.getElementById("foodFat").value) || 0;
        const fiber = parseFloat(document.getElementById("foodFiber").value) || 0;
        const sugar = parseFloat(document.getElementById("foodSugar").value) || 0;

        try {
            const resp = await fetch(`${API_BASE}/predict/food`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    protein: protein,
                    carbohydrates: carbs,
                    fat: fat,
                    fiber: fiber,
                    sugar: sugar
                })
            });

            const data = await resp.json();
            if (!resp.ok || !data.success) throw new Error(data.error || "Food prediction failed");

            // Show result
            const resultCard = document.getElementById("foodResultCard");
            resultCard.classList.remove("hidden");
            animateCount("foodCaloriesValue", data.prediction.calories, 1);

            const badge = document.getElementById("foodDensityBadge");
            badge.textContent = data.prediction.tier || "Moderate";
            badge.className = `badge-pill ${data.prediction.calories > 300 ? 'surplus' : 'deficit'}`;

            if (data.prediction.breakdown) {
                const b = data.prediction.breakdown;
                document.getElementById("barProteinPct").style.width = `${b.protein_pct}%`;
                document.getElementById("barCarbsPct").style.width = `${b.carbs_pct}%`;
                document.getElementById("barFatPct").style.width = `${b.fat_pct}%`;
                document.getElementById("legendProtein").textContent = `${b.protein_pct}%`;
                document.getElementById("legendCarbs").textContent = `${b.carbs_pct}%`;
                document.getElementById("legendFat").textContent = `${b.fat_pct}%`;
            }

            updateEnergyTotals(data.prediction.calories, 0);

            appendHistoryRow({
                category: "Food Intake",
                icon: "fa-utensils",
                categoryColor: "var(--color-food-dark)",
                inputs: `P: ${protein}g | C: ${carbs}g | F: ${fat}g`,
                energy: `+${data.prediction.calories} kcal`,
                details: data.prediction.tier
            });

            showToast(`Food Intake: ${data.prediction.calories} kcal predicted!`, "success");

        } catch (err) {
            showToast(err.message || "Prediction error", "error");
        } finally {
            btn.innerHTML = origHTML;
            btn.disabled = false;
        }
    });

    // 4. Fitness Form Submission
    const fitnessForm = document.getElementById("fitnessTrackerForm");
    fitnessForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const btn = document.getElementById("btnPredictFitness");
        const origHTML = btn.innerHTML;
        btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Calculating...`;
        btn.disabled = true;

        const activityType = document.getElementById("fitnessActivityType") ? document.getElementById("fitnessActivityType").value : "Running";
        const duration = parseFloat(document.getElementById("fitnessDuration") ? document.getElementById("fitnessDuration").value : 45) || 45;
        const heartRate = parseFloat(document.getElementById("fitnessHeartRate") ? document.getElementById("fitnessHeartRate").value : 135) || 135;
        const weight = parseFloat(document.getElementById("fitnessWeight") ? document.getElementById("fitnessWeight").value : 70) || 70;
        const age = parseFloat(document.getElementById("fitnessAge") ? document.getElementById("fitnessAge").value : 28) || 28;
        const gender = document.getElementById("fitnessGender") ? document.getElementById("fitnessGender").value : "Female";
        const steps = parseFloat(document.getElementById("fitnessSteps") ? document.getElementById("fitnessSteps").value : 5000) || 0;
        const sleep = parseFloat(document.getElementById("fitnessSleep") ? document.getElementById("fitnessSleep").value : 7.5) || 7.5;

        try {
            const resp = await fetch(`${API_BASE}/predict/fitness`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    activity_type: activityType,
                    duration_min: duration,
                    heart_rate_avg: heartRate,
                    weight_kg: weight,
                    age: age,
                    gender: gender,
                    steps: steps,
                    sleep_hours: sleep
                })
            });

            const data = await resp.json();
            if (!resp.ok || !data.success) throw new Error(data.error || "Fitness prediction failed");

            const resultCard = document.getElementById("fitnessResultCard");
            resultCard.classList.remove("hidden");
            animateCount("fitnessCaloriesValue", data.prediction.calories_burned, 1);
            
            if (document.getElementById("fitnessBurnRate")) {
                const rate = data.prediction.burn_rate_per_min || (data.prediction.calories_burned / duration);
                document.getElementById("fitnessBurnRate").textContent = rate.toFixed(2);
            }

            if (document.getElementById("fitnessDistanceValue")) {
                animateCount("fitnessDistanceValue", data.prediction.distance_km, 1);
            }

            const badge = document.getElementById("fitnessIntensityBadge");
            if (badge) {
                badge.textContent = data.prediction.intensity || "Moderate Burn";
                const badgeClass = data.prediction.calories_burned > 380 ? 'surplus' : (data.prediction.calories_burned < 200 ? 'deficit' : 'neutral');
                badge.className = `badge-pill ${badgeClass}`;
            }

            updateEnergyTotals(0, data.prediction.calories_burned);

            const iconMap = {
                "Running": "fa-person-running",
                "Yoga": "fa-spa",
                "Walking": "fa-person-walking",
                "Cycling": "fa-bicycle",
                "Swimming": "fa-person-swimming",
                "Hiit": "fa-bolt",
                "Strength Training": "fa-dumbbell"
            };
            const actIcon = iconMap[activityType] || "fa-person-running";

            appendHistoryRow({
                category: "Workout Burn",
                icon: actIcon,
                categoryColor: "var(--color-fitness-dark)",
                inputs: `${duration}m ${activityType} | HR: ${heartRate} bpm | ${weight}kg`,
                energy: `-${data.prediction.calories_burned} kcal`,
                details: `${data.prediction.distance_km} km (${data.prediction.intensity || 'Active'})`
            });

            showToast(`Workout: ${data.prediction.calories_burned} kcal burned predicted!`, "success");

        } catch (err) {
            showToast(err.message || "Fitness prediction error", "error");
        } finally {
            btn.innerHTML = origHTML;
            btn.disabled = false;
        }
    });

    // 5. Clear History Button
    const clearBtn = document.getElementById("btnClearHistory");
    if (clearBtn) {
        clearBtn.addEventListener("click", () => {
            state.history = [];
            state.totalIntake = 0;
            state.totalBurn = 0;
            updateEnergyTotals(0, 0);

            const tbody = document.getElementById("historyTableBody");
            tbody.innerHTML = `
                <tr class="table-empty-box" id="emptyHistoryRow">
                    <td colspan="6">
                        <div class="table-empty-box">
                            <i class="fa-solid fa-clipboard-list"></i>
                            <p>No predictions recorded yet. Fill out either form above to calculate and log results.</p>
                        </div>
                    </td>
                </tr>
            `;
            showToast("Session history cleared", "info");
        });
    }
}

// Update Energy Totals
function updateEnergyTotals(intakeDelta, burnDelta) {
    state.totalIntake += intakeDelta;
    state.totalBurn += burnDelta;

    const net = state.totalIntake - state.totalBurn;
    animateCount("summaryIntake", Math.round(state.totalIntake), 0);
    animateCount("summaryBurn", state.totalBurn, state.totalBurn % 1 === 0 ? 0 : 2);
    animateCount("summaryNet", net, net % 1 === 0 ? 0 : 2);

    const pill = document.getElementById("netStatusPill");
    if (net > 50) {
        pill.textContent = "Calorie Surplus";
        pill.className = "badge-pill surplus";
    } else if (net < -50) {
        pill.textContent = "Calorie Deficit";
        pill.className = "badge-pill deficit";
    } else {
        pill.textContent = "Equilibrium";
        pill.className = "badge-pill neutral";
    }

    const total = state.totalIntake + state.totalBurn;
    if (total > 0) {
        const inPct = Math.round((state.totalIntake / total) * 100);
        const burnPct = 100 - inPct;
        document.getElementById("ratioIntakePct").textContent = `${inPct}%`;
        document.getElementById("ratioBurnPct").textContent = `${burnPct}%`;
        document.getElementById("ratioFillFood").style.width = `${inPct}%`;
        document.getElementById("ratioFillBurn").style.width = `${burnPct}%`;
    }
}

// Append History Row
function appendHistoryRow(item) {
    const tbody = document.getElementById("historyTableBody");
    const emptyRow = document.getElementById("emptyHistoryRow");
    if (emptyRow) emptyRow.remove();

    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const tr = document.createElement("tr");
    tr.innerHTML = `
        <td style="color: var(--text-muted); font-size: 12px;">${timeStr}</td>
        <td>
            <span style="display:inline-flex; align-items:center; gap:6px; font-weight:600; color:${item.categoryColor}">
                <i class="fa-solid ${item.icon}"></i> ${item.category}
            </span>
        </td>
        <td><code>${item.inputs}</code></td>
        <td><strong style="color: var(--text-heading); font-size: 14px;">${item.energy}</strong></td>
        <td><span class="badge-pill neutral">${item.details}</span></td>
        <td><span style="color: #059669; font-size: 11px; font-weight: 700;"><i class="fa-solid fa-circle-check"></i> Predicted</span></td>
    `;
    tbody.insertBefore(tr, tbody.firstChild);
}

// ============================================================
// MODEL INFORMATION LOGIC (models.html)
// ============================================================
async function initModelInfo() {
    try {
        const resp = await fetch(`${API_BASE}/api/model-info`);
        const json = await resp.json();
        if (!json.success || !json.data) return;

        const data = json.data;

        // 1. Food Model
        if (data.food_model) {
            const fScores = data.food_model.performance_scores;
            const fConfusion = data.food_model.confusion_metrics;

            if (fScores) {
                document.getElementById("foodAccScore").textContent = `${(fScores.accuracy * 100).toFixed(2)}%`;
                document.getElementById("foodPrecScore").textContent = fScores.precision.toFixed(4);
                document.getElementById("foodRecScore").textContent = fScores.recall.toFixed(4);
                document.getElementById("foodF1Score").textContent = fScores.f1_score.toFixed(4);
                document.getElementById("foodR2Score").textContent = fScores.r2_score.toFixed(4);
                document.getElementById("foodMaeScore").innerHTML = `${fScores.mae} <small style="font-size:12px; font-weight:normal;">kcal</small>`;
                document.getElementById("foodRmseScore").innerHTML = `${fScores.rmse} <small style="font-size:12px; font-weight:normal;">kcal</small>`;
                document.getElementById("foodMseScore").textContent = fScores.mse;
            }

            if (fConfusion) {
                document.getElementById("foodTP").textContent = fConfusion.TP.toLocaleString();
                document.getElementById("foodTN").textContent = fConfusion.TN.toLocaleString();
                document.getElementById("foodFP").textContent = fConfusion.FP.toLocaleString();
                document.getElementById("foodFN").textContent = fConfusion.FN.toLocaleString();
            }
        }

        // 2. Fitness Model
        if (data.fitness_model) {
            const fitScores = data.fitness_model.performance_scores;
            const fitConfusion = data.fitness_model.confusion_metrics;

            if (data.fitness_model.algorithm && document.getElementById("fitnessAlgoTag")) {
                document.getElementById("fitnessAlgoTag").textContent = data.fitness_model.algorithm;
            }

            if (fitScores) {
                if (document.getElementById("fitnessAccScore")) {
                    document.getElementById("fitnessAccScore").textContent = `${(fitScores.accuracy * 100).toFixed(2)}%`;
                }
                if (document.getElementById("fitnessPrecScore")) {
                    document.getElementById("fitnessPrecScore").textContent = fitScores.precision.toFixed(4);
                }
                if (document.getElementById("fitnessRecScore")) {
                    document.getElementById("fitnessRecScore").textContent = fitScores.recall.toFixed(4);
                }
                if (document.getElementById("fitnessF1Score")) {
                    document.getElementById("fitnessF1Score").textContent = fitScores.f1_score.toFixed(4);
                }
                if (document.getElementById("fitnessR2Score")) {
                    document.getElementById("fitnessR2Score").textContent = fitScores.r2_score.toFixed(4);
                }
                if (document.getElementById("fitnessBurnMae")) {
                    const maeVal = fitScores.mae !== undefined ? fitScores.mae : fitScores.calories_burned_mae;
                    document.getElementById("fitnessBurnMae").innerHTML = `${maeVal} <small style="font-size:12px; font-weight:normal;">kcal</small>`;
                }
                if (document.getElementById("fitnessBurnRmse")) {
                    const rmseVal = fitScores.rmse !== undefined ? fitScores.rmse : fitScores.calories_burned_rmse;
                    document.getElementById("fitnessBurnRmse").innerHTML = `${rmseVal} <small style="font-size:12px; font-weight:normal;">kcal</small>`;
                }
                if (document.getElementById("fitnessMseScore")) {
                    document.getElementById("fitnessMseScore").textContent = (fitScores.mse || 0).toFixed(2);
                }
            }

            if (fitConfusion) {
                if (document.getElementById("fitnessTP")) document.getElementById("fitnessTP").textContent = fitConfusion.TP.toLocaleString();
                if (document.getElementById("fitnessTN")) document.getElementById("fitnessTN").textContent = fitConfusion.TN.toLocaleString();
                if (document.getElementById("fitnessFP")) document.getElementById("fitnessFP").textContent = fitConfusion.FP.toLocaleString();
                if (document.getElementById("fitnessFN")) document.getElementById("fitnessFN").textContent = fitConfusion.FN.toLocaleString();
            }
        }

    } catch (e) {
        console.warn("Using baked-in metrics on models.html", e);
    }
}

// ============================================================
// UTILITIES: COUNT ANIMATION & TOAST
// ============================================================
function animateCount(elementId, targetVal, decimals = 0) {
    const el = document.getElementById(elementId);
    if (!el) return;

    const startVal = parseFloat(el.textContent.replace(/,/g, "")) || 0;
    const duration = 400;
    const startTime = performance.now();

    function update(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const ease = 1 - Math.pow(1 - progress, 3);
        const current = startVal + (targetVal - startVal) * ease;

        el.textContent = decimals > 0 ? current.toFixed(decimals) : Math.round(current).toLocaleString();

        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            el.textContent = decimals > 0 ? targetVal.toFixed(decimals) : Math.round(targetVal).toLocaleString();
        }
    }

    requestAnimationFrame(update);
}

function showToast(msg, type = "info") {
    const shelf = document.getElementById("toastShelf");
    if (!shelf) return;

    const toast = document.createElement("div");
    toast.className = `toast-msg ${type}`;
    const icon = type === "success" ? "fa-circle-check" : type === "error" ? "fa-triangle-exclamation" : "fa-info";
    toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${msg}</span>`;

    shelf.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateX(20px)";
        toast.style.transition = "all 0.2s ease";
        setTimeout(() => toast.remove(), 200);
    }, 3500);
}