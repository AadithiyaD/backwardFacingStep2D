import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm

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
colors = cm.tab10.colors
x_h_color_map = {x_h: colors[i] for i, x_h in enumerate(X_H_LOCATIONS)}

# Create 2x2 subplot grid
fig, axes = plt.subplots(2, 2, figsize=(15, 10))
axes = axes.flatten()  # Flatten to 1D array for easier indexing

# Create a dictionary to store data for each x/H
validation_data = {x_h: None for x_h in X_H_LOCATIONS}
openfoam_data = {x_h: None for x_h in X_H_LOCATIONS}

# Load validation data
for i in range(1, 23):
    file_path = f"ValidationData/backstep_csv/R.ST0/R.ST0_station_{i:02d}.csv"
    df = pd.read_csv(file_path, comment='#')
    
    # Extract x/H from file
    with open(file_path, 'r') as f:
        x_h = float(f.readlines()[2].split(":")[-1].strip())
    
    if x_h in X_H_LOCATIONS:
        validation_data[x_h] = df

# Load OpenFOAM data
for x_h in X_H_LOCATIONS:
    file_path = f"paraViewData/dataFromPV/x_h_{int(x_h)}.csv"
    df = pd.read_csv(file_path)
    
    df['y_normalized'] = df['arc_length'] / STEP_HEIGHT
    df['u_normalized'] = df['U:0'] / U_REF
    
    openfoam_data[x_h] = df

# Plot each x/H in its own subplot
for idx, x_h in enumerate(X_H_LOCATIONS):
    ax = axes[idx]
    
    # Plot validation data
    if validation_data[x_h] is not None:
        ax.plot(validation_data[x_h]['U/Ur'].values, 
                validation_data[x_h]['Y/H'].values, 
                '-', 
                label='Validation',
                color=x_h_color_map[x_h],
                linewidth=2)
    
    # Plot OpenFOAM data
    if openfoam_data[x_h] is not None:
        ax.plot(openfoam_data[x_h]['u_normalized'].values, 
                openfoam_data[x_h]['y_normalized'].values, 
                '--', 
                label='OpenFOAM',
                color=x_h_color_map[x_h],
                linewidth=2)
    
    # Format subplot
    ax.set_xlim(-0.4, 1.2)
    ax.set_ylim(0, 3)
    ax.set_xlabel("U/U₀")
    ax.set_ylabel("y/h")
    ax.set_title(f"x/H = {x_h}")
    ax.grid(True)
    ax.legend(loc="upper left")

# Add overall title
fig.suptitle("U/Ur Profiles at Different x/H Locations", fontsize=14, y=0.995)
plt.tight_layout()

# Save and show
plt.savefig("backwardStep2D_U_plotter_subplots.png", dpi=300, bbox_inches="tight")
plt.show()