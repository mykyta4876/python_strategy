import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse

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

def calculate_bollinger_bands(df, window, num_std_dev_up, num_std_dev_dn):
    df['MA'] = df['Close'].rolling(window=window).mean()
    df['BB_Upper'] = df['MA'] + (df['Close'].rolling(window=window).std() * num_std_dev_up)
    df['BB_Lower'] = df['MA'] - (df['Close'].rolling(window=window).std() * num_std_dev_dn)
    return df

def simulate_trades(market_data, initial_assets=10000, num_long_entry=3, num_long_exit=2, num_short_entry=3, num_short_exit=2, bollinger_window=20, bollinger_std_dev_up=1.5, bollinger_std_dev_dn=1.5):
    balance = initial_assets
    trades = []

    for market, df in market_data.items():
        df = calculate_bollinger_bands(df, bollinger_window, bollinger_std_dev_up, bollinger_std_dev_dn)
        df['LongEntry'] = check_consecutive_closes(df, num_long_entry, direction='positive') & (df['Close'] > df['BB_Lower'])
        df['LongExit'] = check_consecutive_closes(df, num_long_exit, direction='negative')
        df['ShortEntry'] = check_consecutive_closes(df, num_short_entry, direction='negative') & (df['Close'] < df['BB_Upper'])
        df['ShortExit'] = check_consecutive_closes(df, num_short_exit, direction='positive')
        
        current_position = None
        
        for date, row in df.iterrows():
            price = row['Close']
            
            if current_position:
                trade_type, entry_price, entry_market = current_position
                
                if trade_type == 'Long' and row['LongExit']:
                    profit = price - entry_price
                    balance += profit
                    trades.append((date, entry_market, 'Long Exit', price, profit, balance))
                    current_position = None
                    
                elif trade_type == 'Short' and row['ShortExit']:
                    profit = entry_price - price
                    balance += profit
                    trades.append((date, entry_market, 'Short Exit', price, profit, balance))
                    current_position = None
                    
            if not current_position:
                if row['LongEntry']:
                    current_position = ('Long', price, market)
                    trades.append((date, market, 'Long Entry', price, 0, balance))
                    
                elif row['ShortEntry']:
                    current_position = ('Short', price, market)
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
        ax1.plot(df.index, df['BB_Upper'], linestyle='--', label=f'{market} Bollinger Band Upper')
        ax1.plot(df.index, df['BB_Lower'], linestyle='--', label=f'{market} Bollinger Band Lower')

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
    """
    # Add arguments
    parser.add_argument("--startday", "-s", default="2024-01-01", help="start day, ex: 2024-04-24")
    parser.add_argument("--long_entry", "-le", type=int, default=3, help="Number of consecutive negative closes for long entry")
    parser.add_argument("--long_exit", "-lx", type=int, default=2, help="Number of consecutive positive closes for long exit")
    parser.add_argument("--short_entry", "-se", type=int, default=3, help="Number of consecutive negative closes for short entry")
    parser.add_argument("--short_exit", "-sx", type=int, default=2, help="Number of consecutive positive closes for short exit")
    parser.add_argument("--bollinger_window", "-bw", type=int, default=20, help="Window size for Bollinger Bands")
    parser.add_argument("--bollinger_std_dev_up", "-bsdu", type=float, default=1.5, help="Standard deviation for Bollinger Bands Upper")
    parser.add_argument("--bollinger_std_dev_dn", "-bsdd", type=float, default=1.5, help="Standard deviation for Bollinger Bands Lower")
    """

    # Add arguments
    parser.add_argument("--startday", "-s", default="2015-01-01", help="start day, ex: 2024-04-24")
    parser.add_argument("--long_entry", "-le", type=int, default=2, help="Number of consecutive negative closes for long entry")
    parser.add_argument("--long_exit", "-lx", type=int, default=1, help="Number of consecutive positive closes for long exit")
    parser.add_argument("--short_entry", "-se", type=int, default=6, help="Number of consecutive negative closes for short entry")
    parser.add_argument("--short_exit", "-sx", type=int, default=2, help="Number of consecutive positive closes for short exit")
    parser.add_argument("--bollinger_window", "-bw", type=int, default=100, help="Window size for Bollinger Bands")
    parser.add_argument("--bollinger_std_dev_up", "-bsdu", type=float, default=1.2, help="Standard deviation for Bollinger Bands Upper")
    parser.add_argument("--bollinger_std_dev_dn", "-bsdd", type=float, default=1.2, help="Standard deviation for Bollinger Bands Lower")

    args = parser.parse_args()

    return args

def main():
    args = parse_arguments()
    directory = 'MarketData'
    start_date = None
    if args.startday is not None:
        start_date = pd.Timestamp(args.startday)

    market_data = load_data(directory)
    market_data = synchronize_start_dates(market_data, start_date)
    trades, final_balance = simulate_trades(market_data, 
                                            num_long_entry=args.long_entry,
                                            num_long_exit=args.long_exit,
                                            num_short_entry=args.short_entry,
                                            num_short_exit=args.short_exit,
                                            bollinger_window=args.bollinger_window,
                                            bollinger_std_dev_up=args.bollinger_std_dev_up,
                                            bollinger_std_dev_dn=args.bollinger_std_dev_dn)
    trades_df = plot_results(market_data, trades)
    trades_df.to_csv('trades_result.csv', index=False)

if __name__ == '__main__':
    main()
