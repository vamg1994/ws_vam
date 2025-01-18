import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import List, Dict, Any
import time
from urllib.parse import urljoin
import re
import webcolors
from PIL import Image
from collections import defaultdict
import json

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

def get_all_urls(url: str) -> pd.DataFrame:
    """
    Scrape all URLs from a webpage and return them in a DataFrame.
    
    Args:
        url (str): The webpage URL to scrape
        
    Returns:
        pd.DataFrame: DataFrame containing URLs, link text, and link type
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        urls_data = []
        
        # Find all <a> tags
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                # Convert relative URLs to absolute
                absolute_url = urljoin(url, href)
                
                # Determine link type
                link_type = 'Internal' if url in absolute_url else 'External'
                if href.startswith('#'):
                    link_type = 'Anchor'
                elif href.startswith('mailto:'):
                    link_type = 'Email'
                elif href.startswith('tel:'):
                    link_type = 'Phone'
                
                urls_data.append({
                    'url': absolute_url,
                    'text': link.get_text(strip=True) or '[No Text]',
                    'type': link_type
                })
        
        # Create DataFrame and remove duplicates
        df = pd.DataFrame(urls_data)
        df = df.drop_duplicates(subset=['url'])
        
        return df
    
    except Exception as e:
        raise Exception(f"Error scraping URLs: {str(e)}")

def get_colors(url: str) -> List[Dict[str, str]]:
    """
    Scrape colors from a webpage's CSS and HTML.
    
    Args:
        url (str): The webpage URL to scrape
        
    Returns:
        List[Dict[str, str]]: List of dictionaries containing color information
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        colors = []
        # Regular expressions for different color formats
        color_patterns = {
            'hex': r'#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b',
            'rgb': r'rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)',
            'rgba': r'rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([0-1]\.?\d*)\s*\)',
        }
        
        def process_style_content(content: str, source: str):
            for format_name, pattern in color_patterns.items():
                matches = re.finditer(pattern, content)
                for match in matches:
                    color_value = match.group(0)  # Get the full match
                    if format_name == 'hex':
                        colors.append({
                            'color': color_value,
                            'format': 'hex',
                            'source': source
                        })
                    elif format_name == 'rgb':
                        colors.append({
                            'color': color_value,
                            'format': 'rgb',
                            'source': source
                        })
                    elif format_name == 'rgba':
                        colors.append({
                            'color': color_value,
                            'format': 'rgba',
                            'source': source
                        })

        # Extract colors from style tags
        for style in soup.find_all('style'):
            if style.string:
                process_style_content(style.string, 'CSS')

        # Extract colors from inline styles
        for tag in soup.find_all(style=True):
            process_style_content(tag['style'], 'Inline')

        # Extract colors from CSS files
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                if not href.startswith(('http://', 'https://')):
                    base_url = '/'.join(url.split('/')[:-1])
                    href = f"{base_url}/{href}"
                try:
                    css_response = requests.get(href)
                    if css_response.ok:
                        process_style_content(css_response.text, 'External CSS')
                except:
                    continue

        # Remove duplicates while preserving order
        unique_colors = []
        seen = set()
        for color in colors:
            color_key = (color['color'], color['format'])
            if color_key not in seen:
                seen.add(color_key)
                unique_colors.append(color)
        
        return unique_colors
        
    except Exception as e:
        raise Exception(f"Error scraping colors: {str(e)}")

def get_images(url: str) -> List[Dict[str, str]]:
    """
    Scrape all images from a webpage.
    
    Args:
        url (str): The webpage URL to scrape
        
    Returns:
        List[Dict[str, str]]: List of dictionaries containing image information
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        images = []
        for img in soup.find_all('img'):
            # Get image source
            src = img.get('src', '')
            if not src:
                continue
                
            # Convert relative URLs to absolute
            if not src.startswith(('http://', 'https://', 'data:')):
                src = urljoin(url, src)
            
            # Get image metadata
            image_data = {
                'url': src,
                'alt': img.get('alt', 'No alt text'),
                'title': img.get('title', 'No title'),
                'width': img.get('width', 'Not specified'),
                'height': img.get('height', 'Not specified'),
                'type': 'data:image' if src.startswith('data:') else src.split('.')[-1].lower() if '.' in src else 'unknown'
            }
            
            # Try to get actual image dimensions if not specified in HTML
            if image_data['width'] == 'Not specified' and not src.startswith('data:'):
                try:
                    img_response = requests.get(src, stream=True)
                    if img_response.ok:
                        img_response.raw.decode_content = True
                        img_temp = Image.open(img_response.raw)
                        image_data['width'], image_data['height'] = img_temp.size
                except:
                    pass
            
            images.append(image_data)
        
        return images
        
    except Exception as e:
        raise Exception(f"Error scraping images: {str(e)}")

def analyze_performance(url: str) -> Dict[str, Any]:
    """
    Analyze webpage performance metrics.
    
    Args:
        url (str): The webpage URL to analyze
        
    Returns:
        Dict[str, Any]: Dictionary containing performance metrics
    """
    try:
        # Start timing the request
        start_time = time.time()
        
        # Make request and get response
        response = requests.get(url)
        response.raise_for_status()
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Initialize performance metrics
        performance_data = {
            'response_time': round(response_time, 2),
            'page_size': len(response.content) / 1024,  # Convert to KB
            'status_code': response.status_code,
            'content_type': response.headers.get('content-type', 'Not specified'),
            'encoding': response.encoding,
            'compression': response.headers.get('content-encoding', 'None'),
            'cache_control': response.headers.get('cache-control', 'Not specified'),
            'server': response.headers.get('server', 'Not specified'),
            'resources': defaultdict(int),
            'resource_sizes': defaultdict(float),
            'total_resources': 0,
            'headers': dict(response.headers),
        }
        
        # Analyze resources
        # Scripts
        scripts = soup.find_all('script', src=True)
        performance_data['resources']['scripts'] = len(scripts)
        
        # Stylesheets
        styles = soup.find_all('link', rel='stylesheet')
        performance_data['resources']['stylesheets'] = len(styles)
        
        # Images
        images = soup.find_all('img')
        performance_data['resources']['images'] = len(images)
        
        # Calculate total resources
        performance_data['total_resources'] = sum(performance_data['resources'].values())
        
        # Try to get sizes of external resources
        for resource in scripts + styles + images:
            src = resource.get('src') or resource.get('href')
            if src:
                try:
                    if not src.startswith(('http://', 'https://')):
                        src = urljoin(url, src)
                    resource_response = requests.head(src, timeout=2)
                    size = int(resource_response.headers.get('content-length', 0)) / 1024  # KB
                    if resource.name == 'script':
                        performance_data['resource_sizes']['scripts'] += size
                    elif resource.name == 'link':
                        performance_data['resource_sizes']['stylesheets'] += size
                    elif resource.name == 'img':
                        performance_data['resource_sizes']['images'] += size
                except:
                    continue
        
        # Round resource sizes
        for key in performance_data['resource_sizes']:
            performance_data['resource_sizes'][key] = round(performance_data['resource_sizes'][key], 2)
        
        # Calculate total page weight including resources
        performance_data['total_page_weight'] = round(
            performance_data['page_size'] + sum(performance_data['resource_sizes'].values()),
            2
        )
        
        return performance_data
        
    except Exception as e:
        raise Exception(f"Error analyzing performance: {str(e)}")

def analyze_seo(url: str) -> Dict[str, Any]:
    """
    Analyze webpage SEO metrics.
    
    Args:
        url (str): The webpage URL to analyze
        
    Returns:
        Dict[str, Any]: Dictionary containing SEO metrics
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Initialize SEO data structure
        seo_data = {
            'meta_tags': {},
            'headings': {f'h{i}': [] for i in range(1, 7)},
            'images': {'with_alt': 0, 'without_alt': 0},
            'links': {'internal': 0, 'external': 0, 'nofollow': 0},
            'structured_data': [],
            'canonical_url': None,
            'robots_meta': None,
            'viewport': None,
            'lang': soup.html.get('lang', 'Not specified'),
            'text_html_ratio': 0,
            'word_count': 0
        }
        
        # Meta tags analysis
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            if tag.get('name'):
                seo_data['meta_tags'][tag.get('name')] = tag.get('content')
            elif tag.get('property'):
                seo_data['meta_tags'][tag.get('property')] = tag.get('content')
        
        # Special meta tags
        seo_data['robots_meta'] = seo_data['meta_tags'].get('robots', 'Not specified')
        seo_data['viewport'] = seo_data['meta_tags'].get('viewport', 'Not specified')
        
        # Canonical URL
        canonical = soup.find('link', rel='canonical')
        if canonical:
            seo_data['canonical_url'] = canonical.get('href')
        
        # Headings analysis
        for i in range(1, 7):
            headings = soup.find_all(f'h{i}')
            seo_data['headings'][f'h{i}'] = [h.get_text(strip=True) for h in headings]
        
        # Image analysis
        images = soup.find_all('img')
        for img in images:
            if img.get('alt'):
                seo_data['images']['with_alt'] += 1
            else:
                seo_data['images']['without_alt'] += 1
        
        # Link analysis
        links = soup.find_all('a')
        for link in links:
            href = link.get('href', '')
            if href.startswith(('http://', 'https://')):
                if url in href:
                    seo_data['links']['internal'] += 1
                else:
                    seo_data['links']['external'] += 1
            else:
                seo_data['links']['internal'] += 1
                
            if link.get('rel') and 'nofollow' in link.get('rel'):
                seo_data['links']['nofollow'] += 1
        
        # Structured data analysis
        script_tags = soup.find_all('script', type='application/ld+json')
        for script in script_tags:
            try:
                seo_data['structured_data'].append(json.loads(script.string))
            except:
                continue
        
        # Text to HTML ratio calculation
        text_content = soup.get_text(strip=True)
        html_content = str(soup)
        seo_data['text_html_ratio'] = round(
            (len(text_content) / len(html_content)) * 100, 2
        )
        
        # Word count
        seo_data['word_count'] = len(text_content.split())
        
        return seo_data
        
    except Exception as e:
        raise Exception(f"Error analyzing SEO: {str(e)}")
