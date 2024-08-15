import os
import pandas as pd
from collections import defaultdict

# Define the folder path
folder_path = 'Sentiment_Analysis'

# check the folder
if os.path.isdir(folder_path) == False:
    print(f"[-] error: don't exist the folder-{folder_path}")
    exit(0)

# Get a list of all Excel files in the folder
excel_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]

if len(excel_files) == 0:
    print(f"[-] error: no files in the folder-{folder_path}")
    exit(0)

# Initialize a dictionary to store the records
records = defaultdict(lambda: {'count': 0, 'files': [0] * len(excel_files)})

# Process each Excel file
for file_idx, file_name in enumerate(excel_files):
    file_path = os.path.join(folder_path, file_name)
    df = pd.read_excel(file_path)

    # Iterate through each row in the DataFrame
    for _, row in df.iterrows():
        key = (row['Date Time'], row['Team'])
        records[key]['count'] += 1
        records[key]['files'][file_idx] = 1

# Prepare the data for the result DataFrame
result_data = []
for key, value in records.items():
    date_time, team = key
    count = value['count']
    file_flags = value['files']
    result_data.append([date_time, team, count] + file_flags)

# Define the columns for the result DataFrame
columns = ['Date Time', 'Team', 'Repeat Count'] + excel_files

# Create the result DataFrame
result_df = pd.DataFrame(result_data, columns=columns)

print("===================result==================")
print(result_df)
print("===========================================")

# Save the result DataFrame to an Excel file
result_df.to_excel('result.xlsx', index=False)

print("[-] saved the result into result.xlsx")
