import pytest
from selenium import webdriver
from base.web_driver_factory import WebDriverFactory
from selenium.webdriver.chrome.options import Options

@pytest.yield_fixture()
def setUp():
    print("Running method level setUp")
    yield
    print("Running method level tearDown")


@pytest.yield_fixture(scope="class")
def oneTimeSetUp(request, browser, base_url_from_cli):
    print(f"Running one time setUp for browser: {browser}")
    driver_options = None
    
    if browser == "chrome":
        chrome_options = Options()
        print("Configuring Chrome for visible mode (local).")
        driver_options = chrome_options
        driver_options.add_argument('--no-sandbox')
        driver_options.add_argument('--disable-dev-shm-usage')
        driver_options.add_argument('--window-size=1920,1080') # Standard size for visible
        print("Configuring Chrome for visible mode (local).")
    elif browser == "chrome-headless": # Treat 'chrome-headless' as a distinct browser type
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        driver_options.add_argument('--window-size=2560,1440') # Or similar large resolution
        print("Configuring Chrome for headless mode.")
        is_headless = True # Set the flag
        driver_options = chrome_options
    elif browser == "firefox":
        # Add Firefox specific options if needed, e.g., for headless Firefox
        # firefox_options = webdriver.FirefoxOptions()
        # if "headless" in browser: # If you had "firefox-headless"
        #    firefox_options.add_argument("--headless")
        # driver_options = firefox_options
        pass # Currently no specific options for Firefox beyond default
    


    wdf = WebDriverFactory(browser)
    driver = wdf.getWebDriverInstance(driver_options=driver_options)
    driver.get(base_url_from_cli)
    
    if not is_headless:
        driver.maximize_window()
        print("Maximizing browser window.")
    # Only maximize window if it's not headless
    if "headless" not in browser: # Assuming you differentiate headless by browser name
        driver.maximize_window()
        print("Maximizing browser window.")
    if request.cls is not None:
        request.cls.driver = driver
        request.cls.base_url = base_url_from_cli # Make base_url available to test classes
    yield driver
    driver.quit()
    print("Running one time tearDown")

def pytest_addoption(parser):
    parser.addoption( "--browser", action="store", default="chrome", 
                     help="browser to execute tests (chrome or firefox)")
    parser.addoption("--osType", help="Type of operating system")
    
    parser.addoption("--base-url", action="store", default="http://127.0.0.1:8000/",
                     help="Base URL for the web application under test (e.g., http://127.0.0.1:8000/ or https://dev.render.com/)")

@pytest.fixture(scope="session")
def browser(request):
    return request.config.getoption("--browser")

@pytest.fixture(scope="session")
def osType(request):
    return request.config.getoption("--osType")

@pytest.fixture(scope="session")
def base_url_from_cli(request):
    return request.config.getoption("--base-url")