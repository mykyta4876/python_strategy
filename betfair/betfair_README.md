# Betfair Historical Data Downloader

This Python script downloads Betfair historical data and converts it to CSV format suitable for machine learning applications.

## Features

- Downloads historical data from Betfair API
- Decompresses .bz2 files automatically
- Converts data to CSV format for ML processing
- Supports filtering by sport, date range, market types, countries, and file types
- Includes comprehensive logging and error handling
- Processes multiple files and combines them into a single dataset

## Prerequisites

1. **Betfair Account**: You need a Betfair account with access to historical data
2. **Session Token**: Get your session token from Betfair
3. **Python Dependencies**: Install required packages

## Installation

1. (Optional) Create and activate a virtual environment:
python -m venv venv
venv\Scripts\activate


1. Install the required Python packages:
```bash
pip install -r requirements.txt
```

2. Get your Betfair session token:
   - Go to: https://support.developer.betfair.com/hc/en-us/articles/115003900112-How-do-I-get-a-sessionToken
   - Follow the instructions to obtain your session token

## Usage

### Basic Usage

1. Open `betfair.py` and replace `YOUR_SESSION_TOKEN_HERE` with your actual session token
2. Run the script:
```bash
python betfair.py
```

### Customizing the Download

You can modify the parameters in the `main()` function:

```python
# Example: Download horse racing data for March 2017
sport = "Horse Racing"
plan = "Basic Plan"
from_date = datetime(2017, 3, 1)
to_date = datetime(2017, 3, 31)

# Filter options
market_types = ["WIN", "PLACE"]  # Win and Place markets
countries = ["GB", "IE"]  # Great Britain and Ireland
file_types = ["M"]  # Market data files
```

### Using the Class Directly

```python
from betfair import BetfairDataDownloader
from datetime import datetime

# Initialize downloader
downloader = BetfairDataDownloader("YOUR_SESSION_TOKEN")

# Download data
df = downloader.download_and_process_data(
    sport="Horse Racing",
    plan="Basic Plan",
    from_date=datetime(2017, 3, 1),
    to_date=datetime(2017, 3, 31),
    market_types=["WIN", "PLACE"],
    countries=["GB", "IE"],
    file_types=["M"],
    max_files=10  # Limit number of files for testing
)

# Save to CSV
csv_path = downloader.save_to_csv(df, "my_betfair_data.csv")
```

## Output

The script creates the following directory structure:
```
betfair_data/
├── csv/
│   └── betfair_horse_racing_data.csv  # Final CSV output
└── [temporary downloaded files]
```

## Data Format

The CSV output includes:
- `raw_line`: Original data line from Betfair
- `timestamp`: Processing timestamp
- `file_source`: Source filename
- `field_0`, `field_1`, etc.: Parsed fields from the original data

## Configuration Options

### Market Types
- `WIN`: Win markets
- `PLACE`: Place markets
- `ANTEPOST_WIN`: Antepost win markets
- And more...

### Countries
- `GB`: Great Britain
- `IE`: Ireland
- `US`: United States
- And more...

### File Types
- `M`: Market data files
- `E`: Event data files

## Error Handling

The script includes comprehensive error handling:
- Network connection errors
- File download failures
- Data parsing errors
- API authentication issues

All errors are logged with timestamps for debugging.

## Limitations

1. **API Rate Limits**: The script includes delays between requests to be respectful to the API
2. **File Size**: Large datasets may take significant time to download
3. **Data Format**: The parser assumes a basic format - you may need to adjust based on actual data structure
4. **Session Token**: Tokens expire and need to be refreshed

## Troubleshooting

### Common Issues

1. **Authentication Error**: Check your session token is valid and not expired
2. **No Data Found**: Verify your account has access to the requested data package
3. **Download Failures**: Check your internet connection and try again
4. **Memory Issues**: Reduce `max_files` parameter for large datasets

### Getting Help

- Check the logs for detailed error messages
- Verify your Betfair account has the required data packages
- Ensure your session token is current

## API Documentation

For more details about the Betfair API:
- https://historicdata.betfair.com/#/apidocs
- https://support.developer.betfair.com/hc/en-us/articles/360000402211-How-do-I-download-view-Betfair-Historical-Data

## License

This script is provided as-is for educational and research purposes. Please comply with Betfair's terms of service when using their API. 