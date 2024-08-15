Simply put, the system will have around 13 CSV files like this. It's all different markets, and I want to buy (or sell) the market with highest momentum. So, maybe for the code, the momentum value/number will be an absolute figure (all positive). Then we trade the highest momentum. The entry can be either long or short. For long trades, we buy the market with highest positive momentum. For short trades, we buy the market with highest negative momentum. The system should only trade 1 market at a time (whichever has strongest momentum - either short or long). The exist is on a simple moving average crossover. So, for long trades, the exit is when the market close is below the MA. For short trades, the exit is when the market close is above simple MA.

Hopefully it is clear.

The most important fact is that it can take long/short - for the highest momentum. But the 'highest' momentum can be negative or positive 



It trades around 13 markets and looks for the market with the highest momentum (either long or short).

Entry condition:
It takes long trades if the highest momentum (out of the 13 markets) is up, and takes a short trade if the highest momentum is currently down.

Exit condition:
the moving average which is used to exit positions.
when long position,  if MA crossunder Close price, exit long position.
when short position,  if MA crossabove Close price, exit short position.

You can only open one trade at a time.

I am going to backtest this strategy.
Initial assets can be entered. default is 10000.

the market data csv files are in MarketData folder biside the python script.
Data is provided for the markets in CSV format (Date, Close).
start date of csv files can be different.
after you should read all csv files, you find earliest date and you shuold start from the date.
there is some inconsistencies in dates. Some markets don't trade on every day.
So, for that 'missing' date, just copy the previous close price for that 'missing' date.

Result:
I need a python script that report followings:
- trade chart that shows all trades (entry and exit)
	x axis is date and y axis is Close price.
	the chat plots Close Price of all symbol with different colors.

- chart that shows profit performance, x-axis is date and y-axis is balance.

- a result csv with the columns (Date, Symbol, TradeType, Price, Profit, SumProfit)

- And I need that it shows all charts at one.

- Add "startDate" parameter for checking strategy logic.


you can set Start Date.
python momentium_v6.py -s "2024-01-01"