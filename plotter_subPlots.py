import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm

# Set matplotlib style
plt.rcParams.update({
    'font.size': 10,
    'grid.color': 'gray',
    'grid.linestyle': '--',
    'grid.linewidth': 0.5,
    'axes.linewidth': 1.5,
    'lines.linewidth': 2,
    'legend.frameon': False
})

# Compare specified grid levels for all x/H locations
# Available x/H [1.0, 4.0, 6.0, 10.0]. Note - float type
# Available GRID_LEVEL [0, 1, 2, 3, 4]
STEP_HEIGHT = 1 # m
X_H_LOCATIONS = [1.0, 4.0, 6.0, 10.0]
GRID_LEVEL = 4

# Assign colors for each x/H location
grid_colors = ['darkviolet', 'blue', 'darkgreen', 'orange', 'red' ]

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
file_path = f"ValidationData/post_data/grids/grid_{GRID_LEVEL}"

# Load U_ref
df_ref = pd.read_csv(f"{file_path}/Uref_U.mag_U.csv")
U_REF = df_ref['U.mag'].values[0]

for x_h in X_H_LOCATIONS:
    # Now load sampled x/H data
    df = pd.read_csv(f"{file_path}/x_by_h_{int(x_h):02d}_U.mag_U.csv")
    df['y_normalized'] = df['y'].values / STEP_HEIGHT # Normalize y by step height
    df['u_normalized'] = df['U.mag'].values / U_REF  # U_REF

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
                color='black',
                linewidth=2)
    
    # Plot OpenFOAM data
    if openfoam_data[x_h] is not None:
        ax.plot(openfoam_data[x_h]['u_normalized'].values, 
                openfoam_data[x_h]['y_normalized'].values, 
                '--', 
                label=f'GL{GRID_LEVEL}',
                color=grid_colors[GRID_LEVEL],
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
fig.suptitle(f"UU/U₀ Profiles for all x/H at Grid Level {GRID_LEVEL} ", fontsize=14, y=0.995)
plt.tight_layout()

# Save and show
plt.savefig(f"alidationData/Images/U_subplots_GridLevel_{GRID_LEVEL}.png", dpi=300, bbox_inches="tight")
plt.show()