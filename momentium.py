#python momentium.py -m 10
import pandas as pd
import numpy as np
from glob import glob
import os
import argparse

def load_data(files):
    """ Load market data from CSV files. """
    data = {}
    for file in files:
        market_name = file.split('/')[-1].replace('.csv', '')
        data[market_name] = pd.read_csv(file, index_col='Date', parse_dates=True)
    return data

def calculate_momentum(data, momentum_length=10):
    """ Calculate momentum for each market. """
    momentum = {}
    for market, df in data.items():
        df['Return'] = df['Close'].pct_change(periods=momentum_length)
        df['Momentum'] = df['Return'].rolling(window=momentum_length).mean()
        momentum[market] = df['Momentum'].iloc[-1]
    return momentum

def select_market(momentum):
    """ Select the market with the highest absolute momentum. """
    max_momentum_market = max(momentum, key=lambda x: abs(momentum[x]))
    return max_momentum_market, momentum[max_momentum_market]

def decide_trade(momentum_value):
    """ Decide trade based on momentum. """
    return 'Long' if momentum_value > 0 else 'Short'

def calculate_exit_ma(data, market, ma_length=5):
    """ Calculate moving average for exit strategy. """
    data[market]['MA'] = data[market]['Close'].rolling(window=ma_length).mean()
    return data[market]['MA'].iloc[-1]

def parse_arguments():
    parser = argparse.ArgumentParser(description="Python Momentum Strategy")

    # Add arguments
    parser.add_argument("--momentum_len", "-m", help="Momentum length", type=int)

# Main script
if __name__ == '__main__':
    dir_data = "MarketData"
    if os.path.isdir(dir_data) == False:
        print("[-] error: no MarketData directory")

    # Load market data
    files = glob(dir_data + '\\*.csv')  # Update the path accordingly
    market_data = load_data(files)

    # Calculate momentum
    momentum_length = 10  # Example: 10-day momentum
    market_momentum = calculate_momentum(market_data, momentum_length)

    # Select the market with the highest momentum
    selected_market, momentum_value = select_market(market_momentum)
    print(f"Selected Market: {selected_market}, Momentum: {momentum_value}")

    # Decide the trade type
    trade_type = decide_trade(momentum_value)
    print(f"Trade Decision: {trade_type}")

    # Parse command-line arguments
    args = parse_arguments()

    # Calculate exit moving average
    ma_length = 5  # Example: 5-day moving average
    if args.momentum_len != None:
        ma_length = args.momentum_len

    exit_ma = calculate_exit_ma(market_data, selected_market, ma_length)
    print(f"Exit Moving Average: {exit_ma}")
