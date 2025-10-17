import pandas as pd
import matplotlib.pyplot as plt

# Set matplotlib style
plt.rcParams.update({
    'font.family': 'serif',
    'font.sans-serif': 'Faculty Glyphic',
    'font.size': 10,
    'grid.color': 'gray',
    'grid.linestyle': '--',
    'grid.linewidth': 0.5,
    'axes.linewidth': 1.5,
    'lines.linewidth': 2,
    'legend.frameon': False
})

# Constants
STEP_HEIGHT = 0.0127  # m
U_REF = 46.6  # m/s
X_H_LOCATIONS = [1.0, 4.0, 6.0, 10.0]

# Assign colors for each x/H location
from matplotlib import cm
colors = cm.tab10.colors  # 10 distinct colors
x_h_color_map = {x_h: colors[i] for i, x_h in enumerate(X_H_LOCATIONS)}


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
        ax.plot(df['U/Ur'].values, df['Y/H'].values, '-', 
                label=f"Validation x/H = {x_h}",
                color=x_h_color_map[x_h])

# Plot OpenFOAM data
for x_h in X_H_LOCATIONS:
    file_path = f"paraViewData/dataFromPV/x_h_{int(x_h)}.csv"
    df = pd.read_csv(file_path)
    
    y_normalized = df['arc_length'] / STEP_HEIGHT
    u_normalized = df['U:0'] / U_REF
    
    ax.plot(u_normalized.values, y_normalized.values, '--', 
            label=f"OpenFOAM x/H = {x_h}",
            color=x_h_color_map[x_h])

# Format plot
ax.set_xlim(-0.4, 1.2)
ax.set_ylim(0, 3)
ax.set_xlabel("U/U₀")
ax.set_ylabel("y/h")
ax.set_title("U/Ur Profiles at Different x/H Locations")
ax.grid(True)
ax.legend(loc="upper left")

# Save and show
plt.savefig("backwardStep2D_U_plotter.png", dpi=300, bbox_inches="tight")
plt.show()