import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from tqdm import tqdm
import argparse
import sys
import os
from dateutil.parser import parse

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

# Set up argument parser
parser = argparse.ArgumentParser(description='Process horse racing data.')
parser.add_argument('file_path', type=str, help='Path to the CSV file containing horse racing data')
args = parser.parse_args()

# Load the CSV file with proper encoding
file_path = args.file_path
logger.info(f"Loading data from {file_path}")

if not os.path.exists(file_path):
    logger.error(f"File not found: {file_path}")
    sys.exit(1)

try:
    data = pd.read_csv(file_path, encoding='ISO-8859-1', low_memory=False)
except pd.errors.EmptyDataError:
    logger.error(f"The file is empty: {file_path}")
    sys.exit(1)
except Exception as e:
    logger.error(f"An unexpected error occurred while reading the file: {str(e)}")
    sys.exit(1)

# Check if the file is empty after successful read
if data.empty:
    logger.error(f"The file is empty or contains no valid data: {file_path}")
    sys.exit(1)

# Convert 'date' column to datetime format
try:
    # Function to parse dates with multiple formats
    def parse_date(date_str):
        try:
            # Try parsing with dateutil.parser.parse which is very flexible
            return parse(date_str, dayfirst=True)  # Assume day comes first in ambiguous dates
        except:
            return pd.NaT

    # Apply the parse_date function to the 'date' column
    data['date'] = data['date'].apply(parse_date)

    # Check for any remaining NaT values
    nat_count = data['date'].isna().sum()
    if nat_count > 0:
        logger.warning(f"{nat_count} rows have invalid dates. These will be excluded from analysis.")
        
        # Log some examples of unparseable dates
        unparseable_dates = data[data['date'].isna()]['date'].head(10).tolist()
        logger.warning(f"Examples of unparseable dates: {unparseable_dates}")
        
        # Remove rows with invalid dates
        data = data.dropna(subset=['date'])
    
    logger.info(f"Date range: from {data['date'].min()} to {data['date'].max()}")

except KeyError:
    logger.error("The 'date' column is missing from the CSV file")
    sys.exit(1)
except Exception as e:
    logger.error(f"An error occurred while processing the date column: {str(e)}")
    sys.exit(1)

# Convert 'trainer' column to string and handle NaN values
data['trainer'] = data['trainer'].fillna('Unknown').astype(str)

# Truncate the 'trainer' column to 31 characters and store it in 'short_trainer'
data['short_trainer'] = data['trainer'].str[:31]

# Create a list of unique trainers and their corresponding short names
trainers = data[['trainer', 'short_trainer']].drop_duplicates()
logger.info(f"Found {len(trainers)} unique trainers")

# Get the list of unique courses
courses = sorted(data['course'].unique())
logger.info(f"Found {len(courses)} unique courses")

data['Index'] = data.index

# Create an empty Excel writer object
output_file = 'trainers_results.xlsx'
logger.info(f"Creating Excel file: {output_file}")
# Import necessary libraries for multithreading
import concurrent.futures
import threading

# Function to process a single row
def process_row(row):
    trainer = row['trainer']
    race_id = row['Id']
    now_date = row['date']
    course = row['course']

    # Filter data for the specific trainer
    trainer_data = data[data['trainer'] == trainer]
    
    result = {}
    result['Index'] = row['Index']
    for window in [365, 90, 30]:
        # Calculate appearances for different time windows
        before_date = now_date - timedelta(days=window)
        timeframe_data = trainer_data[(trainer_data['date'] >= before_date) & (trainer_data['Id'] <= race_id)]
        result[f'{window} Day Appearances'] = timeframe_data.index.nunique()
        
        timeframe_wins_data = timeframe_data[timeframe_data['position'] == 1]
        # Calculate wins for different time windows
        result[f'{window} Day Wins'] = timeframe_wins_data.index.nunique()

        # Calculate course-specific wins for each time window
        result[f'Course {window} Day Wins'] = timeframe_wins_data.loc[(timeframe_wins_data['course'] == course), 'Id'].nunique()

    # Calculate Total Win Rate Difference (30 Day - 90 Day)
    result['Total Wins Diff'] = result['30 Day Wins'] / result['30 Day Appearances'] - result['90 Day Wins'] / result['90 Day Appearances']

    return result

# Function to update the DataFrame with results
def update_dataframe(index, result):
    for key, value in result.items():
        data.at[index, key] = value

# Create a thread-safe lock for DataFrame updates
lock = threading.Lock()

# Function to process rows in chunks
def process_chunk(chunk):
    results = []
    for _, row in chunk.iterrows():
        result = process_row(row)
        results.append(result)
    return results

# Calculate the number of chunks based on CPU cores
num_chunks = os.cpu_count()
chunk_size = len(data) // num_chunks
chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]

logger.info(f"Processing {len(chunks)} chunks by using {num_chunks} threads")
# Create a ThreadPoolExecutor
with concurrent.futures.ThreadPoolExecutor(max_workers=num_chunks) as executor:
    # Submit tasks for each chunk
    futures = [executor.submit(process_chunk, chunk) for chunk in chunks]

    # Use tqdm to show progress
    all_results = []
    for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Processing data"):
        all_results.extend(future.result())

# Create a new DataFrame with the results
results_df = pd.DataFrame(all_results)
results_df.sort_values(by='Index', inplace=True)

# Reorder columns
column_order = [
    'Index', 
    '365 Day Appearances', '90 Day Appearances', '30 Day Appearances',
    '365 Day Wins', '90 Day Wins', '30 Day Wins',
    'Total Wins Diff',
    'Course 365 Day Wins', 'Course 90 Day Wins', 'Course 30 Day Wins'
]
results_df = results_df[column_order]


# Concatenate the results with the original DataFrame
data = pd.concat([data.set_index('Index'), results_df.set_index('Index')], axis=1)
data = data.reset_index()

# Reorder columns to add new columns next to 'trainer'
trainer_index = data.columns.get_loc('trainer')
new_columns = data.columns.tolist()
new_columns = new_columns[:trainer_index+1] + [col for col in results_df.columns if col != 'Index'] + new_columns[trainer_index+1:]
data = data[new_columns]

data.to_excel(output_file, index=False)

logger.info("Multithreaded processing completed")

logger.info(f"Trainer appearances, win rates, and course-specific wins written to '{output_file}'")
