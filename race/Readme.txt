I have a csv file(horse_racing_data.csv) for horse racing historical data
you should read the cev file with the encoding='ISO-8859-1'
The csv has the columns - Id, course, date, RaceTime, Race, position, horsename, price, trainer, jockey, Comments

'ID' in first column is the race ID. The ID is the same for one race e.g. 44562101, is the ID for the race at Catterick on 01/01/22. The next ID is 44562102, which is the next race.
The column 'position' shows you the finishing positions of the horses in that race
If position=1, then that is winning horse that came first
The horse 'High Moon' won the race with ID 44562101

Total number of races for each trainer - over 365 days, 90 days and 30 days.
"365 Day Appearances", "90 Day Appearances", "30 Day Appearances"
For example, if the trainer appears 20 times in the last 30 days, we would have that as one column '30-Day Appearances' is 20.
So one column for 30-day appearance, one for 90-day appearance, and one for 365-day appearance.

Total win rate - over 365 days, 90 days and 30 days. The 'win rate' is the number of times the trainer had winning horses. You can work this out by looking at column 'position'. If 'position' value=1 then the horse won the race for that trainer.

Course wins - over 365/90/30 days. This is how the trainer performed on a particular course. You can see column 'B' is course. Again it is wins for 30/90/365. A lot might be empty.
we should get course list from the csv.
a cloum for each course and each term(365, 90, 30)

Finally for 'Total Win Rate', I want to look at how the on-going average compares to current time period. For example, if their win rate is 10% over 90 days, and they are currently winning at 15% on 30 days, we need to highlight that.
I am open to ideas as to how to do this, e.g with standard deviations
Total Win Rate = wins(30)/Appearances(30) - wins(90)/Appearances(90)

I need python code to get these result in format xlsx.
a sheet for each trainer.



============================
pip install pandas openpyxl xlsxwriter numpy tqdm

I've done. I added arguments to the code to calculate course stats or not.
In case you want to calculate course stats, please use -c flag.
python horse_racing.py -f newformat.csv -c
python horse_racing.py -f Book1.csv -c
In case you don't want to calculate course stats, please don't use -c flag.
python horse_racing.py -f newformat.csv

============================
I have some new code to incorporate with the other code
However, it was written by AI

It does several things: 
1) Takes horses last race finishing position, normalizes that position (by checking number of runners in the race - for last 5 races)
2) Calculates horses appearance in last 90 and 365 days
3) Checks the distances of the previous races it ran in
4) Merges 'course accuracy' data to an additional column in the final file

the biggest issue is likely the date/ID columns
