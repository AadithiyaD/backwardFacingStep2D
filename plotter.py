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

# Initialize the plot
plt.figure(figsize=(15, 10))

for i in range(1, 23):
    # Load CSV into file_path
    file_path = f"ValidationData/backstep_csv/R.ST0/R.ST0_station_{i:02d}.csv"

    # Load csv data and skip comments
    df = pd.read_csv(file_path, comment='#')

    # Second column is y/h, rest are flow quantities
    y = df['Y/H']
    u = df['U/Ur']
    v = df['V/Ur']

    # Line 3 in csv has commented x/H position, read this
    with open(file_path, 'r') as file:
        lines = file.readlines()
        x_h_line = lines[2]
        x_h = float(x_h_line.split(":")[-1].strip())

        # Plot only for specified x/H values
        if x_h in [1.0, 4.0, 6.0, 10.0]:  # Compare as floats
            plt.plot(u, y, '-', label=f"x/H = {x_h}")

# Set axis ranges to match gnuplot
plt.xlim(-0.4, 1.2)
plt.ylim(0, 3)


# Add labels, title, legend, and grid
plt.xlabel("U/U₀")
plt.ylabel("y/h")
plt.title("U/Ur Profiles at Different x/H Locations")
plt.grid(True)
plt.legend(loc="upper left")

# Save the plot to match gnuplot output
plt.savefig("backwardStep2D_U_plottter.png", dpi=300, bbox_inches="tight")
plt.show()