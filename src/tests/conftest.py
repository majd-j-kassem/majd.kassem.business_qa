import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
import os
import shutil
import tempfile
import logging
from base.web_driver_factory import WebDriverFactory # Your factory

# --- NEW IMPORTS FOR API INTERACTION ---
import requests
import time
# You might need specific imports for your API client or database utility
# Example: from your_application.api_client import register_user_api, delete_user_api
# Example: from your_application.db_utils import create_pending_teacher_db, delete_teacher_db
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException, TimeoutException, ElementNotInteractableException
from selenium.webdriver.support import expected_conditions as EC


# Configure logging
# Ensure this basic config is only run if handlers are not already set up
# This prevents duplicate log messages if pytest or other modules already configure logging
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default="chrome", help="Type of browser: chrome or firefox")
    parser.addoption("--baseurl", action="store", default="http://127.0.0.1:8000", help="Base URL for testing")

# Move browser and base_url fixtures to the top and ensure they are session scoped
@pytest.fixture(scope="session")
def browser(request):
    """Fixture to get the --browser option value."""
    return request.config.getoption("--browser")

@pytest.fixture(scope="session")
def base_url_from_cli(request):
    """Fixture to get the --baseurl option value."""
    # Get the base URL provided by the user
    base_url = request.config.getoption("--baseurl")
    
    # Remove trailing slash if present
    if base_url.endswith('/'):
        base_url = base_url.rstrip('/') # rstrip removes trailing characters
    
    return base_url

@pytest.fixture(scope="class")
def oneTimeSetUp(request, browser, base_url_from_cli): # Now these are correctly passed as arguments
    log.info(f"Running one time setUp for browser: {browser}")
    driver_options = None
    temp_user_data_dir = None
    driver = None 
    try:
        if browser == "chrome" or browser == "chrome-headless":
            chrome_options = Options()
            driver_options = chrome_options
            driver_options.add_argument('--no-sandbox')
            driver_options.add_argument('--disable-dev-shm-usage')
            driver_options.add_argument('--window-size=1920,1080')

            if browser == "chrome-headless":
                driver_options.add_argument('--headless')
                driver_options.add_argument('--disable-gpu')
                log.info("Configuring Chrome for headless mode.")
            else:
                log.info("Configuring Chrome for visible mode (local).")
            log.info(f"Final Chrome Options: {driver_options.arguments}")

        elif browser == "firefox":
            log.info("Configuring Firefox browser.")
            pass 

        wdf = WebDriverFactory(browser)
        try:
            driver = wdf.getWebDriverInstance(driver_options=driver_options)
            log.info("WebDriver instance obtained successfully.")
        except Exception as e:
            log.error(f"Failed to get WebDriver instance: {e}")
            pytest.skip(f"Could not initialize WebDriver for browser '{browser}': {e}. Please check driver compatibility and installation.")

        driver.implicitly_wait(10) # Good practice for initial element loading
        driver.get(base_url_from_cli)
        log.info(f"Navigated to Base URL: {base_url_from_cli}")

        if request.cls:
            request.cls.driver = driver
            request.cls.base_url = base_url_from_cli
        
        yield driver

    finally:
        log.info("Running one time tearDown (from finally block).")
        # Check if driver was successfully initialized before quitting
        if driver:
            try:
                driver.quit()
                log.info("WebDriver quit.")
            except Exception as e:
                log.error(f"Error quitting WebDriver: {e}")

        # Clean up the temporary user data directory
        '''
        if temp_user_data_dir and os.path.exists(temp_user_data_dir):
            try:
                shutil.rmtree(temp_user_data_dir)
                log.info(f"Successfully cleaned up: {temp_user_data_dir}")
            except OSError as e:
                log.error(f"Error cleaning up temporary directory {temp_user_data_dir}: {e}")
        '''
@pytest.fixture(scope="function")
def setUp():
    log.info("Running method level setUp")
    yield
    log.info("Running method level tearDown")