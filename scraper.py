import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import List
import time

def get_raw_html(url: str) -> str:
    """
    Fetch and return the raw HTML content from a given URL.
    
    Args:
        url (str): The URL to fetch HTML from
        
    Returns:
        str: Raw HTML content
        
    Raises:
        Exception: If there's an error during fetching
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Add delay to be respectful to servers
        time.sleep(1)
        
        # Fetch the webpage
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Return formatted HTML
        soup = BeautifulSoup(response.text, 'lxml')
        return soup.prettify()
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch the webpage: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to process HTML content: {str(e)}")

def scrape_tables(url: str) -> List[pd.DataFrame]:
    """
    Scrape all tables from a given URL and return them as a list of pandas DataFrames.
    
    Args:
        url (str): The URL to scrape tables from
        
    Returns:
        List[pd.DataFrame]: List of extracted tables
        
    Raises:
        Exception: If there's an error during scraping
    """
    # Add headers to avoid blocking
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Add delay to be respectful to servers
        time.sleep(1)
        
        # Fetch the webpage
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Find all tables
        table_elements = soup.find_all('table')
        
        # Convert tables to DataFrames
        tables = []
        for table in table_elements:
            try:
                df = pd.read_html(str(table))[0]
                # Clean the DataFrame
                df = df.replace('\n', ' ', regex=True)
                df = df.replace('\r', ' ', regex=True)
                tables.append(df)
            except Exception:
                continue
                
        return tables
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch the webpage: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to parse tables: {str(e)}")
