import pandas as pd
import numpy as np
from datetime import timedelta
from dateutil.parser import parse
import logging
from tqdm import tqdm
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

# Step 1: Normalize positions and calculate previous race data
def normalize_positions(input_file, output_file):
    def normalize_position(position, ran):
        if pd.isna(position) or pd.isna(ran) or ran == 0:
            return None
        return (int(position) - 0.5) / int(ran)

    def parse_date(date_str):
        try:
            return parse(date_str, dayfirst=True)
        except:
            return pd.NaT

    reader = pd.read_csv(input_file, chunksize=250000, encoding='ISO-8859-1')
    date_to_num = {}
    first_chunk = True
    for chunk in tqdm(reader, desc="Processing chunks for normalization"):
        chunk['date'] = chunk['date'].apply(parse_date)
        dates = chunk['date'].dropna().unique()
        date_to_num.update({date: idx for idx, date in enumerate(sorted(dates), start=len(date_to_num) + 1)})
        chunk['Date_Num'] = chunk['date'].map(date_to_num)
        chunk = chunk.sort_values(by=['horsename', 'Date_Num'])
        chunk['NormalizedPosition'] = chunk.apply(lambda row: normalize_position(row['position'], row['ran']), axis=1)
        for i in range(1, 6):
            chunk[f'NormalizedPrevious_{i}'] = chunk.groupby('horsename')['NormalizedPosition'].shift(i)
        chunk['previous_race_date'] = chunk.groupby('horsename')['date'].shift(1)
        chunk['days_since'] = (chunk['date'] - chunk['previous_race_date']).dt.days
        mode = 'w' if first_chunk else 'a'
        header = first_chunk
        chunk.to_csv(output_file, index=False, encoding='ISO-8859-1', mode=mode, header=header)
        first_chunk = False

# Step 2: Calculate 90- and 365-day appearance frequencies
def calculate_appearance_frequencies(input_file, output_file):
    def parse_date(date_str):
        try:
            return parse(date_str, dayfirst=True)
        except:
            return pd.NaT

    data = pd.read_csv(input_file, encoding='ISO-8859-1', low_memory=False)
    data['date'] = data['date'].apply(parse_date)
    data['horsename'] = data['horsename'].fillna('Unknown').astype(str)

    results = []
    for _, row in tqdm(data.iterrows(), desc="Calculating appearances", total=len(data)):
        horsename = row['horsename']
        now_date = row['date']
        horsename_data = data[data['horsename'] == horsename]
        result = {'Index': row.name}
        for window in [365, 90]:
            before_date = now_date - timedelta(days=window)
            timeframe_data = horsename_data[(horsename_data['date'] >= before_date) & (horsename_data.index < row.name)]
            result[f'{window} Day Appearances'] = len(timeframe_data)
        results.append(result)

    results_df = pd.DataFrame(results).set_index('Index')
    data = pd.concat([data, results_df], axis=1)
    data.to_csv(output_file, index=False, encoding='ISO-8859-1')

# Step 3: Add previous yards columns
def add_previous_yards(input_file, output_file):
    df = pd.read_csv(input_file, encoding='ISO-8859-1')
    df['race_order'] = range(1, len(df) + 1)
    df.sort_values(['horsename', 'race_order'], inplace=True)
    for i in range(1, 6):
        df[f'previousyards{i}'] = df.groupby('horsename')['Yards'].shift(i)
    df.drop(columns=['race_order'], inplace=True)
    df.to_csv(output_file, index=False, encoding='ISO-8859-1')

# Step 4: Merge course accuracy data
def merge_course_accuracy(main_file, accuracy_file, output_file):
    df_main = pd.read_csv(main_file, encoding='ISO-8859-1')
    df_accuracy = pd.read_csv(accuracy_file, encoding='ISO-8859-1')
    df_merged = df_main.merge(df_accuracy, on='course', how='left')
    df_merged.to_csv(output_file, index=False, encoding='ISO-8859-1')
    logger.info(f"Merged course accuracy data saved to {output_file}")

# File paths (adjust as necessary)
input_file = 'sample.csv'  # Replace with your actual input file
normalized_output = 'normalized.csv'
appearance_output = 'appearance_frequencies.csv'
yards_output = 'yards_added.csv'
final_output = 'final_processed.csv'
course_accuracy_file = 'accuracy.csv'  # Replace with your actual course accuracy file

# Execute the steps in order
normalize_positions(input_file, normalized_output)
calculate_appearance_frequencies(normalized_output, appearance_output)
add_previous_yards(appearance_output, yards_output)
merge_course_accuracy(yards_output, course_accuracy_file, final_output)

logger.info(f"Final processed data saved to {final_output}")
