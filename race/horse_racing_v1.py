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

# Get the list of unique courses
courses = sorted(data['course'].unique())
logger.info(f"Found {len(courses)} unique courses")

# Create an empty Excel writer object
output_file = 'trainer_appearances.xlsx'
logger.info(f"Creating Excel file: {output_file}")

with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
    total_trainers = len(trainers)
    for index, (trainer, short_trainer) in tqdm(trainers.iterrows(), total=total_trainers, desc="Processing trainers"):
        if not short_trainer:  # Skip empty trainer names
            continue
        
        # Filter data for the specific trainer
        trainer_data = data[data['trainer'] == trainer]

        # Get all unique dates from the dataset
        all_dates = pd.date_range(start=data['date'].min(), end=data['date'].max(), freq='D')

        # Prepare data for the DataFrame
        appearances = trainer_data.groupby('date').size().reindex(all_dates, fill_value=0)
        wins = trainer_data[trainer_data['position'] == 1].groupby('date').size().reindex(all_dates, fill_value=0)

        df_data = {
            'date': all_dates,
            'appearances': appearances,
            'wins': wins
        }

        # Calculate cumulative appearances and wins for different time windows
        for window in [365, 90, 30]:
            df_data[f'{window} Day Appearances'] = appearances.rolling(window=window, min_periods=1).sum()
            df_data[f'{window} Day Wins'] = wins.rolling(window=window, min_periods=1).sum()

        # Calculate Total Win Rate Difference (30 Day - 90 Day)
        df_data['Total Win Rate Difference'] = df_data['30 Day Wins'] / df_data['30 Day Appearances'] - df_data['90 Day Wins'] / df_data['90 Day Appearances']

        # Calculate course-specific wins for each time window
        for course in courses:
            course_data = trainer_data[trainer_data['course'] == course]
            for window in [365, 90, 30]:
                column_name = f'{course} {window} Day Wins'
                course_wins = course_data[course_data['position'] == 1].groupby('date').size().reindex(all_dates, fill_value=0)
                df_data[column_name] = course_wins.rolling(window=window, min_periods=1).sum()

        # Create the DataFrame all at once
        appearances_df = pd.DataFrame(df_data)

        # Write the trainer's data to a sheet in the Excel file
        sheet_name = short_trainer[:31]  # Ensure sheet name is not too long
        appearances_df.to_excel(writer, sheet_name=sheet_name, index=False)

        # Conditional formatting to highlight significant differences
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        last_column = len(df_data.keys())
        worksheet.conditional_format(1, last_column - 1, len(all_dates), last_column - 1, {
            'type': '3_color_scale',
            'min_color': "#FFC7CE",
            'mid_color': "#FFFFFF",
            'max_color': "#C6EFCE"
        })

logger.info(f"Trainer appearances, win rates, and course-specific wins written to '{output_file}'")