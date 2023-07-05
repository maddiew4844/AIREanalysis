import numpy as np

# Example data for PM2.5 measurements (replace with your actual data)
pm25_data = {
    'participant1': [10, 15, 8, 20, 14, 16, 11, 9, 12, 18, 19, 10, 22, 13, 17],
    'participant2': [13, 16, 9, 7, 21, 15, 10, 11, 18, 14, 20, 9, 12, 19, 16],
    # Add data for the remaining participants
    # ...
}

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

# Call the function with your data
summary_stats = calculate_summary_statistics(pm25_data)

# Print the summary statistics for each participant
for participant, stats in summary_stats.items():
    print(f"Participant: {participant}")
    print(f"10th percentile: {stats['10th_percentile']}")
    print(f"25th percentile: {stats['25th_percentile']}")
    print(f"50th percentile (median): {stats['50th_percentile']}")
    print(f"75th percentile: {stats['75th_percentile']}")
    print(f"90th percentile: {stats['90th_percentile']}")
    print(f"Max: {stats['max']}")
    print(f"Mean: {stats['mean']}")
    print(f"Percentage above 12: {stats['percentage_above_12']}%\n")

# Print the summary statistics for the entire dataset
print("Overall Summary Statistics")
print(f"10th percentile: {summary_stats['overall']['10th_percentile']}")
print(f"25th percentile: {summary_stats['overall']['25th_percentile']}")
print(f"50th percentile (median): {summary_stats['overall']['50th_percentile']}")
print(f"75th percentile: {summary_stats['overall']['75th_percentile']}")
print(f"90th percentile: {summary_stats['overall']['90th_percentile']}")
print(f"Max: {summary_stats['overall']['max']}")
print(f"Mean: {summary_stats['overall']['mean']}")
print(f"Percentage above 12: {summary_stats['overall']['percentage_above_12']}%")
