import pandas as pd
import numpy as np
import os

folder_path = "/Users/maddiewallace/PycharmProjects/AIRE_Report_Back2/outputs/"
csv_files = [file for file in os.listdir(folder_path) if file.endswith(".csv")]

pm25_data = {}

for file in csv_files:
    file_path = os.path.join(folder_path, file)
    participant_id = os.path.splitext(file)[0]
    data = pd.read_csv(file_path)
    print(data)
    data['pm25'] = pd.to_numeric(data['pm25'], errors='coerce')  # Convert 'PM2.5' column to numeric
    pm25_data[participant_id] = data['pm25'].dropna().tolist()

def calculate_summary_statistics(data):
    summary_stats = {}
    all_values = []

    for participant, values in data.items():
        summary_stats[participant] = {}
        values = np.array(values)

        # Calculate summary statistics
        summary_stats[participant]['10th_percentile'] = np.percentile(values, 10)
        summary_stats[participant]['25th_percentile'] = np.percentile(values, 25)
        summary_stats[participant]['50th_percentile'] = np.percentile(values, 50)
        summary_stats[participant]['75th_percentile'] = np.percentile(values, 75)
        summary_stats[participant]['90th_percentile'] = np.percentile(values, 90)
        summary_stats[participant]['max'] = np.max(values)
        summary_stats[participant]['mean'] = np.mean(values)
        summary_stats[participant]['percentage_above_12'] = (np.sum(values > 12) / len(values)) * 100

        all_values.extend(values)

    # Calculate summary statistics for the entire dataset
    all_values = np.array(all_values)
    summary_stats['overall'] = {
        '10th_percentile': np.percentile(all_values, 10),
        '25th_percentile': np.percentile(all_values, 25),
        '50th_percentile': np.percentile(all_values, 50),
        '75th_percentile': np.percentile(all_values, 75),
        '90th_percentile': np.percentile(all_values, 90),
        'max': np.max(all_values),
        'mean': np.mean(all_values),
        'percentage_above_12': (np.sum(all_values > 12) / len(all_values)) * 100
    }

    return summary_stats

# Call the function with the data
summary_stats = calculate_summary_statistics(pm25_data)

# Convert the summary_stats dictionary to a DataFrame and sort the columns
df_summary_stats = pd.DataFrame(summary_stats).transpose().sort_index()

# Save the DataFrame as a CSV file
output_path = "/Users/maddiewallace/PycharmProjects/AIRE_Report_Back2/outputs/summary_stats.csv"
df_summary_stats.to_csv(output_path, index=True)
