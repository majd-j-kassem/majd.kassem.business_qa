from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions # Keep if you plan to support Firefox
from selenium.webdriver.chrome.service import Service as ChromeService
# Import webdriver_manager for automatic driver management
from webdriver_manager.chrome import ChromeDriverManager
# If you support Firefox
# from webdriver_manager.firefox import GeckoDriverManager

import logging

log = logging.getLogger(__name__)

class WebDriverFactory:

    def __init__(self, browser):
        self.browser = browser.lower() # Normalize to lowercase for consistency

    def getWebDriverInstance(self, driver_options=None):
        driver = None

        if self.browser in ["chrome", "chrome-headless"]:
            # If no options are provided from conftest, create a default set
            if driver_options is None:
                chrome_options = ChromeOptions()
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--window-size=1920,1080')
                # Add headless if it's explicitly chrome-headless
                if self.browser == "chrome-headless":
                    chrome_options.add_argument('--headless')
                    chrome_options.add_argument('--disable-gpu') # Recommended for headless
                driver_options = chrome_options
                log.info("WebDriverFactory: No Chrome options provided, using default set.")
            else:
                log.info("WebDriverFactory: Using Chrome options provided from conftest.")

            # --- CRITICAL IMPROVEMENT: Use ChromeDriverManager ---
            # This automatically downloads and manages the correct chromedriver executable.
            try:
                service = ChromeService(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=driver_options)
                log.info("WebDriverFactory: ChromeDriver initialized using ChromeDriverManager.")
            except Exception as e:
                log.error(f"WebDriverFactory: Failed to initialize ChromeDriver with webdriver_manager: {e}")
                # You might want to re-raise or handle this more gracefully,
                # but conftest.py already has a skip for this.
                raise # Re-raise to let conftest handle the skip

        elif self.browser == "firefox":
            # If no options are provided from conftest, create a default set
            if driver_options is None:
                firefox_options = FirefoxOptions()
                # Add any default Firefox options here if needed
                driver_options = firefox_options
                log.info("WebDriverFactory: No Firefox options provided, using default set.")
            else:
                log.info("WebDriverFactory: Using Firefox options provided from conftest.")

            # --- For Firefox, you'd use GeckoDriverManager ---
            try:
                # service = FirefoxService(GeckoDriverManager().install()) # Uncomment if supporting Firefox
                # driver = webdriver.Firefox(service=service, options=driver_options) # Uncomment if supporting Firefox
                # Placeholder if you haven't implemented Firefox fully:
                log.warning("WebDriverFactory: Firefox browser selected, but driver initialization not fully implemented yet.")
                raise NotImplementedError("Firefox WebDriver initialization is not fully implemented.")
            except Exception as e:
                log.error(f"WebDriverFactory: Failed to initialize FirefoxDriver with webdriver_manager: {e}")
                raise # Re-raise to let conftest handle the skip

        else:
            log.error(f"WebDriverFactory: Unsupported browser type specified: {self.browser}")
            raise ValueError(f"Unsupported browser type: {self.browser}. Please choose 'chrome', 'chrome-headless', or 'firefox'.")

        # Common configurations for all browsers (if driver was successfully initialized)
        if driver:
            driver.set_page_load_timeout(30)
            driver.maximize_window() # Note: Maximize might not work in headless
            log.info(f"WebDriverFactory: Driver initialized with page load timeout (30s) and maximized window.")

        return driver