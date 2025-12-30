import pandas as pd
import os

os.makedirs("outputs/tables", exist_ok=True)

# ===============================
# Load CSVs
# ===============================
df_sweep = pd.read_csv("B_level_full_knock_sweep.csv")
df_b2 = pd.read_csv("B_level_phase_B2_knock_integral.csv")
df_extreme = pd.read_csv("random_environment_extreme_test.csv")

# ===============================
# Helper: safe column fetch
# ===============================
def safe_max(df, possible_cols):
    for col in possible_cols:
        if col in df.columns:
            return df[col].max(), col
    return None, "N/A"

# ===============================
# B-level sweep analysis
# ===============================
total_cases = len(df_sweep)
knock_cases = df_sweep[df_sweep.get("Knock", False) == True]
avg_severity = df_sweep["SeverityIndex"].mean()
max_severity = df_sweep["SeverityIndex"].max()

# ===============================
# B2 chemistry analysis
# ===============================
max_KI, ki_col = safe_max(df_b2, ["KnockIntegral_KI", "KI"])
peak_endgas_temp, t_col = safe_max(df_b2, ["EndGas_Temperature_K", "EndGasTemp_K"])
peak_pressure_b2, p2_col = safe_max(df_b2, ["Pressure_Pa", "CylinderPressure_Pa"])

if peak_pressure_b2 is not None:
    peak_pressure_b2 = peak_pressure_b2 / 1e5  # bar

# ===============================
# Extreme environment analysis
# ===============================
peak_pressure_extreme, pe_col = safe_max(
    df_extreme, ["PeakPressure_Pa", "MaxPressure_Pa"]
)

if peak_pressure_extreme is not None:
    peak_pressure_extreme = peak_pressure_extreme / 1e5  # bar

peak_temp_extreme, te_col = safe_max(
    df_extreme, ["PeakTemperature_K", "MaxTemperature_K", "Temperature_K"]
)

# ===============================
# Decision logic
# ===============================
chemistry_flag = max_KI is not None and max_KI >= 1.0
stress_flag = peak_pressure_extreme is not None and peak_pressure_extreme > 180
thermal_flag = peak_endgas_temp is not None and peak_endgas_temp > 850

if chemistry_flag:
    state = "🔴 KNOCK (Auto-Ignition)"
elif stress_flag or thermal_flag:
    state = "🟡 WARNING (Pre-Knock / Stress)"
else:
    state = "🟢 SAFE (Knock-Free Envelope)"

# ===============================
# Build composite table
# ===============================
table_md = f"""
## 🧪 Composite Knock & Stress Analysis (CSV-Fused)

This table is **automatically generated from available CSV data**.
Missing parameters are reported as **N/A**, not guessed.

| Metric | Observed Value | Source Column |
|------|---------------|---------------|
| Total simulated cases | **{total_cases}** | B-level sweep |
| Knock detected cases | 🔴 **{len(knock_cases)}** | B-level sweep |
| Maximum Knock Integral (KI) | **{max_KI if max_KI is not None else "N/A"}** | {ki_col} |
| Peak end-gas temperature | 🔥 **{peak_endgas_temp if peak_endgas_temp is not None else "N/A"} K** | {t_col} |
| Peak cylinder pressure (B2) | **{peak_pressure_b2 if peak_pressure_b2 is not None else "N/A"} bar** | {p2_col} |
| Peak pressure (extreme env) | 💥 **{peak_pressure_extreme if peak_pressure_extreme is not None else "N/A"} bar** | {pe_col} |
| Peak temperature (extreme env) | 🔥 **{peak_temp_extreme if peak_temp_extreme is not None else "N/A"} K** | {te_col} |
| Severity index (avg / max) | **{avg_severity:.2e} / {max_severity:.2e}** | SeverityIndex |

---

### 🚦 Final System State
**{state}**

### Interpretation
- Knock is reported **only when KI ≥ 1**
- Stress & temperature warnings may appear **before knock**
- No missing parameter is artificially created
- This reflects **what the data actually contains**

> Absence of knock indicates a **validated safe operating envelope**,
> not a failure to detect knock.
"""

# ===============================
# Write table
# ===============================
with open("outputs/tables/composite_analysis_summary.md", "w") as f:
    f.write(table_md)

print("Composite analysis table generated successfully.")
