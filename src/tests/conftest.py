import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService # Import Service here too if you need it for local runs
import os
import shutil
import tempfile # Make sure tempfile is imported
import logging # Optional, for better logging
from  base.web_driver_factory import WebDriverFactory # Your factory

# Configure logging (optional, but good for debugging)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default="chrome", help="Type of browser: chrome or firefox")
    parser.addoption("--baseurl", action="store", default="https://majd-kassem-business-dev.onrender.com/", help="Base URL for testing")

@pytest.fixture(scope="class")
def oneTimeSetUp(request, browser, base_url_from_cli):
    log.info(f"Running one time setUp for browser: {browser}")
    driver_options = None
    temp_user_data_dir = None

    try:
        if browser == "chrome" or browser == "chrome-headless":
            chrome_options = Options()
            driver_options = chrome_options
            driver_options.add_argument('--no-sandbox')
            driver_options.add_argument('--disable-dev-shm-usage')
            driver_options.add_argument('--window-size=1920,1080')

            # Ensure a unique temporary user data directory is created
            temp_user_data_dir = tempfile.mkdtemp(prefix='chrome_user_data_')
            driver_options.add_argument(f"--user-data-dir={temp_user_data_dir}")
            log.info(f"Using temporary user data directory: {temp_user_data_dir}")

            if browser == "chrome-headless":
                driver_options.add_argument('--headless')
                driver_options.add_argument('--disable-gpu')
                log.info("Configuring Chrome for headless mode.")
            else:
                log.info("Configuring Chrome for visible mode (local).")

            log.info(f"Final Chrome Options: {driver_options.arguments}")

        elif browser == "firefox":
            # Add Firefox specific options here if needed
            pass

        wdf = WebDriverFactory(browser)
        # Pass driver_options to the factory method
        driver = wdf.getWebDriverInstance(driver_options=driver_options) # This line remains the same

        driver.implicitly_wait(10) # Good practice for initial element loading
        driver.get(base_url_from_cli)

        if request.cls:
            request.cls.driver = driver
            request.cls.base_url = base_url_from_cli

        yield driver

    finally:
        log.info("Running one time tearDown (from finally block).")
        if 'driver' in locals() and driver: # Check if driver was successfully initialized
            driver.quit()
            log.info("WebDriver quit.")

        # Clean up the temporary user data directory
        if temp_user_data_dir and os.path.exists(temp_user_data_dir):
            try:
                shutil.rmtree(temp_user_data_dir)
                log.info(f"Successfully cleaned up: {temp_user_data_dir}")
            except OSError as e:
                log.error(f"Error cleaning up temporary directory {temp_user_data_dir}: {e}")

@pytest.fixture(scope="function")
def setUp():
    log.info("Running method level setUp")
    yield
    log.info("Running method level tearDown")
    
# --- ADD THESE TWO NEW FIXTURES ---
@pytest.fixture(scope="session")
def browser(request):
    """Fixture to get the --browser option value."""
    return request.config.getoption("--browser")

@pytest.fixture(scope="session")
def base_url_from_cli(request):
    """Fixture to get the --base-url option value."""
    return request.config.getoption("--baseurl")
# --- END NEW FIXTURES ---