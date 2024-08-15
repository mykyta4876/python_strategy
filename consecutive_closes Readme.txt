For the next approach, I want to look at consecutive closes.

For example, if market close today < market close yesterday, enter short trade
However, we can change the parameter for number of consecutive closes.
For example, if market today < market yesterday and market yesterday < market (2 days ago) - this is two consecutive (negative) closes
Or we can have three consecutive negative closes, etc.
For long it will be the opposite - 2, 3, 4, 5, 6 etc consecutive +ve closes from previous day
This time, the system can have multiple open positions across different markets also. The only criterion is number of consecutive +ve (long) or -ve closes (short).

Exit is for number of consecutive closes in opposite direction.
Later we might be able to combine it with other ideas
So it's best to code it so we can possibly add other criteria later
For example, you could use it with bollinger band entry as well.
But for now only the chain of consecutive closes

==================================
Take the example of a market that is today a closing value of 1,000
Tomorrow it closes at 1,001
This is one consecutive positive close
Then let's say the day after it closes at 1,002
That is another positive close
So that is a total of two positive closes
Then say it closes at 1,003
That is a third consecutive positive close
When we are testing the system, we can change number of closes
Above, I gave example of three positive closes
But we could also have 4 positive closes, or 5, 6 etc
So we should have a value we can change
Maybe 2, 3, 4, 5, 6
For number of positive closes
Is it clear?
You would buy after, say, 3 positive closes
or 4 positive closes, or whatever number
======================================
For short trade it is the opposite
If today close is 1,000, then tomorrow is 999, it is negative close
Then day after is 998 - that's two consecutive closes which are negative
Again we can vary the number of negative closes - maybe 3, 4, 5 etc
For exit, it is consecutive trades in opposite direction
For example, maybe entry is 3 consecutive closes. The market is 1,000, then 1,001, then 1,002, and 1,003
So that's an entry
Then it goes from 1,003 to 1,002, then 1,001
That's two consecutive negative closes.
So This would be exit

The code would have four things we can change
1) Number of consecutive closes for long entry
2) Number of consecutive (negative) closes for long exit
3) Number of consecutive closes (negative) for short entry
4) Number of consecutive closes (positive) for short exit

=======================================

you can set "start date" with -s parameter.
you can set "Number of consecutive positive closes for long entry" with -le parameter. default=3
you can set "Number of consecutive negative closes for long exit" with -lx parameter. default=2
you can set "Number of consecutive negative closes for short entry" with -se parameter. default=3
you can set "Number of consecutive positive closes for short exit" with -sx parameter. default=2
ex) python consecutive_closes.py -s "2024-03-01" -le 3 -lx 2 -se 3 -sx 2
=======================================

I want to update this strategy.

I want only long position.
And I want to add bollinger band standard deviation into this strategy.
So we would wait for the market to exceed bollinger band (of 'x' amount, e.g 1.5, 2, 2.5), then would enter if 3 consecutive down closes.

For example
Market close is 1000, bollinger band at 1.5 standard deviation is 1,110.
The market has three consecutive positive closes, and then closes above 1,100
The first and second close could be below 1,100, but the final close must be above the bollinger band
Or, the first, second and third closes can be above 1,100. It doesn't matter as long as the final close is above

The standard deviation amount should be changeable

So I can adjust to 1.5, 2, 2.5 etc

=======================================

you can set "start date" with -s parameter.
you can set "Number of consecutive positive closes for long entry" with -le parameter. default=3
you can set "Number of consecutive negative closes for long exit" with -lx parameter. default=2
you can set "size of bollinger_window" with -bw parameter. default=20
you can set "size of bollinger_std_dev" with -bsd parameter. default=1.5

ex) python consecutive_closes_bb.py -s "2024-01-01" -le 3 -lx 2 -bw 20 -bsd -1.5

But, when test with bollinger_window(20) and bollinger_std_dev(1.5), no trades.
I think we should change bollinger_std_dev into -1.5

at this time I want to open both long and short positions.
if consecutive positive closes and last close > bb lower, open long position
if consecutive negative closes and last close < bb upper, open short position
you can set deviation len for bb lower, parameter name is "bsdd"
you can set deviation len for bb upper, parameter name is "bsdu"


you can set "start date" with -s parameter.
you can set "Number of consecutive positive closes for long entry" with -le parameter. default=3
you can set "Number of consecutive negative closes for long exit" with -lx parameter. default=2
you can set "Number of consecutive negative closes for short entry" with -se parameter. default=3
you can set "Number of consecutive positive closes for short exit" with -sx parameter. default=2
you can set "size of bollinger_window" with -bw parameter. default=20
you can set "size of bollinger_std_dev upper" with -bsdu parameter. default=1.5
you can set "size of bollinger_std_dev lower" with -bsdd parameter. default=1.5

ex) python consecutive_closes_bb_v2.py -s "2024-01-01" -le 3 -lx 2 -se 3 -sx 2 -bw 20 -bsdu 1.5 -bsdd 1.5


I want optimize this strategy in order that total profit is maximized.
I am going to add optimization function.
The variables to be optimized are as follows:
le, lx, se, sx

I want to log about each try.

you can change the range of optimzation value in this part of main function.


XGBoost
https://medium.com/@matthew1992/algorithmic-stock-trading-utilizing-xgboost-and-kalman-filters-approach-b63858f040db
https://medium.com/@samjgbennett/predicting-financial-market-prices-with-xgboost-and-kalman-filters-strategy-5d9c801bceea