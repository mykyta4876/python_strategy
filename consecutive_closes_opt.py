import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
from itertools import product

def load_data(directory):
    market_data = {}
    if not os.path.exists(directory):
        raise FileNotFoundError(f"The system cannot find the path specified: {directory}")

    for file in os.listdir(directory):
        if file.endswith('.csv'):
            path = os.path.join(directory, file)
            df = pd.read_csv(path, parse_dates=['Date'], index_col='Date', dayfirst=True)
            df.index = pd.to_datetime(df.index)
            df = df[~df.index.duplicated(keep='first')]
            df = df.sort_index()
            df = df.asfreq('D', method='ffill')
            market_data[file.replace('.csv', '')] = df
    return market_data

def synchronize_start_dates(market_data, start_date):
    if start_date is None:
        return market_data
    for market, df in market_data.items():
        market_data[market] = df[df.index >= start_date]
    return market_data

def check_consecutive_closes(df, num_consecutive, direction='positive'):
    if direction == 'positive':
        return (df['Close'].diff() > 0).rolling(window=num_consecutive).sum().eq(num_consecutive)
    else:
        return (df['Close'].diff() < 0).rolling(window=num_consecutive).sum().eq(num_consecutive)

def calculate_bollinger_bands(df, window, num_std_dev_lower, num_std_dev_upper):
    df['MA'] = df['Close'].rolling(window=window).mean()
    df['BB_Lower'] = df['MA'] - (df['Close'].rolling(window=window).std() * num_std_dev_lower)
    df['BB_Upper'] = df['MA'] + (df['Close'].rolling(window=window).std() * num_std_dev_upper)
    return df

def simulate_trades(market_data, initial_assets=10000, num_long_entry=3, num_long_exit=2, num_short_entry=3, num_short_exit=2):
    balance = initial_assets
    trades = []
    current_positions = {}  # Keep track of positions per market

    for market, df in market_data.items():
        df['LongEntry'] = check_consecutive_closes(df, num_long_entry, direction='positive')
        df['LongExit'] = check_consecutive_closes(df, num_long_exit, direction='negative')
        df['ShortEntry'] = check_consecutive_closes(df, num_short_entry, direction='negative')
        df['ShortExit'] = check_consecutive_closes(df, num_short_exit, direction='positive')
        
        current_positions[market] = None

        for date, row in df.iterrows():
            price = row['Close']
            position = current_positions[market]

            if position:
                trade_type, entry_price = position
                
                if trade_type == 'Long' and row['LongExit']:
                    profit = price - entry_price
                    balance += profit
                    trades.append((date, market, 'Long Exit', price, profit, balance))
                    current_positions[market] = None
                
                elif trade_type == 'Short' and row['ShortExit']:
                    profit = entry_price - price
                    balance += profit
                    trades.append((date, market, 'Short Exit', price, profit, balance))
                    current_positions[market] = None

            if not current_positions[market]:
                if row['LongEntry']:
                    current_positions[market] = ('Long', price)
                    trades.append((date, market, 'Long Entry', price, 0, balance))
                
                elif row['ShortEntry']:
                    current_positions[market] = ('Short', price)
                    trades.append((date, market, 'Short Entry', price, 0, balance))

    return trades, balance

def plot_results(market_data, trades):
    """ Plot trading results and balance over time. """
    trades_df = pd.DataFrame(trades, columns=['Date', 'Symbol', 'TradeType', 'Price', 'Profit', 'Balance'])
    trades_df['Date'] = pd.to_datetime(trades_df['Date'])
    trades_df.set_index('Date', inplace=True)
    
    # Group by date and take the last balance value for each date
    balance_df = trades_df[['Balance']].groupby('Date').last().resample('D').ffill()
    
    plt.figure(figsize=(15, 15))

    ax1 = plt.subplot(311)
    for market, df in market_data.items():
        ax1.plot(df.index, df['Close'], label=f'{market} Close Price')

    labels_added = {'Long Entry': False, 'Long Exit': False, 'Short Entry': False, 'Short Exit': False}
    for trade in trades:
        label = None
        if 'Entry' in trade[2]:
            if 'Long' in trade[2]:
                color = 'green'
                direction = '^'
                label = 'Long Entry'
            else:
                color = 'blue'
                direction = 'v'
                label = 'Short Entry'
            
            if not labels_added[label]:
                ax1.scatter(trade[0], trade[3], color=color, marker=direction, label=label)
                labels_added[label] = True
            else:
                ax1.scatter(trade[0], trade[3], color=color, marker=direction)
        elif 'Exit' in trade[2]:
            if 'Long' in trade[2]:
                color = 'red'
                direction = 'v'
                label = 'Long Exit'
            else:
                color = 'orange'
                direction = '^'
                label = 'Short Exit'
            
            if not labels_added[label]:
                ax1.scatter(trade[0], trade[3], color=color, marker=direction, label=label)
                labels_added[label] = True
            else:
                ax1.scatter(trade[0], trade[3], color=color, marker=direction)

    ax1.set_title('Market Close Prices and Trades')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Close Price')
    ax1.legend()

    ax2 = plt.subplot(312)
    ax2.plot(balance_df.index, balance_df['Balance'], label='Balance Over Time', color='black')
    ax2.set_title('Balance Performance')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Balance')
    ax2.legend()

    plt.tight_layout()
    plt.show()

    return trades_df

def parse_arguments():
    parser = argparse.ArgumentParser(description="Trading Strategy Simulation")

    # Add arguments
    parser.add_argument("--startday", "-s", default="2020-01-01", help="start day, ex: 2024-04-24")
    parser.add_argument("--long_entry", "-le", type=int, default=3, help="Number of consecutive positive closes for long entry")
    parser.add_argument("--long_exit", "-lx", type=int, default=2, help="Number of consecutive negative closes for long exit")
    parser.add_argument("--short_entry", "-se", type=int, default=3, help="Number of consecutive negative closes for short entry")
    parser.add_argument("--short_exit", "-sx", type=int, default=2, help="Number of consecutive positive closes for short exit")\

    args = parser.parse_args()

    return args

def optimize_strategy(market_data, initial_assets=10000, long_entry_range=(2, 4), long_exit_range=(1, 3), short_entry_range=(2, 4), short_exit_range=(1, 3)):
    best_profit = -np.inf
    best_params = None

    parameter_grid = product(
        range(*long_entry_range),
        range(*long_exit_range),
        range(*short_entry_range),
        range(*short_exit_range)
    )

    log_file = "optimization_log.txt"
    with open(log_file, 'w') as f:
        f.write("le, lx, se, sx, total_profit\n")
        
    for params in parameter_grid:
        le, lx, se, sx = params
        _, total_profit = simulate_trades(
            market_data,
            initial_assets=initial_assets,
            num_long_entry=le,
            num_long_exit=lx,
            num_short_entry=se,
            num_short_exit=sx
        )
        
        with open(log_file, 'a') as f:
            f.write(f"{le}, {lx}, {se}, {sx}, {total_profit:.2f}\n")
            print(f"[-] Long Entry={le}, Long Exit={lx}, Short Entry={se}, Short Exit={sx}, total_profit={total_profit:.2f}")
        
        if total_profit > best_profit:
            best_profit = total_profit
            best_params = params

    return best_params, best_profit

def main():
    args = parse_arguments()

    # Load market data
    market_data = load_data("MarketData")

    # Synchronize start dates
    market_data = synchronize_start_dates(market_data, args.startday)

    # Optimize strategy
    best_params, best_profit = optimize_strategy(
        market_data,
        initial_assets=10000,
        long_entry_range=(2, 6),
        long_exit_range=(1, 3),
        short_entry_range=(2, 6),
        short_exit_range=(1, 3)
    )

    le, lx, se, sx = best_params

    print(f"Best Parameters: Long Entry={le}, Long Exit={lx}, Short Entry={se}, Short Exit={sx}")
    print(f"Best Profit: {best_profit:.2f}")

    # Simulate trades with the best parameters
    trades, _ = simulate_trades(
        market_data,
        initial_assets=10000,
        num_long_entry=le,
        num_long_exit=lx,
        num_short_entry=se,
        num_short_exit=sx
    )

    # Plot the results
    trades_df = plot_results(market_data, trades)

    # Save trades to CSV
    trades_df.to_csv("trades.csv")

if __name__ == "__main__":
    main()