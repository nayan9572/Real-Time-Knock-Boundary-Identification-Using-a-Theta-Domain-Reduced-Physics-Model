import pandas as pd
import os

os.makedirs("outputs/tables", exist_ok=True)

# -------------------------------
# Load CSVs
# -------------------------------
df_sweep   = pd.read_csv("data/B_level_full_knock_sweep.csv")
df_b2      = pd.read_csv("data/B_level_phase_B2_knock_integral.csv")
df_extreme = pd.read_csv("data/random_environment_extreme_test.csv")
df_window  = pd.read_csv("data/knock_window_isolation_sweep.csv")

# -------------------------------
# Helpers
# -------------------------------
def find_col(df, names):
    for n in names:
        if n in df.columns:
            return n
    return None

def safe_max(df, names):
    c = find_col(df, names)
    return (df[c].max(), c) if c else (None, None)

# -------------------------------
# Extract signals
# -------------------------------
# Knock (explicit)
knock_col = find_col(df_sweep, ["Knock", "KnockDetected"])
actual_knock = int(df_sweep[knock_col].sum()) if knock_col else 0

# KI (chemistry proximity)
ki_b2, ki_b2_col   = safe_max(df_b2, ["KnockIntegral_KI", "KI", "KnockIntegral"])
ki_win, ki_win_col = safe_max(df_window, ["Max_KI", "KI", "KnockIntegral"])
closest_KI = max([v for v in [ki_b2, ki_win] if v is not None], default=0.0)

# Pressure
p_ext, p_ext_col = safe_max(df_extreme, ["PeakPressure_Pa", "MaxPressure_Pa"])
p_b2,  p_b2_col  = safe_max(df_b2, ["Pressure_Pa", "CylinderPressure_Pa"])
p_ext = (p_ext/1e5) if p_ext is not None else None
p_b2  = (p_b2/1e5)  if p_b2  is not None else None
peak_pressure = max([v for v in [p_ext, p_b2] if v is not None], default=None)

# Temperature
t_b2, t_b2_col   = safe_max(df_b2, ["EndGas_Temperature_K", "Temperature_K"])
t_ext, t_ext_col = safe_max(df_extreme, ["PeakTemperature_K", "Temperature_K"])
peak_temp = max([v for v in [t_b2, t_ext] if v is not None], default=None)

# -------------------------------
# TEST thresholds (documented)
# -------------------------------
KI_LIMIT = 1.0
P_LIMIT  = 180.0   # bar (stress)
T_LIMIT  = 850.0   # K (end-gas)

# -------------------------------
# Margins (% to limit)
# -------------------------------
ki_margin = (closest_KI / KI_LIMIT)*100 if KI_LIMIT else 0
p_margin  = (peak_pressure / P_LIMIT)*100 if peak_pressure else 0
t_margin  = (peak_temp / T_LIMIT)*100 if peak_temp else 0

# -------------------------------
# Warning logic (TEST MODE)
# -------------------------------
warnings = []
if ki_margin >= 70: warnings.append("🟡 Chemistry proximity")
if p_margin  >= 80: warnings.append("🟡 Pressure stress")
if t_margin  >= 80: warnings.append("🟡 Thermal stress")

if actual_knock > 0:
    state = "🔴 KNOCK DETECTED"
elif warnings:
    state = "🟡 WARNING / BOUNDARY ZONE"
else:
    state = "🟢 SAFE OPERATION"

# -------------------------------
# Build table
# -------------------------------
table_md = f"""
## 🧪 Warning & Boundary Test (CSV-Driven)

| Metric | Value |
|---|---|
| Actual knock events | 🔴 **{actual_knock}** |
| Closest KI reached | **{closest_KI:.3f}** |
| KI margin to knock | **{ki_margin:.1f}%** |
| Peak pressure | **{peak_pressure if peak_pressure else "N/A"} bar** |
| Pressure margin | **{p_margin:.1f}%** |
| Peak end-gas temperature | **{peak_temp if peak_temp else "N/A"} K** |
| Temperature margin | **{t_margin:.1f}%** |

### ⚠️ Warnings
{("- " + "\\n- ".join(warnings)) if warnings else "🟢 None (within margins)"}

### 🚦 Final Verdict
**{state}**

> Zero knock indicates **limits not crossed**.  
> Margins quantify **how close** the system operated.
"""

with open("outputs/tables/test_warning_boundary_summary.md", "w") as f:
    f.write(table_md)

print("✅ Warning & boundary test summary generated.")
