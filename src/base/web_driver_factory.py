"""
@package base

WebDriver Factory class implementation
It creates a webdriver instance based on browser configurations

Example:
    wdf = WebDriverFactory(browser)
    wdf.getWebDriverInstance()
"""
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


class WebDriverFactory():

    def __init__(self, browser):
        """
        Inits WebDriverFactory class

        Returns:
            None
        """
        self.browser = browser
    """
        Set chrome driver and iexplorer environment based on OS

        chromedriver = "C:/.../chromedriver.exe"
        os.environ["webdriver.chrome.driver"] = chromedriver
        self.driver = webdriver.Chrome(chromedriver)

        PREFERRED: Set the path on the machine where browser will be executed
    """

    def getWebDriverInstance(self, driver_options=None):
        """
       Get WebDriver Instance based on the browser configuration

        Returns:
            'WebDriver Instance'
        """
        if self.browser == "chrome" or self.browser == "chrome-headless": # Use "in" because browser can be "chrome" or "chrome-headless"
            # For newer Selenium (4.x+):
            # webdriver_manager will download and manage the ChromeDriver executable
            #service = Service(ChromeDriverManager().install())
            #driver = webdriver.Chrome(service=service, options=driver_options) # Pass options here!
            driver = webdriver.Chrome(options=driver_options) # Pass options here!
        elif "firefox" in self.browser:
            # For Firefox, you'd typically use GeckoDriverManager
            # service = Service(GeckoDriverManager().install())
            # driver = webdriver.Firefox(service=service, options=driver_options) # Pass options here!
            driver = webdriver.Firefox() # Fallback if no specific options
        else:
            # Default to Chrome if browser is not specified or recognized
            #service = Service(ChromeDriverManager().install())
            #driver = webdriver.Chrome(service=service, options=driver_options)
            driver = webdriver.Chrome(options=driver_options)

        return driver