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