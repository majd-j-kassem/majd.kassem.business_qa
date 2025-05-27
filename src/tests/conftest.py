import pytest
from selenium import webdriver
from base.web_driver_factory import WebDriverFactory
from selenium.webdriver.chrome.options import Options
import os
import shutil # <--- Add this import!


@pytest.fixture()
def setUp():
    print("Running method level setUp")
    yield
    print("Running method level tearDown")


@pytest.fixture(scope="class")
def oneTimeSetUp(request, browser, base_url_from_cli):
    print(f"Running one time setUp for browser: {browser}")
    driver_options = None # Initialize to None
    is_headless = False # Flag to track if we're in headless mode
    temp_user_data_dir = None # <--- Initialize outside the try block
    try:

        if browser == "chrome":
            chrome_options = Options()
            driver_options = chrome_options  # <--- Assign chrome_options to driver_options HERE
            driver_options.add_argument('--no-sandbox')
            driver_options.add_argument('--disable-dev-shm-usage')
            driver_options.add_argument('--window-size=1920,1080') # Standard size for visible
            temp_user_data_dir = os.path.join('/tmp', f'chrome_user_data_{os.getpid()}')
            driver_options.add_argument(f"--user-data-dir={temp_user_data_dir}")
            print("Configuring Chrome for visible mode (local).")

        elif browser == "chrome-headless":
            chrome_options = Options()
            driver_options = chrome_options  # <--- Assign chrome_options to driver_options HERE
            driver_options.add_argument('--headless')
            driver_options.add_argument('--no-sandbox')
            driver_options.add_argument('--disable-dev-shm-usage')
            driver_options.add_argument('--window-size=1920,1080') # Larger size for headless
            # --- ADD THESE TWO LINES ---
            # Forces Chrome to use a unique, temporary user data directory for each run.
            # os.getpid() makes it unique per process, good for parallel execution (though not happening here).
            temp_user_data_dir = os.path.join('/tmp', f'chrome_user_data_{os.getpid()}')
            driver_options.add_argument(f"--user-data-dir={temp_user_data_dir}")
            # Add remote debugging port - useful for debugging headless Chrome if needed
            #driver_options.add_argument("--remote-debugging-port=9222")
            # --- END ADDITIONS ---
            print("Configuring Chrome for headless mode.")
            is_headless = True

        elif browser == "firefox":
            # Add Firefox specific options here if needed
            # For now, it will proceed with driver_options as None if not set here
            pass

        # Ensure WebDriverFactory handles the case where driver_options might still be None for 'firefox'
        # if no options were set for it.
        wdf = WebDriverFactory(browser)
        driver = wdf.getWebDriverInstance(driver_options=driver_options) # Pass the configured options

        driver.get(base_url_from_cli)

        if not is_headless: # Maximize only if not headless
            driver.maximize_window()
            print("Maximizing browser window.")

        if request.cls is not None:
            request.cls.driver = driver
            request.cls.base_url = base_url_from_cli
        yield driver
    finally: # <--- START OF FINALLY BLOCK - This will ALWAYS execute
        print("Running one time tearDown (from finally block).")
        # Ensure the driver is quit, even if an error occurred before yield
        if 'driver' in locals() and driver is not None: # Check if driver variable exists and is not None
             driver.quit()
         # Crucially, clean up the temporary user data directory here
        if temp_user_data_dir and os.path.exists(temp_user_data_dir):
            try:
                print(f"Attempting to remove temporary user data directory: {temp_user_data_dir}")
                shutil.rmtree(temp_user_data_dir)
                print(f"Successfully removed {temp_user_data_dir}")
            except OSError as e:
                print(f"Error removing directory {temp_user_data_dir}: {e}")

    
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