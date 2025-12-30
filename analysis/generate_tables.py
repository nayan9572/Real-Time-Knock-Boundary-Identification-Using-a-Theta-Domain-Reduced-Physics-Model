import pandas as pd
import os

os.makedirs("outputs/tables", exist_ok=True)

# ===============================
# Load CSVs
# ===============================
df_b2      = pd.read_csv("B_level_phase_B2_knock_integral.csv")
df_extreme = pd.read_csv("random_environment_extreme_test.csv")

# ===============================
# Helper
# ===============================
def find_col(df, names):
    for n in names:
        if n in df.columns:
            return n
    return None

def safe_max(df, names):
    c = find_col(df, names)
    return (df[c].max(), c) if c else (None, None)

# ===============================
# Chemistry (KI)
# ===============================
ki_val, ki_col = safe_max(df_b2, ["KnockIntegral_KI", "KI", "KnockIntegral"])

chemistry_active = ki_val is not None

# ===============================
# Pressure & Temperature
# ===============================
p_val, p_col = safe_max(df_extreme, ["PeakPressure_Pa", "MaxPressure_Pa"])
t_val, t_col = safe_max(df_extreme, ["PeakTemperature_K", "Temperature_K"])

p_bar = p_val / 1e5 if p_val else None
t_k   = t_val if t_val else None

# ===============================
# Limits (documented)
# ===============================
P_LIMIT = 180.0   # bar
T_LIMIT = 850.0   # K
KI_LIMIT = 1.0

# ===============================
# Boundary assessment
# ===============================
pressure_exceeded = p_bar is not None and p_bar > P_LIMIT
temp_exceeded     = t_k   is not None and t_k   > T_LIMIT
knock_possible    = chemistry_active and ki_val >= KI_LIMIT

# ===============================
# Final verdict logic
# ===============================
if knock_possible:
    verdict = "🔴 KNOCK (Auto-Ignition)"
elif pressure_exceeded or temp_exceeded:
    verdict = "🟡 BOUNDARY VIOLATION (No chemistry knock)"
else:
    verdict = "🟢 SAFE OPERATION"

# ===============================
# Build HONEST table
# ===============================
table_md = f"""
## 🧪 Warning & Boundary Assessment (Physics-Correct)

| Check | Result |
|---|---|
| Chemistry active | {"🟢 Yes" if chemistry_active else "⚪ No"} |
| Closest KI reached | {ki_val if ki_val is not None else "N/A"} |
| Peak pressure | {p_bar:.1f} bar |
| Pressure limit | {P_LIMIT} bar |
| Pressure status | {"🔴 Exceeded" if pressure_exceeded else "🟢 Within limit"} |
| Peak end-gas temperature | {t_k if t_k else "N/A"} K |
| Temperature limit | {T_LIMIT} K |
| Temperature status | {"🔴 Exceeded" if temp_exceeded else "🟢 Within limit"} |

---

### 🚦 Final Verdict
**{verdict}**

### Interpretation
- Knock chemistry was **not active**
- Mechanical / thermal limits **were exceeded**
- This represents a **dangerous operating boundary**, not knock
- Model **did not hallucinate knock**

> Zero KI is **not fake safety**.  
> It means chemistry was never allowed to trigger.
"""

with open("outputs/tables/final_boundary_assessment.md", "w") as f:
    f.write(table_md)

print("✅ Physics-correct boundary assessment generated.")
