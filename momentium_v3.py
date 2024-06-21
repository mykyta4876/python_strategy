import os
import pandas as pd
import matplotlib.pyplot as plt

def load_data(directory):
    """ Load data from CSV files and return a dictionary of DataFrames. """
    market_data = {}
    for file in os.listdir(directory):
        if file.endswith('.csv'):
            path = os.path.join(directory, file)
            market_data[file.replace('.csv', '')] = pd.read_csv(path, parse_dates=['Date'], index_col='Date')
    return market_data

def find_earliest_date(market_data):
    """ Find the earliest common date across all markets. """
    earliest_date = max(df.index.min() for df in market_data.values())
    return earliest_date

def calculate_momentum(data, window=14):
    """ Calculate momentum as a simple price difference over the specified window. """
    return data.diff(window)

def backtest_strategy(market_data, start_date):
    """ Backtest trading strategy and return trading records and updated market data. """
    balance = 10000
    total_trades = []
    current_positions = {}
    profits = {}
    sum_profits = {}

    for date in pd.date_range(start=start_date, end=max(df.index.max() for df in market_data.values())):
        momentums = {market: df.loc[date, 'Momentum'] if date in df.index else None for market, df in market_data.items()}
        momentums = {k: v for k, v in momentums.items() if v is not None}
        if not momentums:
            continue
        
        highest_market = max(momentums, key=lambda x: abs(momentums[x]))
        highest_momentum = momentums[highest_market]
        trade_type = 'Long' if highest_momentum > 0 else 'Short'
        price = market_data[highest_market].loc[date, 'Close']
        
        if highest_market in current_positions:
            if (trade_type == 'Long' and current_positions[highest_market] == 'Short') or \
               (trade_type == 'Short' and current_positions[highest_market] == 'Long'):
                entry_price = profits[highest_market]
                profit = (price - entry_price) if trade_type == 'Short' else (entry_price - price)
                balance += profit
                sum_profits[highest_market] += profit
                total_trades.append((date, highest_market, 'Exit', price, profit, sum_profits[highest_market]))
                del current_positions[highest_market]
        
        if highest_market not in current_positions:
            current_positions[highest_market] = trade_type
            profits[highest_market] = price
            sum_profits.setdefault(highest_market, 0)
            total_trades.append((date, highest_market, 'Enter', price, 0, sum_profits[highest_market]))

    return total_trades, market_data, balance

def plot_trades_and_balance(market_data, trades):
    """ Plot trade charts for each symbol with trades and balance performance in a grid layout. """
    trades_df = pd.DataFrame(trades, columns=['Date', 'Symbol', 'TradeType', 'Price', 'Profit', 'SumProfit'])
    symbols_with_trades = trades_df['Symbol'].unique()
    num_charts = len(symbols_with_trades) + 1  # Additional chart for balance
    cols = 3  # Define number of columns in subplot grid
    rows = num_charts // cols + (num_charts % cols > 0)
    fig, axes = plt.subplots(rows, cols, figsize=(15, rows * 5), squeeze=False)
    
    idx = -1  # Initialize idx to handle case where no symbols have trades
    for idx, symbol in enumerate(symbols_with_trades):
        ax = axes[idx // cols, idx % cols]
        data = market_data[symbol]
        ax.plot(data.index, data['Close'], label=f'{symbol} Close Price')
        symbol_trades = trades_df[trades_df['Symbol'] == symbol]
        for i, row in symbol_trades.iterrows():
            color = 'green' if 'Enter' in row['TradeType'] else 'red'
            marker = '^' if 'Enter' in row['TradeType'] else 'o'
            ax.plot(row['Date'], row['Price'], marker=marker, color=color, markersize=10, label=f"{row['TradeType']} at {row['Price']}")
        ax.set_title(f'Trades for {symbol}')
        ax.set_xlabel('Date')
        ax.set_ylabel('Close Price')
        ax.legend()
        ax.grid(True)
    
    # Plot balance performance on the next subplot after the last symbol plot
    balance_ax_idx = idx + 1 if idx >= 0 else 0
    ax_balance = axes[balance_ax_idx // cols, balance_ax_idx % cols]
    ax_balance.plot(trades_df['Date'], trades_df['SumProfit'].cumsum(), label='Balance Over Time')
    ax_balance.set_title('Balance Performance')
    ax_balance.set_xlabel('Date')
    ax_balance.set_ylabel('Balance')
    ax_balance.legend()
    ax_balance.grid(True)
    
    # Hide unused axes
    for i in range(balance_ax_idx + 1, rows * cols):
        axes[i // cols, i % cols].axis('off')

    plt.tight_layout()
    plt.show()

def main():
    directory = 'MarketData'
    market_data = load_data(directory)
    start_date = find_earliest_date(market_data)
    
    for df in market_data.values():
        df['Momentum'] = calculate_momentum(df['Close'])
    
    trades, market_data, final_balance = backtest_strategy(market_data, start_date)
    plot_trades_and_balance(market_data, trades)
    
    # Save trades to CSV
    trades_df = pd.DataFrame(trades, columns=['Date', 'Symbol', 'TradeType', 'Price', 'Profit', 'SumProfit'])
    trades_df.to_csv('result_trades.csv', index=False)

if __name__ == '__main__':
    main()
