import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

# Set matplotlib style
plt.rcParams.update({
    'font.size': 12,
    'grid.color': 'gray',
    'grid.linestyle': '-',
    'grid.linewidth': 0.5,
    'grid.alpha': 0.3,
    'axes.linewidth': 1.5,
    'lines.linewidth': 2,
    'legend.frameon': True,
    'legend.framealpha':1.0
})

# Constants
STEP_HEIGHT = 1 # m

# Compare specified x/H locations for all grid levels
# Available x/H [1.0, 4.0, 6.0, 10.0]. Note - float type
# Available GRID_LEVEL [0, 1, 2, 3, 4]
X_H_LOCATIONS = [10.0]
GRID_LEVEL = [0, 1, 2, 3, 4]

# Assign colors
grid_colors = ['darkviolet', 'blue', 'darkgreen', 'orange', 'red' ]

# Initialize plot
fig, ax = plt.subplots(figsize=(15, 10))

# Plot validation data
for i in range(1, 23):
    file_path = f"ValidationData/backstep_csv/R.ST0/R.ST0_station_{i:02d}.csv"
    df = pd.read_csv(file_path, comment='#')
    
    # Extract x/H from file
    with open(file_path, 'r') as f:
        x_h = float(f.readlines()[2].split(":")[-1].strip())
    
    if x_h in X_H_LOCATIONS:
        ax.plot(df['U/Ur'].values, df['Y/H'].values,
                marker='o', linestyle='-', 
                label=f"Validation x/H = {x_h}",
                color='black')

# Plot OpenFOAM data
for GRID_LEVEL in GRID_LEVEL:
    file_path = f"ValidationData/post_data/grids/grid_{GRID_LEVEL}"

    # Load U_ref
    df_ref = pd.read_csv(f"{file_path}/Uref_U.mag_U.csv")
    U_REF = df_ref['U.mag'].values[0]
    
    for x_h in X_H_LOCATIONS:
        # Now load sampled x/H data
        df = pd.read_csv(f"{file_path}/x_by_h_{int(x_h):02d}_U.mag_U.csv")
        y_normalized = df['y'].values / STEP_HEIGHT # Normalize y by step height
        u_normalized = df['U.mag'].values / U_REF  # U_REF
        
        ax.plot(u_normalized, y_normalized, linestyle='dashdot',
                label=f"GL{GRID_LEVEL}",
                color=grid_colors[GRID_LEVEL])

# Format plot
ax.set_xlim(-0.4, 1.2)
ax.set_ylim(0, 3)
ax.set_xlabel("U/U₀")
ax.set_ylabel("y/h")
ax.set_title(f"U/U₀ Profiles at x/H={X_H_LOCATIONS[0]} and Grid Levels (GL)")
ax.grid(True)
ax.axvline(x=0, color='gray', linestyle='--', linewidth=1, alpha=0.7)
ax.legend(loc="upper left")

# Save and show
plt.savefig(f"ValidationData/Images/GridLevels_w_x_by_H_{int(X_H_LOCATIONS[0]):02d}.png", dpi=300, bbox_inches="tight")
plt.show()