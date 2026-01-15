#!/usr/bin/env python3
"""
Script to compare velocity magnitudes from simulation and experimental data
at different x/H locations for backward facing step case.
"""

#! TO BE IGNORED IN GIT ADD

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Configuration
U_ref = 44.2  # Reference velocity in m/s
data_dir = 'dataForOptLoop'

# Mapping between x_by_h files and R.ST0_station files
sample_expt_map = {
    1: 5,
    4: 10,
    6: 13,
    10: 17
}

# Create output directory for plots
output_dir = 'velocity_comparison_plots'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


def load_simulation_data(x_by_h_num):
    """Load simulation data from x_by_h_* file."""
    filename = os.path.join(data_dir, f'x_by_h_{x_by_h_num:02d}_U.csv')
    try:
        df = pd.read_csv(filename)
        return df
    except FileNotFoundError:
        print(f"Warning: {filename} not found")
        return None


def load_experimental_data(station_num):
    """Load experimental data from R.ST0_station_* file."""
    filename = os.path.join(data_dir, f'R.ST0_station_{station_num:02d}.csv')
    try:
        # Skip header lines starting with #
        df = pd.read_csv(filename, comment='#')
        return df
    except FileNotFoundError:
        print(f"Warning: {filename} not found")
        return None


def calculate_velocity_magnitude_sim(df):
    """
    Calculate velocity magnitude from simulation data.
    Input columns: y, U_0, U_1, U_2 (velocity components in m/s)
    """
    U_mag = np.sqrt(df['U_0']**2 + df['U_1']**2 + df['U_2']**2)
    U_mag_nondim = U_mag / U_ref
    return df['y'].values, U_mag_nondim.values


def calculate_velocity_magnitude_expt(df):
    """
    Calculate velocity magnitude from experimental data.
    Input columns: U/Ur, V/Ur (already non-dimensionalized)
    Assumes 2D flow, so W/Ur = 0
    """
    U_mag_nondim = np.sqrt(df['U/Ur']**2 + df['V/Ur']**2)
    return df['Y/H'].values, U_mag_nondim.values


def plot_comparison(x_by_h_num, station_num):
    """
    Create comparison plot for a single x/H location.
    """
    # Load data
    sim_data = load_simulation_data(x_by_h_num)
    expt_data = load_experimental_data(station_num)
    
    if sim_data is None or expt_data is None:
        print(f"Skipping x_by_h_{x_by_h_num:02d} (station {station_num}): missing data")
        return False
    
    # Calculate velocity magnitudes
    y_sim, U_mag_sim = calculate_velocity_magnitude_sim(sim_data)
    y_expt, U_mag_expt = calculate_velocity_magnitude_expt(expt_data)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Plot both datasets
    ax.plot(U_mag_sim, y_sim, 'b-', linewidth=2, label='CFD Simulation', marker='o', markersize=3, alpha=0.7)
    ax.plot(U_mag_expt, y_expt, 'r--', linewidth=2, label='Experimental', marker='s', markersize=5, alpha=0.7)
    
    # Labels and title
    ax.set_xlabel('Velocity Magnitude (normalized by U_ref = 44.2 m/s)', fontsize=12)
    ax.set_xbound(lower=-0.4, upper=1.2)
    ax.set_ylabel('Y/H', fontsize=12)
    ax.set_ybound(lower=0, upper=3)
    ax.set_title(f'Velocity Magnitude Comparison at X/H = {x_by_h_num}', fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=11)
    ax.grid(True, alpha=0.3)
    
    # Save figure
    output_file = os.path.join(output_dir, f'velocity_comparison_x_by_h_{x_by_h_num:02d}.png')
    fig.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    
    plt.close(fig)
    return True


def plot_all_locations():
    """
    Create a single plot showing velocity profiles at all x/H locations as subplots.
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    plot_idx = 0
    for x_by_h_num, station_num in sample_expt_map.items():
        # Load data
        sim_data = load_simulation_data(x_by_h_num)
        expt_data = load_experimental_data(station_num)
        
        if sim_data is None or expt_data is None:
            print(f"Skipping x_by_h_{x_by_h_num:02d} in combined plot")
            continue
        
        # Calculate velocity magnitudes
        y_sim, U_mag_sim = calculate_velocity_magnitude_sim(sim_data)
        y_expt, U_mag_expt = calculate_velocity_magnitude_expt(expt_data)
        
        # Plot on subplot
        ax = axes[plot_idx]
        ax.plot(U_mag_sim, y_sim, 'b-', linewidth=2, label='CFD', marker='o', markersize=3, alpha=0.7)
        ax.plot(U_mag_expt, y_expt, 'r--', linewidth=2, label='Experiment', marker='s', markersize=5, alpha=0.7)
        
        ax.set_xlabel('U Magnitude (normalized)', fontsize=10)
        ax.set_xbound(lower=-0.4, upper=1.2)
        ax.set_ylabel('Y/H', fontsize=10)
        ax.set_ybound(lower=0, upper=3)
        ax.set_title(f'X/H = {x_by_h_num}', fontsize=11, fontweight='bold')
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)
        
        plot_idx += 1
    
    fig.suptitle('Velocity Magnitude Profiles at Different X/H Locations', 
                 fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    output_file = os.path.join(output_dir, 'velocity_comparison_all_locations.png')
    fig.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    
    plt.close(fig)


def plot_all_locations_single():
    """
    Create a single plot with all x/H locations overlaid.
    - Each x/H has a different color (consistent for CFD and experimental)
    - CFD data plotted as lines (no markers)
    - Experimental data plotted as markers only (no lines)
    - Different markers for each x/H location
    """
    # Define colors and markers for each x/H location
    colors = {
        1: '#e74c3c',      # Red
        4: '#2ecc71',      # Green
        6: '#3498db',      # Blue
        10: '#f39c12'      # Orange
    }
    
    markers = {
        1: 's',            # Square
        4: 'o',            # Circle
        6: '^',            # Triangle up
        10: 'v'            # Triangle down
    }
    
    fig, ax = plt.subplots(figsize=(12, 9))
    
    for x_by_h_num, station_num in sorted(sample_expt_map.items()):
        # Load data
        sim_data = load_simulation_data(x_by_h_num)
        expt_data = load_experimental_data(station_num)
        
        if sim_data is None or expt_data is None:
            print(f"Skipping x_by_h_{x_by_h_num:02d} in single plot")
            continue
        
        # Calculate velocity magnitudes
        y_sim, U_mag_sim = calculate_velocity_magnitude_sim(sim_data)
        y_expt, U_mag_expt = calculate_velocity_magnitude_expt(expt_data)
        
        # Get color and marker for this x/H location
        color = colors[x_by_h_num]
        marker = markers[x_by_h_num]
        
        # Plot CFD data as solid lines (no markers)
        ax.plot(U_mag_sim, y_sim, color=color, linewidth=2.5, 
               label=f'CFD X/H={x_by_h_num}', alpha=0.85)
        
        # Plot experimental data as markers only (no line)
        ax.scatter(U_mag_expt, y_expt, color=color, marker=marker, s=100,
                  label=f'Expt X/H={x_by_h_num}', alpha=0.8, edgecolors='black', linewidth=1)
    
    # Labels and title
    ax.set_xlabel('Velocity Magnitude (normalized by U_ref = 44.2 m/s)', fontsize=13, fontweight='bold')
    ax.set_xbound(lower=-0.4, upper=1.2)
    ax.set_ylabel('Y/H', fontsize=13, fontweight='bold')
    ax.set_ybound(lower=0, upper=3)
    ax.set_title('Velocity Magnitude Comparison at All X/H Locations', fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10, ncol=2, framealpha=0.95)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(-0.5, 1.3)
    
    # Save figure
    output_file = os.path.join(output_dir, 'velocity_comparison_single_plot.png')
    fig.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    
    plt.close(fig)


if __name__ == '__main__':
    print("Starting velocity magnitude comparison analysis...")
    print(f"Using reference velocity U_ref = {U_ref} m/s\n")
    
    # Create individual plots for each x/H location
    print("Creating individual plots for each x/H location:")
    for x_by_h_num, station_num in sample_expt_map.items():
        plot_comparison(x_by_h_num, station_num)
    
    print("\nCreating combined comparison plot (subplots)...")
    # Create combined subplot plot
    plot_all_locations()
    
    print("Creating single overlaid plot for all x/H locations...")
    # Create single plot with all locations overlaid
    plot_all_locations_single()
    
    print("\nAnalysis complete!")
    print(f"All plots saved in '{output_dir}' directory")
