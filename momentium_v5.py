import os
import pandas as pd
import matplotlib.pyplot as plt

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
    for market, df in market_data.items():
        market_data[market] = df[df.index >= start_date]
    return market_data

def calculate_momentum_and_ma(data, window=14):
    for market, df in data.items():
        df['Momentum'] = df['Close'].diff(window)
        df['MA'] = df['Close'].rolling(window=window).mean()
    return data

def simulate_trades(market_data, initial_assets=10000):
    balance = initial_assets
    trades = []
    current_position = None

    all_dates = pd.date_range(start=min(df.index.min() for df in market_data.values()),
                              end=max(df.index.max() for df in market_data.values()))

    for date in all_dates:
        if not all(date in df.index for df in market_data.values()):
            continue

        momentums = {market: df.loc[date, 'Momentum'] for market, df in market_data.items() if date in df.index}
        if not momentums:
            continue
        highest_market = max(momentums, key=lambda x: abs(momentums[x]))
        highest_momentum = momentums[highest_market]
        price = market_data[highest_market].loc[date, 'Close']
        ma = market_data[highest_market].loc[date, 'MA']

        if current_position:
            trade_type, entry_market, entry_price = current_position
            if entry_market == highest_market:
                if trade_type == 'Long' and ma > price:
                    profit = price - entry_price
                    balance += profit
                    trades.append((date, entry_market, 'Long Exit', price, profit, balance))
                    current_position = None
                elif trade_type == 'Short' and ma < price:
                    profit = entry_price - price
                    balance += profit
                    trades.append((date, entry_market, 'Short Exit', price, profit, balance))
                    current_position = None
            continue

        if not current_position:
            if highest_momentum > 0:
                current_position = ('Long', highest_market, price)
                trades.append((date, highest_market, 'Long Entry', price, 0, balance))
            elif highest_momentum < 0:
                current_position = ('Short', highest_market, price)
                trades.append((date, highest_market, 'Short Entry', price, 0, balance))

    return trades, balance

def plot_results(market_data, trades):
    """ Plot trading results, momentum, MA, and balance over time. """
    trades_df = pd.DataFrame(trades, columns=['Date', 'Symbol', 'TradeType', 'Price', 'Profit', 'Balance'])
    plt.figure(figsize=(15, 15))

    ax1 = plt.subplot(311)
    for market, df in market_data.items():
        ax1.plot(df.index, df['Close'], label=f'{market} Close Price')
        ax1.plot(df.index, df['MA'], linestyle='--', label=f'{market} MA')

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

    ax1.set_title('Market Close Prices, Trades, and MA')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Close Price')
    ax1.legend()

    ax2 = plt.subplot(312)
    ax2.plot(trades_df['Date'], trades_df['Balance'], label='Balance Over Time', color='black')
    ax2.set_title('Balance Performance')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Balance')
    ax2.legend()

    ax3 = plt.subplot(313)
    for market, df in market_data.items():
        ax3.plot(df.index, df['Momentum'], linestyle=':', label=f'{market} Momentum')
        ax3.plot(df.index, df['MA'], linestyle='--', label=f'{market} MA')

    ax3.set_title('Momentum and Moving Average')
    ax3.set_xlabel('Date')
    ax3.set_ylabel('Value')
    ax3.legend()

    plt.tight_layout()
    plt.show()

    return trades_df

def main():
    directory = 'MarketData'
    start_date = pd.Timestamp('2024-03-01')
    market_data = load_data(directory)
    market_data = synchronize_start_dates(market_data, start_date)
    calculate_momentum_and_ma(market_data)
    trades, final_balance = simulate_trades(market_data)
    trades_df = plot_results(market_data, trades)
    trades_df.to_csv('trades_result.csv', index=False)

if __name__ == '__main__':
    main()
