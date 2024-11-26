from urllib.parse import urlparse
import re

def validate_url(url: str) -> bool:
    """
    Validate if the given string is a proper URL.
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def format_table_name(url: str, index: int) -> str:
    """
    Generate a filename for the table based on URL and index.
    
    Args:
        url (str): Source URL
        index (int): Table index
        
    Returns:
        str: Formatted table name
    """
    # Extract domain name
    domain = urlparse(url).netloc
    # Remove non-alphanumeric characters
    domain = re.sub(r'[^\w\s-]', '', domain)
    # Create filename
    return f"{domain}_table_{index + 1}"
