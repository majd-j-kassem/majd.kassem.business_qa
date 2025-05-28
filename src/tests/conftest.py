import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
import os
import shutil
import tempfile
import logging

# Assuming WebDriverFactory is in src/base/web_driver_factory.py
from src.base.web_driver_factory import WebDriverFactory

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

# Define a plugin class
class MySeleniumPlugin:
    # pytest_addoption hook
    def pytest_addoption(self, parser):
        parser.addoption("--browser", action="store", default="chrome", help="Type of browser: chrome or firefox")
        parser.addoption("--base-url", action="store", default="https://www.letskodeit.com", help="Base URL for testing")

    # Fixture to get browser from CLI
    @pytest.fixture(scope="session")
    def browser(self, request):
        return request.config.getoption("--browser")

    # Fixture to get base_url from CLI
    @pytest.fixture(scope="session")
    def base_url_from_cli(self, request):
        return request.config.getoption("--base-url")

    # Your oneTimeSetUp fixture (ensure 'self' is the first argument if it's a method)
    @pytest.fixture(scope="class")
    def oneTimeSetUp(self, request, browser, base_url_from_cli): # 'self' added here
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
            driver = wdf.getWebDriverInstance(driver_options=driver_options)

            driver.implicitly_wait(10)
            driver.get(base_url_from_cli)

            if request.cls:
                request.cls.driver = driver
                request.cls.base_url = base_url_from_cli

            yield driver

        finally:
            log.info("Running one time tearDown (from finally block).")
            if 'driver' in locals() and driver:
                driver.quit()
                log.info("WebDriver quit.")

            if temp_user_data_dir and os.path.exists(temp_user_data_dir):
                try:
                    shutil.rmtree(temp_user_data_dir)
                    log.info(f"Successfully cleaned up: {temp_user_data_dir}")
                except OSError as e:
                    log.error(f"Error cleaning up temporary directory {temp_user_data_dir}: {e}")

    # Your setUp fixture
    @pytest.fixture(scope="function")
    def setUp(self): # 'self' added here
        log.info("Running method level setUp")
        yield
        log.info("Running method level tearDown")