from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService # ADD THIS LINE
# from selenium.webdriver.firefox.service import Service as FirefoxService # If you support Firefox, add this too

class WebDriverFactory:

    def __init__(self, browser):
        self.browser = browser

    def getWebDriverInstance(self, driver_options=None):
        # ... (your existing code) ...

        if self.browser == "chrome" or self.browser == "chrome-headless":
            # Ensure driver_options is not None, if not passed, initialize it
            if driver_options is None:
                driver_options = ChromeOptions()
                driver_options.add_argument('--no-sandbox')
                driver_options.add_argument('--disable-dev-shm-usage')
                driver_options.add_argument('--window-size=1920,1080')
                # If you want to use the temp_user_data_dir here, you'd need to pass it or generate it here.
                # For now, let's assume conftest handles it.

            # Instantiate the ChromeService with the explicit path
            # Common paths in selenium/standalone-chrome:
            # /usr/bin/chromedriver or /usr/local/bin/chromedriver
            # Let's try /usr/bin/chromedriver first as it's often the default.
            #chrome_service = ChromeService(executable_path='/usr/bin/chromedriver') # CRITICAL CHANGE

            # Pass both the options and the service object
            driver = webdriver.Chrome( options=driver_options) # CRITICAL CHANGE
        elif self.browser == "firefox":
            # ... (your existing Firefox logic, potentially adding FirefoxService too)
            # driver = webdriver.Firefox(options=driver_options) # or similar
            pass # Keep your Firefox logic if you have it

        else:
            driver = webdriver.Chrome(options=driver_options) # Fallback, though ideally handled

        driver.set_page_load_timeout(30)
        driver.maximize_window()
        return driver