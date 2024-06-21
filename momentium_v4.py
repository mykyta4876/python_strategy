import os
import pandas as pd
import matplotlib.pyplot as plt

def load_data(directory):
    """ Load data from CSV files and synchronize start dates. """
    market_data = {}
    for file in os.listdir(directory):
        if file.endswith('.csv'):
            path = os.path.join(directory, file)
            df = pd.read_csv(path, parse_dates=['Date'], index_col='Date')
            market_data[file.replace('.csv', '')] = df
    return market_data

def synchronize_start_dates(market_data):
    """ Synchronize start dates across all markets. """
    earliest_date = max(df.index.min() for df in market_data.values())
    for market in market_data:
        market_data[market] = market_data[market][market_data[market].index >= earliest_date]
    return earliest_date

def calculate_momentum_and_ma(data, window=14):
    """ Calculate momentum and moving average for the markets. """
    for market, df in data.items():
        df['Momentum'] = df['Close'].diff(window)
        df['MA'] = df['Close'].rolling(window=window).mean()
    return data

def simulate_trades(market_data, initial_assets=10000):
    """ Simulate trades based on momentum and generate trade details and profit performance. """
    balance = initial_assets
    trades = []
    current_positions = {}
    sum_profits = {}

    # Iterate over all possible dates
    dates = pd.date_range(start=min(df.index.min() for df in market_data.values()), end=max(df.index.max() for df in market_data.values()))
    for date in dates:
        if date not in market_data[next(iter(market_data))].index:
            continue
        # Identify the market with the highest momentum
        momentums = {market: df.loc[date, 'Momentum'] if date in df.index else None for market, df in market_data.items()}
        if all(m is None for m in momentums.values()):
            continue
        highest_market = max(momentums, key=lambda x: abs(momentums[x]))
        highest_momentum = momentums[highest_market]
        trade_type = 'Long' if highest_momentum > 0 else 'Short'
        price = market_data[highest_market].loc[date, 'Close']

        # Manage positions and trades
        if highest_market in current_positions:
            if current_positions[highest_market] != trade_type:
                # Exit condition
                entry_price = current_positions.pop(highest_market)[1]
                profit = price - entry_price if trade_type == 'Short' else entry_price - price
                balance += profit
                sum_profits[highest_market] = sum_profits.get(highest_market, 0) + profit
                trades.append((date, highest_market, 'Exit', price, profit, balance))
        if highest_market not in current_positions:
            # Entry condition
            current_positions[highest_market] = (trade_type, price)
            trades.append((date, highest_market, 'Enter', price, 0, balance))

    return trades, balance

def plot_results(market_data, trades):
    """ Plot trading results and balance over time. """
    trades_df = pd.DataFrame(trades, columns=['Date', 'Symbol', 'TradeType', 'Price', 'Profit', 'Balance'])
    plt.figure(figsize=(15, 10))

    # Plot market close prices
    ax1 = plt.subplot(211)
    for market, df in market_data.items():
        ax1.plot(df['Close'], label=f'{market} Close Price')
    ax1.set_title('Market Close Prices and Trades')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Close Price')
    ax1.legend()

    # Plot balance performance
    ax2 = plt.subplot(212)
    ax2.plot(trades_df['Date'], trades_df['Balance'], label='Balance Over Time', color='black')
    ax2.set_title('Balance Performance')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Balance')
    ax2.legend()

    plt.tight_layout()
    plt.show()

    return trades_df

def main():
    directory = 'MarketData'
    market_data = load_data(directory)
    synchronize_start_dates(market_data)
    calculate_momentum_and_ma(market_data)
    trades, final_balance = simulate_trades(market_data)
    trades_df = plot_results(market_data, trades)
    trades_df.to_csv('trades_result.csv', index=False)

if __name__ == '__main__':
    main()
