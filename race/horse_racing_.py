import argparse
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pandas import ExcelWriter

# Function to calculate appearances and win rate
def calculate_stats(df, start_date, period_label):
    period_df = df[df['date'] >= start_date]
    
    # Calculate appearances per trainer
    trainer_appearances = period_df.groupby('trainer')['Id'].nunique().reset_index(name=f'{period_label}-Day Appearances')
    
    # Calculate win rate per trainer
    trainer_wins = period_df[period_df['position'] == 1].groupby('trainer')['Id'].nunique().reset_index(name=f'{period_label}-Day Wins')
    
    # Merge appearances and wins, and calculate win rate
    trainer_stats = pd.merge(trainer_appearances, trainer_wins, on='trainer', how='left').fillna(0)
    trainer_stats[f'{period_label}-Day Win Rate'] = trainer_stats[f'{period_label}-Day Wins'] / trainer_stats[f'{period_label}-Day Appearances']
    
    return trainer_stats

# Function to calculate course-specific win rates
def calculate_course_stats(df, start_date, period_label):
    period_df = df[df['date'] >= start_date]
    course_list = period_df['course'].unique()
    
    course_stats = {}
    
    for course in course_list:
        course_df = period_df[period_df['course'] == course]
        
        # Appearances and win rates per trainer for this course
        appearances = course_df.groupby('trainer')['Id'].nunique().reset_index(name=f'{course}_{period_label}-Day Appearances')
        wins = course_df[course_df['position'] == 1].groupby('trainer')['Id'].nunique().reset_index(name=f'{course}_{period_label}-Day Wins')
        
        # Merge appearances and wins
        course_stat = pd.merge(appearances, wins, on='trainer', how='left').fillna(0)
        course_stat[f'{course}_{period_label}-Day Win Rate'] = course_stat[f'{course}_{period_label}-Day Wins'] / course_stat[f'{course}_{period_label}-Day Appearances']
        
        # Add this to course_stats
        course_stats[course] = course_stat
    
    return course_stats

def parse_arguments():
    parser = argparse.ArgumentParser(description="Caculate trainer stats")

    # Add arguments
    parser.add_argument("--file", "-f", type=str, help="path of source file", required=True)
    parser.add_argument("--course", "-c", action="store_false", help="flag to calculate course stats", required=False)

    args = parser.parse_args()

    return args

if __name__ == "__main__":

    # Parse command-line arguments
    args = parse_arguments()

    if args.file == None or args.file == "":
        print("Please provide a file path")
        exit(1)

    # Load the CSV data
    df = pd.read_csv(args.file, encoding='ISO-8859-1')

    # Convert 'date' column to datetime format
    df['date'] = pd.to_datetime(df['date'])

    # Today's date
    current_date = df['date'].max()

    # Define the periods: 365, 90, and 30 days
    periods = {
        '365': current_date - timedelta(days=365),
        '90': current_date - timedelta(days=90),
        '30': current_date - timedelta(days=30)
    }

    # Compute stats for each period
    trainers_365 = calculate_stats(df, periods['365'], '365')
    trainers_90 = calculate_stats(df, periods['90'], '90')
    trainers_30 = calculate_stats(df, periods['30'], '30')

    # Merge the stats
    trainers_stats = pd.merge(trainers_365, trainers_90, on='trainer', how='outer').merge(trainers_30, on='trainer', how='outer').fillna(0)

    # Compute standard deviation to compare win rates
    trainers_stats['Win Rate Std'] = (trainers_stats['30-Day Win Rate'] - trainers_stats['90-Day Win Rate'])

    # Calculate course-specific win rates
    course_stats_365 = calculate_course_stats(df, periods['365'], '365')
    course_stats_90 = calculate_course_stats(df, periods['90'], '90')
    course_stats_30 = calculate_course_stats(df, periods['30'], '30')

    # Write to Excel file
    with ExcelWriter('trainer_stats.xlsx', engine='xlsxwriter') as writer:
        for trainer in trainers_stats['trainer'].unique():
            trainer_data = trainers_stats[trainers_stats['trainer'] == trainer]
            
            # Add course-specific stats
            for course in course_stats_365.keys():
                course_data_365 = course_stats_365[course]
                course_data_90 = course_stats_90[course]
                course_data_30 = course_stats_30[course]
                
                # Merge course-specific stats for this trainer
                course_data = pd.merge(course_data_365, course_data_90, on='trainer', how='outer').merge(course_data_30, on='trainer', how='outer').fillna(0)
                trainer_data = pd.merge(trainer_data, course_data[course_data['trainer'] == trainer], on='trainer', how='outer').fillna(0)
            
            # Write trainer data to an individual sheet
            trainer_data.to_excel(writer, sheet_name=trainer, index=False)

    print("Trainer stats written to 'trainer_stats.xlsx'")
