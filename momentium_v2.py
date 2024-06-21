import os
import pandas as pd
import matplotlib.pyplot as plt

def load_data(file_path):
    return pd.read_csv(file_path, parse_dates=['Date'], index_col='Date')

def calculate_momentum(data, period=14):
    return data['Close'].diff(period) / data['Close'].shift(period)

def backtest_strategy(directory):
    initial_capital = 10000
    markets_data = {}
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.csv')]
    
    for file in files:
        data = load_data(file)
        data['Momentum'] = calculate_momentum(data)
        markets_data[file] = data
    
    trades = pd.DataFrame(index=markets_data[next(iter(markets_data))].index)
    balance = initial_capital
    current_position = None
    entry_price = None
    last_market = None
    trade_details = []

    for date in trades.index:
        highest_momentum = None
        selected_market = None
        for file, data in markets_data.items():
            if date in data.index:
                momentum = data.at[date, 'Momentum']
                if highest_momentum is None or abs(momentum) > abs(highest_momentum):
                    highest_momentum = momentum
                    selected_market = file

        if selected_market:
            close_price = markets_data[selected_market].at[date, 'Close']
            moving_average = markets_data[selected_market]['Close'].rolling(window=14).mean().at[date]

            if highest_momentum is not None:
                if highest_momentum > 0 and (current_position is None or current_position == 'short'):
                    if current_position == 'short':
                        profit = entry_price - close_price
                        balance += profit * balance / entry_price
                    entry_price = close_price
                    current_position = 'long'
                    last_market = os.path.basename(selected_market).replace('.csv', '')
                    trade_details.append((date, close_price, 'Long Entry', last_market))
                elif highest_momentum < 0 and (current_position is None or current_position == 'long'):
                    if current_position == 'long':
                        profit = close_price - entry_price
                        balance += profit * balance / entry_price
                    entry_price = close_price
                    current_position = 'short'
                    last_market = os.path.basename(selected_market).replace('.csv', '')
                    trade_details.append((date, close_price, 'Short Entry', last_market))

            if current_position == 'long' and close_price < moving_average:
                profit = close_price - entry_price
                balance += profit * balance / entry_price
                current_position = None
                trade_details.append((date, close_price, 'Long Exit', last_market))
                entry_price = None
            elif current_position == 'short' and close_price > moving_average:
                profit = entry_price - close_price
                balance += profit * balance / entry_price
                current_position = None
                trade_details.append((date, close_price, 'Short Exit', last_market))
                entry_price = None

        trades.at[date, 'Balance'] = balance

    # Plotting trade entries and exits on close price charts
    plt.figure(figsize=(12, 10))
    for market, data in markets_data.items():
        plt.plot(data.index, data['Close'], label=os.path.basename(market).replace('.csv', ' Close'))

    for date, price, ttype, market in trade_details:
        marker = '^' if 'Entry' in ttype else 'o'
        color = 'green' if 'Long' in ttype else 'red'
        plt.plot(date, price, marker=marker, color=color, label=f"{ttype} ({market})")

    plt.title('Trade Entries and Exits on Close Prices')
    plt.xlabel('Date')
    plt.ylabel('Close Price')
    plt.legend()
    plt.show()

    # Plotting balance performance over time
    plt.figure(figsize=(12, 6))
    plt.plot(trades.index, trades['Balance'], label='Account Balance')
    plt.title('Balance Performance Over Time')
    plt.xlabel('Date')
    plt.ylabel('Balance')
    plt.legend()
    plt.show()

# Specify the directory containing the CSV files
directory = 'MarketData'
backtest_strategy(directory)
