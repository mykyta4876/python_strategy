For new models

I have several inputs to think about it

The data I have isn't conventional data

It's for soccer/football betting

I have these 'known' inputs:

1) Stadium, 2) Day week, 3) Team name

4) Odds (the bookmaker belief of how likely they are to win - for example, 2/1 means if you bet £10, you win £20)

There is more data, but we only have the data from previous match.

This data is - cumulative loss (which is previous losses the team had), moving average 7 (this is an average of the last 7 matches), Standard deviation of the MA7

Also MA30 and SD30, MA 90 and SD90

All these - we only have the data for previous match.
So I want to build a model such as XGBoost for this
But how do we handle empty data of cumulative loss, MA7, MA30, MA90 and SDev
I assume we just copy from previous record/match?

The inputs 1-4 are only confirmed data for current match

========================================
The details like dates are wrong but it doesn't really matter

The most important columns which we have data for in advance are:

Column B - Parameter X. This is my own data which is one of around 6 different inputs (this is available in advance of the match)

Column C - time - this is known

Column F - is NOT known (the result)

Column G - is known (the odds from bookmaker)

Column H-O are not known

Also neither is column F

For columns H-O we would use average of previous 2 records like you mentioned

Column H shows whether it was a loss, and assigns a value of -£50 if it was a loss.

The 'cumularive loss' is a figure that sums the losses of previous matches

The reason for this is to show how well the team is performing at current time.

7-day of MA loss shows the 7-day average of the column I

SD of loss (7) is standard deviation of the column J

Column L is 30 days average of column I (not shown as not enough data from this file)

Column M is standard deviation of L

Column N is 90-day moving average of loss (column I)

and then O is standard deviation of N

All these figures we only have number from previous match, so would use 2-record average of previous 2 matches

XGBoost could use column B, C, D, E and G - these are known parameters

The columns H-O are now known

The prediction value is column F

A draw is counted as a loss so the only two predictions to make for F are Loss/Win.
========================================
Can we normalize the data between 0-1, for each column?

And update it for every 200 records, so it is always updating

You could then categories values of 0-0.1, as '1', 0.1-0.2 as '2', and so on
========================================