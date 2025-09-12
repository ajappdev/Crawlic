import psutil
import requests
from requests.auth import HTTPProxyAuth
from seleniumbase import Driver
from seleniumbase.config import settings
from selenium_stealth import stealth
import random
import string
import time
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse



PROXIES = [
"184.174.43.150:6690:smjpoqfr:bg3x4gn8qbz5",
"154.6.116.19:5988:smjpoqfr:bg3x4gn8qbz5",
]

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

def kill_all_chrome_processes():
    """
    Aggressively kill all Chrome and ChromeDriver processes
    """
    process_names = ['chrome', 'chromedriver', 'chrome.exe', 'chromedriver.exe']
    total_killed = 0
    
    for process_name in process_names:
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if process_name.lower() in proc.info['name'].lower():
                    print(f"Killing {proc.info['name']} (PID: {proc.info['pid']})")
                    proc.kill()
                    total_killed += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    
    if total_killed > 0:
        print(f"Killed {total_killed} Chrome processes")
        time.sleep(5)  # Longer wait for cleanup
        
        # Double-check and force kill any remaining processes
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if any(name.lower() in proc.info['name'].lower() for name in process_names):
                    print(f"Force killing remaining {proc.info['name']} (PID: {proc.info['pid']})")
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

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

def quit_driver(driver):
    # Quit the driver and release resources
    driver.quit()

    # Explicitly delete the driver object
    del driver

    # Terminate any lingering processes associated with ChromeDriver
    kill_all_chrome_processes()

def initiate_driver(proxy: bool, headless: bool, incognito: bool):
    """
    Initializes and returns a SeleniumBase Chrome driver. Optionally uses a working proxy and headless mode.
    Kills any existing Chrome or chromedriver processes before starting.
    """
    kill_all_chrome_processes()
    
    time.sleep(5)

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
            disable_cookies=True,
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
            disable_cookies=True,
            agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.138 Safari/537.36 AVG/112.0.21002.139",
            do_not_track=True,
            undetectable=True,
            no_sandbox=True,  # Equivalent to adding "--no-sandbox"
            disable_gpu=True,  # Equivalent to adding "--disable-gpu"
        )
        
    driver.set_window_size(1920, 1080)
    return driver

def random_string(length):
    """
    Generates a random string of the specified length containing both letters and numbers.
    :param length: Length of the random string to generate
    :return: Random alphanumeric string
    """
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

def find_contact_email(url):
    """
    Finds and returns email addresses from a website's contact page.
    
    Args:
        url (str): The website URL to search for contact information
        
    Returns:
        list: List of email addresses found, or empty list if none found
    """
    driver = initiate_driver(False, True, True)
    
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
    
    # Load the URL with Selenium
    driver = initiate_driver(False, True, True)
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
    for selector in main_selectors:
        if 'class' in selector:
            main_content = soup.find(selector['tag'], class_=selector['class'])
        else:
            main_content = soup.find(selector['tag'])
        
        if main_content:
            # Clean up unwanted sections within the main content
            for unwanted in main_content.find_all(['nav', 'aside', 'footer', 'header', 'script', 'style', 'img']):
                unwanted.decompose()
            return main_content.get_text(strip=True)
    
    # Fallback: Longest text block if no main content tag is found
    text_blocks = [el.get_text(strip=True) for el in soup.find_all('div')]
    main_content = max(text_blocks, key=len, default="")
    quit_driver(driver)
    return main_content

def get_google_news_links(keyword, max_results=20):
    """
    Searches Google News for a keyword and returns top links.
    
    Args:
        keyword (str): The search keyword/phrase
        max_results (int): Maximum number of results to return (default: 20)
        
    Returns:
        list: List of dictionaries containing news article information
              Each dict has: {'title': str, 'url': str, 'source': str, 'published': str}
    """
    driver = initiate_driver(False, True, True)
    
    try:
        # Encode the search keyword for URL
        encoded_keyword = urllib.parse.quote_plus(keyword)
        
        # Google News search URL
        google_news_url = f"https://news.google.com/search?q={encoded_keyword}"
        
        print(f"Searching Google News for: {keyword}")
        driver.get(google_news_url)
        time.sleep(10)  # Wait for page to load
        
        # Sometimes Google shows a consent dialog, try to handle it
        try:
            # Look for and click "Accept all" or "I agree" buttons
            consent_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'agree') or contains(text(), 'Accept all')]")
            if consent_buttons:
                consent_buttons[0].click()
                time.sleep(2)
        except:
            pass  # Continue if no consent dialog
        
        # Scroll down to load more articles
        scroll_and_load_more(driver, max_results)
        
        # Parse the page source
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Extract news articles
        articles = extract_news_articles(soup, max_results)
        
        print(f"Found {len(articles)} news articles")
        return articles
        
    except Exception as e:
        print(f"Error searching Google News: {e}")
        return []
    
    finally:
        quit_driver(driver)

def scroll_and_load_more(driver, target_results):
    """
    Scrolls down the page to load more news articles.
    
    Args:
        driver: Selenium WebDriver instance
        target_results (int): Target number of results to load
    """
    try:
        last_height = driver.execute_script("return document.body.scrollHeight")
        articles_loaded = 0
        scroll_attempts = 0
        max_scroll_attempts = 10
        
        while articles_loaded < target_results and scroll_attempts < max_scroll_attempts:
            # Scroll down to the bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Check if new content loaded
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            # Count current articles
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            current_articles = count_articles(soup)
            
            if current_articles >= target_results or new_height == last_height:
                break
                
            last_height = new_height
            articles_loaded = current_articles
            scroll_attempts += 1
            
    except Exception as e:
        print(f"Error during scrolling: {e}")

def count_articles(soup):
    """
    Counts the number of articles currently loaded on the page.
    
    Args:
        soup: BeautifulSoup object of the page
        
    Returns:
        int: Number of articles found
    """
    # Google News article selectors (these may change over time)
    selectors = [
        'article[jslog]',
        'article[data-n-tid]',
        'div[data-n-tid]',
        '.JtKRv',  # Common Google News article class
        '.xrnccd'  # Another common class
    ]
    
    for selector in selectors:
        articles = soup.select(selector)
        if articles:
            return len(articles)
    
    return 0

def extract_news_articles(soup, max_results):
    """
    Extracts news article information from the parsed HTML.
    
    Args:
        soup: BeautifulSoup object of the Google News page
        max_results (int): Maximum number of articles to extract
        
    Returns:
        list: List of article dictionaries
    """
    articles = []
    
    # Multiple selectors to try (Google frequently changes their HTML structure)
    article_selectors = [
        'article[jslog]',
        'article[data-n-tid]', 
        'div[data-n-tid]',
        '.JtKRv',
        '.xrnccd',
        'article'
    ]
    
    found_articles = []
    
    # Try different selectors until we find articles
    for selector in article_selectors:
        found_articles = soup.select(selector)
        if found_articles and len(found_articles) > 5:  # Make sure we found a good set
            break
    
    if not found_articles:
        print("Could not find articles with known selectors, trying alternative approach...")
        # Fallback: look for links that seem like news articles
        return extract_articles_fallback(soup, max_results)
    
    print(f"Found {len(found_articles)} article elements using selector")
    
    for i, article_elem in enumerate(found_articles[:max_results]):
        try:
            article_info = parse_article_element(article_elem)
            if article_info and article_info['url']:
                articles.append(article_info)
                
        except Exception as e:
            print(f"Error parsing article {i}: {e}")
            continue
    
    return articles

def parse_article_element(article_elem):
    """
    Parses a single article element to extract information.
    
    Args:
        article_elem: BeautifulSoup element representing an article
        
    Returns:
        dict: Article information or None if parsing failed
    """
    try:
        # Find the main link
        link_elem = article_elem.find('a')
        if not link_elem:
            return None
        
        # Extract title
        title = ""
        title_selectors = ['h3', 'h4', '[role="heading"]', '.JtKRv h3', '.JtKRv h4']
        for selector in title_selectors:
            title_elem = article_elem.select_one(selector)
            if title_elem:
                title = title_elem.get_text().strip()
                break
        
        if not title:
            title = link_elem.get_text().strip()
        
        # Extract URL (Google News URLs are usually redirects)
        url = link_elem.get('href', '')
        if url.startswith('./'):
            url = 'https://news.google.com' + url[1:]
        elif url.startswith('/'):
            url = 'https://news.google.com' + url
        
        # Extract source
        source = ""
        source_selectors = ['.wEwyrc', '.vr1PYe', '.CEMjEf']
        for selector in source_selectors:
            source_elem = article_elem.select_one(selector)
            if source_elem:
                source = source_elem.get_text().strip()
                break
        
        # Extract published time
        published = ""
        time_selectors = ['time', '.WW6dff', '.r0bn4c']
        for selector in time_selectors:
            time_elem = article_elem.select_one(selector)
            if time_elem:
                published = time_elem.get_text().strip()
                break
        
        return {
            'title': title,
            'url': url,
            'source': source,
            'published': published
        }
        
    except Exception as e:
        print(f"Error parsing article element: {e}")
        return None

def extract_articles_fallback(soup, max_results):
    """
    Fallback method to extract articles when main selectors fail.
    
    Args:
        soup: BeautifulSoup object
        max_results (int): Maximum number of results
        
    Returns:
        list: List of article dictionaries
    """
    articles = []
    
    # Look for all links that might be news articles
    links = soup.find_all('a', href=True)
    
    for link in links[:max_results * 3]:  # Check more links to filter out non-articles
        try:
            href = link.get('href', '')
            text = link.get_text().strip()
            
            # Filter out non-article links
            if (len(text) > 20 and  # Reasonable title length
                not href.startswith('#') and  # Not anchor links
                not 'google.com/search' in href and  # Not search links
                text.lower() not in ['more', 'next', 'previous', 'home']):  # Not navigation
                
                if href.startswith('./'):
                    href = 'https://news.google.com' + href[1:]
                elif href.startswith('/'):
                    href = 'https://news.google.com' + href
                
                articles.append({
                    'title': text,
                    'url': href,
                    'source': '',
                    'published': ''
                })
                
                if len(articles) >= max_results:
                    break
                    
        except Exception:
            continue
    
    return articles

def get_google_news_urls_only(keyword, max_results=20):
    """
    Simplified function that returns only URLs from Google News search.
    
    Args:
        keyword (str): Search keyword
        max_results (int): Maximum number of URLs to return
        
    Returns:
        list: List of URLs
    """
    articles = get_google_news_links(keyword, max_results)
    return [article['url'] for article in articles if article['url']]

def print_news_results(articles):
    """
    Pretty prints the news search results.
    
    Args:
        articles (list): List of article dictionaries
    """
    print(f"\n=== Found {len(articles)} News Articles ===\n")
    
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title']}")
        if article['source']:
            print(f"   Source: {article['source']}")
        if article['published']:
            print(f"   Published: {article['published']}")
        print(f"   URL: {article['url']}")
        print("-" * 80)