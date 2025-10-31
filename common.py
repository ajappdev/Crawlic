# GENERAL IMPORTATIONS
import requests
from requests.auth import HTTPProxyAuth
import random
import string
import time
import re
import subprocess
import os
import signal
import psutil
from decouple import Config, RepositoryEnv, config
import os
from pathlib import Path
from typing import Any, Dict, Optional, List, Union

# SCRAPING IMPORTATIONS
from seleniumbase import Driver
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Fetching ENV Variables from .env file
BASE_DIR = Path(__file__).resolve().parent
DOTENV_FILE = os.path.join(BASE_DIR, '.env')

try:
    # Try to read from .env file (for local development)
    env_config = Config(RepositoryEnv(DOTENV_FILE))
    OPENAI_ORGANIZATION_ID = env_config.get('ORGANIZATION_ID')
    OPENAI_PROJECT_ID = env_config.get('PROJECT_ID')
    OPENAI_API_KEY = env_config.get('OPENAI_API_KEY')
    POSTGRES_PASSWORD = env_config.get('POSTGRES_PASSWORD')
    POSTGRES_DB = env_config.get('POSTGRES_DB')
    POSTGRES_USER = env_config.get('POSTGRES_USER')
    POSTGRES_HOST = env_config.get('POSTGRES_HOST')
    POSTGRES_PORT = env_config.get('POSTGRES_PORT')
except Exception as e:
    # Fallback to environment variables (for production/Docker)
    OPENAI_ORGANIZATION_ID = config('ORGANIZATION_ID')
    OPENAI_PROJECT_ID = config('PROJECT_ID')
    OPENAI_API_KEY = config('OPENAI_API_KEY')
    POSTGRES_PASSWORD = config('POSTGRES_PASSWORD')
    POSTGRES_DB = config('POSTGRES_DB')
    POSTGRES_USER = config('POSTGRES_USER')
    POSTGRES_HOST = config('POSTGRES_HOST')
    POSTGRES_PORT = config('POSTGRES_PORT')

# GLOBAL_VARIABLES
PROXIES = [
"184.174.43.150:6690:smjpoqfr:bg3x4gn8qbz5",
"154.6.116.19:5988:smjpoqfr:bg3x4gn8qbz5",
]

##############################################
##############################################
##############################################
# DECLARING FUNCTIONS
##############################################
##############################################
##############################################

##############################################
# FUNCTIONS TO USE AFTER SCRAPING
##############################################

def quit_driver(driver):
    # Quit the driver and release resources
    driver.quit()

    # Explicitly delete the driver object
    del driver

    kill_all_chrome_processes_linux()


def kill_all_chrome_processes_linux():
    """
    Kill all running Chrome/Chromedriver related processes in the container.
    Useful for cleaning up after Selenium scraping sessions to prevent zombie
    accumulation.
    """
    try:
        # Get all running processes
        result = subprocess.run(
            ["ps", "aux"], capture_output=True, text=True
        )
        
        for line in result.stdout.splitlines():
            if any(proc in line.lower() for proc in ["chrome", "chromedriver"]):
                parts = line.split()
                pid = int(parts[1])  # PID is the second column
                try:
                    os.kill(pid, signal.SIGKILL)
                    print(f"🔪 Killed process {pid}: {line}")
                except Exception as e:
                    print(f"⚠️ Could not kill process {pid}: {e}")
    except Exception as e:
        print(f"❌ Error while killing chrome processes: {e}")


# FUNCTIONS TO USE WHEN SCRAPING BEHIND A PROXY
def parse_proxy(proxy_string):
    """
    Parses a proxy string in the format 'ip:port:username:password' and returns a dictionary
    with the corresponding fields. Returns None if the format is incorrect.
    """
    parts = proxy_string.split(':')
    if len(parts) == 4:
        ip, port, username, password = parts
        return {
            'ip': ip,
            'port': port,
            'username': username,
            'password': password
        }
    return None

def find_working_proxy():
    """
    Randomly shuffles the list of proxies and tests each one until a working proxy is found.
    Returns the first working proxy as a dictionary, or None if none work.
    """
    random.shuffle(PROXIES)
    for proxy in PROXIES:
        parsed_proxy = parse_proxy(proxy)
        if test_proxy(parsed_proxy):
            return parsed_proxy
    print("No working proxy found.")
    return None

def test_proxy(proxy):
    """
    Tests if a given proxy (dictionary with ip, port, username, password) is working by making a request
    to http://httpbin.org/ip. Returns True if the proxy works, False otherwise.
    """
    print(f"Testing Proxy : {proxy['ip']}:{proxy['port']}")
    url = "http://httpbin.org/ip"  # Simple URL to test the proxy
    proxies = {
        "http": f"http://{proxy['ip']}:{proxy['port']}",
        "https": f"http://{proxy['ip']}:{proxy['port']}",
    }
    auth = HTTPProxyAuth(proxy['username'], proxy['password'])

    try:
        response = requests.get(url, proxies=proxies, auth=auth, timeout=5)
        if response.status_code == 200:
            print(f"Proxy {proxy} works! IP: {response.json()['origin']}")
            return True
    except requests.exceptions.RequestException as e:
        print(f"Proxy {proxy} failed: {e}")
    return False


##############################################
# FUNCTIONS TO USE WHILE SCRAPING
##############################################

def initiate_driver(proxy: bool, headless: bool, incognito: bool, disable_cookies: bool):
    """
    Initializes and returns a SeleniumBase Chrome driver. Optionally uses a working proxy and headless mode.
    Kills any existing Chrome or chromedriver processes before starting.
    """
    if OS_MACHINE == "Windows":
        kill_all_chrome_processes_windows()
    elif OS_MACHINE == "Linux":
        kill_all_chrome_processes_linux()
    
    # time.sleep(5)
    pass

    print("launching the driver")
    if proxy:
        working_proxy = find_working_proxy()
        proxy_ip = working_proxy['ip']
        proxy_port = working_proxy['port']
        proxy_username = working_proxy['username']
        proxy_password = working_proxy['password']

        proxy = f"{proxy_username}:{proxy_password}@{proxy_ip}:{proxy_port}"

        # Initialize SeleniumBase driver
        driver = Driver(
            browser="chrome",
            uc=True,
            headless2=headless,
            incognito=incognito,
            agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.138 Safari/537.36 AVG/112.0.21002.139",
            do_not_track=True,
            undetectable=True,
            disable_cookies=disable_cookies,
            no_sandbox=True,  # Equivalent to adding "--no-sandbox"
            disable_gpu=True,  # Equivalent to adding "--disable-gpu"
            proxy=proxy  # Add the proxy here
        )
    else:
        # Initialize SeleniumBase driver
        driver = Driver(
            browser="chrome",
            uc=True,
            headless2=headless,
            incognito=incognito,
            disable_cookies=disable_cookies,
            agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.138 Safari/537.36 AVG/112.0.21002.139",
            do_not_track=True,
            undetectable=True,
            no_sandbox=True,  # Equivalent to adding "--no-sandbox"
            disable_gpu=True,  # Equivalent to adding "--disable-gpu"
        )
        
    driver.set_window_size(1920, 1080)
    return driver

def find_contact_email(url):
    """
    Finds and returns email addresses from a website's contact page.
    
    Args:
        url (str): The website URL to search for contact information
        
    Returns:
        list: List of email addresses found, or empty list if none found
    """
    driver = initiate_driver(False, True, True, False)
    
    try:
        # Start with the main page
        driver.get(url)
        time.sleep(3)
        
        # Get the base domain for building absolute URLs
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        
        # Look for contact page links
        contact_urls = find_contact_page_links(driver, base_url)
        
        # Search for emails on main page first
        emails = extract_emails_from_page(driver)
        
        if emails:
            print(f"Found emails on main page: {emails}")
            return emails
        
        # If no emails found on main page, try contact pages
        for contact_url in contact_urls:
            try:
                print(f"Checking contact page: {contact_url}")
                driver.get(contact_url)
                time.sleep(5)
                
                emails = extract_emails_from_page(driver)
                if emails:
                    print(f"Found emails on {contact_url}: {emails}")
                    return emails
                    
            except Exception as e:
                print(f"Error accessing {contact_url}: {e}")
                continue
        
        print("No emails found on any contact pages")
        return []
        
    except Exception as e:
        print(f"Error during email extraction: {e}")
        return []
    
    finally:
        quit_driver(driver)

def find_contact_page_links(driver, base_url):
    """
    Finds potential contact page URLs on the current page.
    
    Args:
        driver: Selenium WebDriver instance
        base_url (str): Base URL of the website
        
    Returns:
        list: List of contact page URLs
    """
    contact_urls = []
    
    try:
        # Get page source and parse with BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Common contact page indicators
        contact_keywords = [
            'contact', 'contact-us', 'contact_us', 'contactus',
            'about', 'about-us', 'about_us', 'aboutus',
            'team', 'staff', 'management',
            'support', 'help', 'feedback'
        ]
        
        # Find all links
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href'].lower()
            link_text = link.get_text().lower().strip()
            
            # Check if link or text contains contact keywords
            is_contact_link = any(
                keyword in href or keyword in link_text 
                for keyword in contact_keywords
            )
            
            if is_contact_link:
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    full_url = base_url + href
                elif href.startswith('http'):
                    full_url = href
                else:
                    full_url = urljoin(base_url + '/', href)
                
                if full_url not in contact_urls:
                    contact_urls.append(full_url)
        
        # Common contact page paths to try even if no links found
        common_paths = [
            '/contact', '/contact-us', '/contact_us', '/contactus',
            '/about', '/about-us', '/about_us', '/aboutus',
            '/team', '/staff', '/support', '/help'
        ]
        
        for path in common_paths:
            full_url = base_url + path
            if full_url not in contact_urls:
                contact_urls.append(full_url)
    
    except Exception as e:
        print(f"Error finding contact links: {e}")
    
    return contact_urls[:10]  # Limit to first 10 URLs to avoid too many requests

def extract_emails_from_page(driver):
    """
    Extracts email addresses from the current page.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        list: List of unique email addresses found
    """
    try:
        # Get page source and parse with BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "noscript"]):
            script.decompose()
        
        # Get all text content
        text_content = soup.get_text()
        
        # Also check for emails in href attributes and other attributes
        all_content = text_content + " "
        
        # Check mailto links
        mailto_links = soup.find_all('a', href=re.compile(r'^mailto:', re.I))
        for link in mailto_links:
            href = link.get('href', '')
            if href.startswith('mailto:'):
                email = href.replace('mailto:', '').split('?')[0]  # Remove query parameters
                all_content += f" {email} "
        
        # Check data attributes and other attributes that might contain emails
        for element in soup.find_all():
            for attr_name, attr_value in element.attrs.items():
                if isinstance(attr_value, str) and '@' in attr_value:
                    all_content += f" {attr_value} "
        
        # Email regex pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        # Find all email addresses
        emails = re.findall(email_pattern, all_content)
        
        # Filter out common false positives and clean emails
        filtered_emails = []
        ignore_domains = [
            'example.com', 'test.com', 'domain.com', 'yoursite.com',
            'yourdomain.com', 'website.com', 'company.com', 'business.com',
            'sentry.io', 'google-analytics.com', 'googletagmanager.com'
        ]
        
        for email in emails:
            email = email.lower().strip()
            domain = email.split('@')[1] if '@' in email else ''
            
            # Skip obvious false positives
            if (domain not in ignore_domains and 
                not email.endswith('.png') and 
                not email.endswith('.jpg') and 
                not email.endswith('.js') and
                len(email) > 5 and
                '.' in domain):
                filtered_emails.append(email)
        
        # Remove duplicates while preserving order
        unique_emails = list(dict.fromkeys(filtered_emails))
        
        return unique_emails
        
    except Exception as e:
        print(f"Error extracting emails: {e}")
        return []

def get_primary_contact_email(url):
    """
    Simplified function that returns the first/primary email found.
    
    Args:
        url (str): Website URL to search
        
    Returns:
        str: First email address found, or None if no email found
    """
    emails = find_contact_email(url)
    return emails[0] if emails else None

def get_source_content(url):
    """
    Scrapes and cleans content from a webpage, preserving links and structure.
    
    Args:
        url: The URL to scrape
        
    Returns:
        Cleaned HTML string with minimal formatting
    """
    # Load the URL with Selenium
    driver = initiate_driver(False, False, False, False)
    driver.get(url)
    time.sleep(10)

    # Get the page source and parse with BeautifulSoup
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Define possible selectors for main content
    main_selectors = [
        {'tag': 'article'},
        {'tag': 'div', 'class': 'post-content'},
        {'tag': 'div', 'class': 'blog-post'},
        {'tag': 'div', 'class': 'article-content'},
        {'tag': 'main'}
    ]
    
    # Try to find the main content
    main_content = None
    for selector in main_selectors:
        if 'class' in selector:
            main_content = soup.find(selector['tag'], class_=selector['class'])
        else:
            main_content = soup.find(selector['tag'])
        
        if main_content:
            break
    
    # Fallback: Find the div with the most text content
    if not main_content:
        text_blocks = [(el, len(el.get_text(strip=True))) for el in soup.find_all('div')]
        if text_blocks:
            main_content = max(text_blocks, key=lambda x: x[1])[0]
    
    # Clean up the content
    if main_content:
        # Remove scripts and styles (always unwanted)
        for unwanted in main_content.find_all(['script', 'style']):
            unwanted.decompose()

        # Remove visual elements but keep their parent containers
        for unwanted in main_content.find_all(['img', 'svg', 'iframe']):
            unwanted.decompose()

        # Only remove structural elements if they don't contain links
        for unwanted in main_content.find_all(['nav', 'aside', 'footer', 'header']):
            if len(unwanted.find_all('a')) == 0:
                unwanted.decompose()

        # Remove HTML comments
        from bs4 import Comment
        for comment in main_content.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        
        # Define allowed HTML tags
        allowed_tags = {
            'p', 'ul', 'ol', 'li', 'div', 'span', 'a', 'button',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'strong', 'em', 'blockquote', 'pre', 'code'
        }
        
        # Remove attributes from the main_content tag itself
        main_content.attrs = {}
        
        # Clean tags: unwrap non-allowed tags and strip attributes from allowed tags
        for tag in main_content.find_all(True):
            if tag.name not in allowed_tags:
                tag.unwrap()
            else:
                # Keep only href and id attributes
                allowed_attrs = {}
                if "href" in tag.attrs:
                    allowed_attrs["href"] = tag["href"]
                if "id" in tag.attrs:
                    allowed_attrs["id"] = tag["id"]
                tag.attrs = allowed_attrs
        
        # Simplify redundant nested divs/spans
        simplify_nested_tags(main_content)
        
        # Remove empty tags
        remove_empty_tags(main_content)
        
        # Convert to string and clean up whitespace
        result = str(main_content)
        result = result.replace('\n', '')
        
        # Remove excessive spaces
        import re
        result = re.sub(r'\s+', ' ', result)
        result = re.sub(r'>\s+<', '><', result)
        result = result.strip()
    else:
        result = ""
    
    quit_driver(driver)
    return result

def simplify_nested_tags(element):
    """
    Remove redundant nested divs/spans that don't add structural value.
    Only removes tags with a single child of the same type and no direct text.
    """
    changed = True
    while changed:
        changed = False
        for tag in element.find_all(True):
            if tag.name in ['div', 'span']:
                children_tags = [c for c in tag.children if hasattr(c, 'name')]
                direct_text = ''.join([str(c) for c in tag.children if isinstance(c, str)]).strip()
                
                # Only unwrap if there's exactly one child of the same type and no direct text
                if len(children_tags) == 1 and children_tags[0].name == tag.name and not direct_text:
                    tag.unwrap()
                    changed = True

def remove_empty_tags(element):
    """
    Remove tags that contain no text content.
    Runs multiple times to catch nested empty tags.
    """
    changed = True
    while changed:
        changed = False
        for tag in element.find_all(True):
            if not tag.get_text(strip=True):
                tag.decompose()
                changed = True

##############################################
# GENERAL FUNCTIONS
##############################################

def random_string(length):
    """
    Generates a random string of the specified length containing both letters and numbers.
    :param length: Length of the random string to generate
    :return: Random alphanumeric string
    """
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

def is_valid_json(
    input_data: Union[str, dict],
    required_keys: Optional[List[str]] = None,
    optional_keys: Optional[List[str]] = None,
    key_types: Optional[Dict[str, type]] = None,
    strict: bool = False) -> tuple[bool, Optional[str]]:
    """
    Validates if input is valid JSON with correct format.
    
    Args:
        input_data: String to parse as JSON or dict to validate
        required_keys: List of keys that must be present
        optional_keys: List of keys that may be present (only checked if strict=True)
        key_types: Dict mapping key names to expected types (e.g., {'name': str, 'age': int})
        strict: If True, only required_keys and optional_keys are allowed
    
    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: Boolean indicating if validation passed
        - error_message: None if valid, otherwise description of the error
    """
    
    # Step 1: Parse JSON if it's a string
    if isinstance(input_data, str):
        try:
            data = json.loads(input_data)
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON syntax: {str(e)}"
    elif isinstance(input_data, dict):
        data = input_data
    else:
        return False, f"Input must be a string or dict, got {type(input_data).__name__}"
    
    # Step 2: Check if parsed data is a dictionary
    if not isinstance(data, dict):
        return False, f"JSON must be an object/dict, got {type(data).__name__}"
    
    # Step 3: Check required keys
    if required_keys:
        missing_keys = set(required_keys) - set(data.keys())
        if missing_keys:
            return False, f"Missing required keys: {', '.join(missing_keys)}"
    
    # Step 4: Check for unexpected keys in strict mode
    if strict and (required_keys or optional_keys):
        allowed_keys = set(required_keys or []) | set(optional_keys or [])
        unexpected_keys = set(data.keys()) - allowed_keys
        if unexpected_keys:
            return False, f"Unexpected keys: {', '.join(unexpected_keys)}"
    
    # Step 5: Check key types
    if key_types:
        for key, expected_type in key_types.items():
            if key in data:
                if not isinstance(data[key], expected_type):
                    actual_type = type(data[key]).__name__
                    expected_type_name = expected_type.__name__
                    return False, f"Key '{key}' has wrong type: expected {expected_type_name}, got {actual_type}"
    
    return True, None