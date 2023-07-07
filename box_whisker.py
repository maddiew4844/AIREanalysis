import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

folder_path = "/Users/maddiewallace/PycharmProjects/AIRE_Report_Back2/outputs/"
csv_files = [file for file in os.listdir(folder_path) if file.endswith(".csv")]

pm25_data = {}

for file in csv_files:
    file_path = os.path.join(folder_path, file)
    participant_id = os.path.splitext(file)[0]
    data = pd.read_csv(file_path)
    data['pm25'] = pd.to_numeric(data['pm25'], errors='coerce')  # Convert 'PM2.5' column to numeric
    pm25_data[participant_id] = data['pm25'].dropna().tolist()

# Create a list of PM2.5 values for each participant
participant_values = [pm25_data[participant] for participant in pm25_data]

# Create a list of participant IDs
participant_ids = list(pm25_data.keys())

# Create the box and whisker plot
plt.figure(figsize=(10, 6))
plt.boxplot(participant_values, labels=participant_ids, showfliers=False)
plt.xlabel('Participant')
plt.ylabel('PM2.5')
plt.title('PM2.5 Box and Whisker Plot')
plt.xticks(rotation=45)
plt.show()