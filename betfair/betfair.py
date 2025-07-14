import requests
import json
import pandas as pd
import bz2
import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BetfairDataDownloader:
    """
    A class to download and process Betfair historical data into CSV format
    suitable for machine learning applications.
    """
    
    def __init__(self, session_token: str, output_dir: str = "betfair_data"):
        """
        Initialize the Betfair data downloader.
        
        Args:
            session_token: Your Betfair session token
            output_dir: Directory to save downloaded data
        """
        self.session_token = session_token
        self.base_url = "https://historicdata.betfair.com/api"
        self.headers = {
            'ssoid': session_token,
            'content-type': 'application/json'
        }
        self.output_dir = output_dir
        self.csv_output_dir = os.path.join(output_dir, "csv")
        
        # Create output directories
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(self.csv_output_dir, exist_ok=True)
        
    def get_my_data(self) -> List[Dict[str, Any]]:
        """
        Get list of purchased packages.
        
        Returns:
            List of purchased packages
        """
        try:
            response = requests.get(
                f"{self.base_url}/GetMyData",
                headers={'ssoid': self.session_token}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting my data: {e}")
            return []
    
    def get_collection_options(self, sport: str, plan: str, 
                             from_date: datetime, to_date: datetime,
                             market_types: List[str] = None,
                             countries: List[str] = None,
                             file_types: List[str] = None) -> Dict[str, Any]:
        """
        Get available collection options for filtering data.
        
        Args:
            sport: Sport name (e.g., "Horse Racing")
            plan: Plan name (e.g., "Basic Plan")
            from_date: Start date
            to_date: End date
            market_types: List of market types to filter
            countries: List of countries to filter
            file_types: List of file types to filter
            
        Returns:
            Dictionary with available options
        """
        payload = {
            "sport": sport,
            "plan": plan,
            "fromDay": from_date.day,
            "fromMonth": from_date.month,
            "fromYear": from_date.year,
            "toDay": to_date.day,
            "toMonth": to_date.month,
            "toYear": to_date.year,
            "eventId": None,
            "eventName": None,
            "marketTypesCollection": market_types or [],
            "countriesCollection": countries or [],
            "fileTypeCollection": file_types or []
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/GetCollectionOptions",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting collection options: {e}")
            return {}
    
    def get_basket_data_size(self, sport: str, plan: str,
                           from_date: datetime, to_date: datetime,
                           market_types: List[str] = None,
                           countries: List[str] = None,
                           file_types: List[str] = None) -> Dict[str, Any]:
        """
        Get the size and count of files for a given filter.
        
        Returns:
            Dictionary with totalSizeMB and fileCount
        """
        payload = {
            "sport": sport,
            "plan": plan,
            "fromDay": from_date.day,
            "fromMonth": from_date.month,
            "fromYear": from_date.year,
            "toDay": to_date.day,
            "toMonth": to_date.month,
            "toYear": to_date.year,
            "eventId": None,
            "eventName": None,
            "marketTypesCollection": market_types or [],
            "countriesCollection": countries or [],
            "fileTypeCollection": file_types or []
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/GetAdvBasketDataSize",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting basket data size: {e}")
            return {}
    
    def get_download_list(self, sport: str, plan: str,
                         from_date: datetime, to_date: datetime,
                         market_types: List[str] = None,
                         countries: List[str] = None,
                         file_types: List[str] = None) -> List[str]:
        """
        Get list of files to download.
        
        Returns:
            List of file paths to download
        """
        payload = {
            "sport": sport,
            "plan": plan,
            "fromDay": from_date.day,
            "fromMonth": from_date.month,
            "fromYear": from_date.year,
            "toDay": to_date.day,
            "toMonth": to_date.month,
            "toYear": to_date.year,
            "eventId": None,
            "eventName": None,
            "marketTypesCollection": market_types or [],
            "countriesCollection": countries or [],
            "fileTypeCollection": file_types or []
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/DownloadListOfFiles",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting download list: {e}")
            return []
    
    def download_file(self, file_path: str, local_filename: str = None) -> bool:
        """
        Download a single file from Betfair.
        
        Args:
            file_path: Path of file on Betfair server
            local_filename: Local filename to save as
            
        Returns:
            True if successful, False otherwise
        """
        if local_filename is None:
            local_filename = os.path.basename(file_path)
        
        local_path = os.path.join(self.output_dir, local_filename)
        
        try:
            # URL encode the file path
            import urllib.parse
            encoded_path = urllib.parse.quote(file_path, safe='')
            
            response = requests.get(
                f"{self.base_url}/DownloadFile?filePath={encoded_path}",
                headers={'ssoid': self.session_token},
                stream=True
            )
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Downloaded: {local_filename}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading {file_path}: {e}")
            return False
    
    def decompress_bz2_file(self, bz2_file_path: str) -> str:
        """
        Decompress a .bz2 file and return the path to the decompressed file.
        
        Args:
            bz2_file_path: Path to the .bz2 file
            
        Returns:
            Path to the decompressed file
        """
        try:
            # Remove .bz2 extension for output file
            output_path = bz2_file_path[:-4] if bz2_file_path.endswith('.bz2') else bz2_file_path
            
            with bz2.open(bz2_file_path, 'rb') as source, open(output_path, 'wb') as target:
                target.write(source.read())
            
            logger.info(f"Decompressed: {os.path.basename(bz2_file_path)}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error decompressing {bz2_file_path}: {e}")
            return None
    
    def parse_betfair_data(self, data_file_path: str) -> pd.DataFrame:
        """
        Parse Betfair data file and convert to DataFrame.
        
        Args:
            data_file_path: Path to the data file
            
        Returns:
            DataFrame with parsed data
        """
        try:
            with open(data_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Initialize lists to store data
            data_rows = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Parse the line based on Betfair format
                # This is a basic parser - you may need to adjust based on actual data format
                try:
                    # Split by common delimiters and clean up
                    parts = line.split('|')
                    if len(parts) < 2:
                        parts = line.split(',')
                    
                    # Create a row with all parts
                    row_data = {
                        'raw_line': line,
                        'timestamp': datetime.now().isoformat(),
                        'file_source': os.path.basename(data_file_path)
                    }
                    
                    # Add parsed parts as columns
                    for i, part in enumerate(parts):
                        row_data[f'field_{i}'] = part.strip()
                    
                    data_rows.append(row_data)
                    
                except Exception as e:
                    logger.warning(f"Could not parse line: {line[:100]}... Error: {e}")
                    continue
            
            return pd.DataFrame(data_rows)
            
        except Exception as e:
            logger.error(f"Error parsing data file {data_file_path}: {e}")
            return pd.DataFrame()
    
    def download_and_process_data(self, sport: str, plan: str,
                                from_date: datetime, to_date: datetime,
                                market_types: List[str] = None,
                                countries: List[str] = None,
                                file_types: List[str] = None,
                                max_files: int = 10) -> pd.DataFrame:
        """
        Download and process Betfair data into a single DataFrame.
        
        Args:
            sport: Sport name
            plan: Plan name
            from_date: Start date
            to_date: End date
            market_types: Market types to filter
            countries: Countries to filter
            file_types: File types to filter
            max_files: Maximum number of files to download (for testing)
            
        Returns:
            Combined DataFrame with all data
        """
        logger.info(f"Starting download for {sport} - {plan} from {from_date} to {to_date}")
        
        # Get file list
        file_list = self.get_download_list(sport, plan, from_date, to_date,
                                         market_types, countries, file_types)
        
        if not file_list:
            logger.error("No files found to download")
            return pd.DataFrame()
        
        logger.info(f"Found {len(file_list)} files to download")
        
        # Limit files for testing
        if max_files and len(file_list) > max_files:
            file_list = file_list[:max_files]
            logger.info(f"Limited to {max_files} files for testing")
        
        all_dataframes = []
        
        for i, file_path in enumerate(file_list):
            logger.info(f"Processing file {i+1}/{len(file_list)}: {os.path.basename(file_path)}")
            
            # Download file
            local_filename = f"betfair_data_{i+1}.bz2"
            if not self.download_file(file_path, local_filename):
                continue
            
            local_path = os.path.join(self.output_dir, local_filename)
            
            # Decompress file
            decompressed_path = self.decompress_bz2_file(local_path)
            if not decompressed_path:
                continue
            
            # Parse data
            df = self.parse_betfair_data(decompressed_path)
            if not df.empty:
                all_dataframes.append(df)
            
            # Clean up compressed file
            try:
                os.remove(local_path)
            except:
                pass
            
            # Small delay to be respectful to the API
            time.sleep(0.5)
        
        # Combine all dataframes
        if all_dataframes:
            combined_df = pd.concat(all_dataframes, ignore_index=True)
            logger.info(f"Combined {len(all_dataframes)} files into DataFrame with {len(combined_df)} rows")
            return combined_df
        else:
            logger.warning("No data was successfully processed")
            return pd.DataFrame()
    
    def save_to_csv(self, df: pd.DataFrame, filename: str = None) -> str:
        """
        Save DataFrame to CSV file.
        
        Args:
            df: DataFrame to save
            filename: Output filename (optional)
            
        Returns:
            Path to saved CSV file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"betfair_data_{timestamp}.csv"
        
        csv_path = os.path.join(self.csv_output_dir, filename)
        
        try:
            df.to_csv(csv_path, index=False, encoding='utf-8')
            logger.info(f"Saved data to: {csv_path}")
            return csv_path
        except Exception as e:
            logger.error(f"Error saving CSV: {e}")
            return None

def main():
    """
    Main function to demonstrate usage of the BetfairDataDownloader.
    """
    # You need to get your session token from Betfair
    # https://support.developer.betfair.com/hc/en-us/articles/115003900112-How-do-I-get-a-sessionToken
    SESSION_TOKEN = "nZmKr9X1mWWjoVnI9nu5c0kTrv9h2+2BajCHKSHpCFg="  # Replace with your actual token
    
    if SESSION_TOKEN == "YOUR_SESSION_TOKEN_HERE":
        print("Please replace SESSION_TOKEN with your actual Betfair session token")
        print("Get your token from: https://support.developer.betfair.com/hc/en-us/articles/115003900112-How-do-I-get-a-sessionToken")
        return
    
    # Initialize downloader
    downloader = BetfairDataDownloader(SESSION_TOKEN)
    
    # Example: Download horse racing data for March 2017
    sport = "Horse Racing"
    plan = "Basic Plan"
    from_date = datetime(2017, 3, 1)
    to_date = datetime(2017, 3, 31)
    
    # Filter options
    market_types = ["WIN", "PLACE"]  # Win and Place markets
    countries = ["GB", "IE"]  # Great Britain and Ireland
    file_types = ["M"]  # Market data files
    
    # Check available data first
    logger.info("Checking available data...")
    my_data = downloader.get_my_data()
    if my_data:
        logger.info("Available packages:")
        for package in my_data:
            logger.info(f"  - {package['sport']} - {package['plan']} - {package['forDate']}")
    
    # Get collection options
    options = downloader.get_collection_options(sport, plan, from_date, to_date,
                                              market_types, countries, file_types)
    if options:
        logger.info("Available options:")
        logger.info(f"  Market types: {options.get('marketTypesCollection', [])}")
        logger.info(f"  Countries: {options.get('countriesCollection', [])}")
        logger.info(f"  File types: {options.get('fileTypeCollection', [])}")
    
    # Get data size
    size_info = downloader.get_basket_data_size(sport, plan, from_date, to_date,
                                              market_types, countries, file_types)
    if size_info:
        logger.info(f"Data size: {size_info.get('totalSizeMB', 0)} MB, {size_info.get('fileCount', 0)} files")
    
    # Download and process data
    logger.info("Starting data download and processing...")
    df = downloader.download_and_process_data(sport, plan, from_date, to_date,
                                            market_types, countries, file_types,
                                            max_files=5)  # Limit to 5 files for testing
    
    if not df.empty:
        # Save to CSV
        csv_path = downloader.save_to_csv(df, "betfair_horse_racing_data.csv")
        
        # Display sample data
        logger.info("Sample data:")
        print(df.head())
        print(f"\nData shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        logger.info(f"Data saved to: {csv_path}")
    else:
        logger.error("No data was processed successfully")

if __name__ == "__main__":
    main() 