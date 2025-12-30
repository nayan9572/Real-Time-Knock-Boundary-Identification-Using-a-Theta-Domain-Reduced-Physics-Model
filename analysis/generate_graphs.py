
# No ego. No marketing.  
# **Scientist tone.**



# 📈 `analysis/generate_graphs.py` (REAL GRAPH CODE)

```python
import pandas as pd
import matplotlib.pyplot as plt
import os

os.makedirs("outputs/graphs", exist_ok=True)

# ---------- Load CSVs ----------
knock = pd.read_csv("data/B_level_full_knock_sweep.csv")
b2 = pd.read_csv("data/B_level_phase_B2_knock_integral.csv")
extreme = pd.read_csv("data/random_environment_extreme_test.csv")

# ---------- Graph 1: KI vs RPM ----------
plt.figure()
for cr in sorted(knock["CR"].unique()):
    sub = knock[knock["CR"] == cr]
    plt.plot(sub["RPM"], sub["Max_KI"], marker="o", label=f"CR={cr}")

plt.xlabel("RPM")
plt.ylabel("Max Knock Integral (KI)")
plt.title("Knock Proximity vs RPM")
plt.legend()
plt.savefig("outputs/graphs/ki_vs_rpm.png", dpi=150)
plt.close()

# ---------- Graph 2: End-gas temperature ----------
plt.figure()
plt.plot(b2["Theta_deg"], b2["EndGas_Temperature_K"])
plt.xlabel("Crank Angle (deg)")
plt.ylabel("End-Gas Temperature (K)")
plt.title("End-Gas Temperature Evolution")
plt.savefig("outputs/graphs/endgas_temp_vs_theta.png", dpi=150)
plt.close()

# ---------- Graph 3: Pressure comparison ----------
plt.figure()
plt.plot(b2["Theta_deg"], b2["Pressure_Pa"]/1e5, label="B-Level Model")
plt.scatter(range(len(extreme)), extreme["PeakPressure_Pa"]/1e5,
            label="Extreme Env Peaks")
plt.ylabel("Pressure (bar)")
plt.legend()
plt.title("Pressure Discipline Comparison")
plt.savefig("outputs/graphs/pressure_comparison.png", dpi=150)
plt.close()
