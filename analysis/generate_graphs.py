import pandas as pd
import matplotlib.pyplot as plt
import os

# Ensure output directories exist
os.makedirs("outputs/graphs", exist_ok=True)

# ===============================
# Load CSV files
# ===============================
knock_df = pd.read_csv("data/B_level_full_knock_sweep.csv")
b2_df = pd.read_csv("data/B_level_phase_B2_knock_integral.csv")
extreme_df = pd.read_csv("data/random_environment_extreme_test.csv")

# ===============================
# Graph 1: Knock Integral vs RPM
# ===============================
plt.figure(figsize=(8, 5))
for cr in sorted(knock_df["CR"].unique()):
    sub = knock_df[knock_df["CR"] == cr]
    plt.plot(sub["RPM"], sub["Max_KI"], marker="o", label=f"CR={cr}")

plt.xlabel("RPM")
plt.ylabel("Max Knock Integral (KI)")
plt.title("Knock Integral vs RPM (Boundary Proximity)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("outputs/graphs/ki_vs_rpm.png", dpi=150)
plt.close()

# ===============================
# Graph 2: End-Gas Temperature vs Theta
# ===============================
plt.figure(figsize=(8, 5))
plt.plot(b2_df["Theta_deg"], b2_df["EndGas_Temperature_K"])
plt.xlabel("Crank Angle (deg)")
plt.ylabel("End-Gas Temperature (K)")
plt.title("End-Gas Temperature Evolution")
plt.grid(True)
plt.tight_layout()
plt.savefig("outputs/graphs/endgas_temp_vs_theta.png", dpi=150)
plt.close()

# ===============================
# Graph 3: Pressure comparison
# ===============================
plt.figure(figsize=(8, 5))
plt.plot(
    b2_df["Theta_deg"],
    b2_df["Pressure_Pa"] / 1e5,
    label="B-Level Kernel"
)

plt.scatter(
    range(len(extreme_df)),
    extreme_df["PeakPressure_Pa"] / 1e5,
    label="Extreme Environment Peaks",
    alpha=0.7
)

plt.xlabel("Theta / Scenario Index")
plt.ylabel("Pressure (bar)")
plt.title("Pressure Discipline Comparison")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("outputs/graphs/pressure_comparison.png", dpi=150)
plt.close()

print("Graphs generated in outputs/graphs/")
