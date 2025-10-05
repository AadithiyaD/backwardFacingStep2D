import re
import csv
import os

def parse_backstep_data(filename):
    """
    Parse the backwards step experimental data file and create CSV files for each station.
    """
    
    # Read the file
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Dictionary to store data for each case and station
    data_dict = {}
    current_case = None
    current_station = None
    current_metadata = {}
    collecting_data = False
    data_rows = []
    
    for i, line in enumerate(lines):
        # Check for case and station header
        case_station_match = re.match(r'\s*TABLE\s+C\.\s*\d+\s*(?:\(cont\.\))?\s+CASE\s+(\S+)\s+Station=\s*(\d+)', line)
        if case_station_match:
            # Save previous data if exists
            if current_case and current_station and data_rows:
                key = (current_case, current_station)
                data_dict[key] = {
                    'metadata': current_metadata.copy(),
                    'data': data_rows.copy()
                }
            
            # Start new case/station
            current_case = case_station_match.group(1)
            current_station = int(case_station_match.group(2))
            current_metadata = {}
            data_rows = []
            collecting_data = False
            continue
        
        # Check for metadata lines
        if current_case and current_station:
            # X/H line
            xh_match = re.match(r'\s*X/H=\s*([-\d.]+)', line)
            if xh_match:
                current_metadata['X/H'] = float(xh_match.group(1))
                continue
            
            # Tunnel Run line
            run_match = re.match(r'\s*Tunnel Run#=\s*(\d+)', line)
            if run_match:
                current_metadata['Tunnel_Run'] = int(run_match.group(1))
                continue
            
            # Ue/Uref line
            ue_match = re.match(r'\s*Ue/Uref=\s*([\d.]+)', line)
            if ue_match:
                current_metadata['Ue/Uref'] = float(ue_match.group(1))
                continue
            
            # Wall case line
            wall_match = re.match(r'\s*(.*Wall case.*)', line)
            if wall_match:
                current_metadata['Wall_Case'] = wall_match.group(1).strip()
                continue
            
            # Check for column headers
            if 'LR' in line and 'Y/H' in line and 'U/Ur' in line:
                collecting_data = True
                continue
            
            # Parse data rows
            if collecting_data:
                # Split line and check if it's a data row
                parts = line.split()
                if len(parts) >= 11 and parts[0].isdigit():
                    try:
                        row = {
                            'LR': int(parts[0]),
                            'Y/H': float(parts[1]),
                            'U/Ur': float(parts[2]),
                            'V/Ur': float(parts[3]),
                            'uu': float(parts[4]),
                            'vv': float(parts[5]),
                            'uv': float(parts[6]),
                            'uuu': float(parts[7]),
                            'uvv': float(parts[8]),
                            'vuu': float(parts[9]),
                            'vvv': float(parts[10])
                        }
                        data_rows.append(row)
                    except (ValueError, IndexError):
                        # Skip lines that don't parse as data
                        pass
    
    # Save last station data
    if current_case and current_station and data_rows:
        key = (current_case, current_station)
        data_dict[key] = {
            'metadata': current_metadata.copy(),
            'data': data_rows.copy()
        }
    
    return data_dict

def write_csv_files(data_dict, output_dir='backstep_csv'):
    """
    Write the parsed data to CSV files, one per station for each case.
    """
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Group by case
    cases = {}
    for (case, station), data in data_dict.items():
        if case not in cases:
            cases[case] = {}
        cases[case][station] = data
    
    # Write CSV files for each case
    for case, stations in cases.items():
        # Create case subdirectory
        case_dir = os.path.join(output_dir, case)
        if not os.path.exists(case_dir):
            os.makedirs(case_dir)
        
        for station, station_data in sorted(stations.items()):
            # Create filename
            filename = os.path.join(case_dir, f'{case}_station_{station:02d}.csv')
            
            # Write CSV
            with open(filename, 'w', newline='') as csvfile:
                # Write metadata as comments
                csvfile.write(f'# Case: {case}\n')
                csvfile.write(f'# Station: {station}\n')
                for key, value in station_data['metadata'].items():
                    csvfile.write(f'# {key}: {value}\n')
                csvfile.write('#\n')
                
                # Write column headers and data
                if station_data['data']:
                    fieldnames = ['LR', 'Y/H', 'U/Ur', 'V/Ur', 'uu', 'vv', 'uv', 'uuu', 'uvv', 'vuu', 'vvv']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(station_data['data'])
            
            print(f'Created: {filename}')
    
    # Also create a combined CSV for each case with all stations
    for case, stations in cases.items():
        combined_filename = os.path.join(case_dir, f'{case}_all_stations.csv')
        
        with open(combined_filename, 'w', newline='') as csvfile:
            csvfile.write(f'# Case: {case} - All Stations Combined\n')
            csvfile.write('#\n')
            
            # Write header
            fieldnames = ['Station', 'X/H', 'LR', 'Y/H', 'U/Ur', 'V/Ur', 'uu', 'vv', 'uv', 'uuu', 'uvv', 'vuu', 'vvv']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write all station data
            for station in sorted(stations.keys()):
                station_data = stations[station]
                xh = station_data['metadata'].get('X/H', 'N/A')
                
                for row in station_data['data']:
                    combined_row = {'Station': station, 'X/H': xh}
                    combined_row.update(row)
                    writer.writerow(combined_row)
        
        print(f'Created combined file: {combined_filename}')

def main():
    """
    Main function to run the parser.
    """
    # Input file name
    input_file = 'bakstp1.txt'  # Change this to your file name
    
    print(f"Parsing {input_file}...")
    
    # Parse the data
    data_dict = parse_backstep_data(input_file)
    
    # Print summary
    print(f"\nParsed data summary:")
    cases_found = set()
    for (case, station) in data_dict.keys():
        cases_found.add(case)
    
    for case in sorted(cases_found):
        stations = [s for (c, s) in data_dict.keys() if c == case]
        print(f"  Case {case}: {len(stations)} stations (stations {min(stations)}-{max(stations)})")
        for station in sorted(stations):
            n_points = len(data_dict[(case, station)]['data'])
            xh = data_dict[(case, station)]['metadata'].get('X/H', 'N/A')
            print(f"    Station {station:2d} at X/H={xh:6.1f}: {n_points} data points")
    
    # Write CSV files
    print("\nWriting CSV files...")
    write_csv_files(data_dict)
    
    print("\nDone! CSV files have been created in the 'backstep_csv' directory.")

if __name__ == "__main__":
    main()