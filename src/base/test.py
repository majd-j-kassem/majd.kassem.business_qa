from webdriver_manager.chrome import ChromeDriverManager
import time
import logging

# Set up basic logging to see what webdriver_manager is doing
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

print("Attempting to install/update ChromeDriver...")
start_time = time.time()
try:
    driver_path = ChromeDriverManager().install()
    end_time = time.time()
    print(f"ChromeDriver installation/check complete in {end_time - start_time:.2f} seconds.")
    print(f"ChromeDriver executable path: {driver_path}")
except Exception as e:
    print(f"Error during ChromeDriver installation/check: {e}")

print("\nNow, let's try to launch a simple Chrome browser to see if it's quick.")
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

try:
    # Launch Chrome without any special options first
    print("Launching Chrome (minimal options)...")
    start_time_launch = time.time()
    service = ChromeService(executable_path=driver_path)
    driver = webdriver.Chrome(service=service)
    driver.quit()
    end_time_launch = time.time()
    print(f"Chrome launched and quit successfully in {end_time_launch - start_time_launch:.2f} seconds.")
except Exception as e:
    print(f"Error launching Chrome: {e}")

print("\nNow, launching Chrome with your specific options (headless if applicable)...")
try:
    options = ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--headless') # Add this if you usually run headless
    options.add_argument('--disable-gpu') # Recommended for headless

    start_time_launch_options = time.time()
    service_options = ChromeService(executable_path=driver_path)
    driver_with_options = webdriver.Chrome(service=service_options, options=options)
    driver_with_options.quit()
    end_time_launch_options = time.time()
    print(f"Chrome launched and quit with options successfully in {end_time_launch_options - start_time_launch_options:.2f} seconds.")
except Exception as e:
    print(f"Error launching Chrome with options: {e}")