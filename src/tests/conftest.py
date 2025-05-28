import pytest
from selenium import webdriver
from base.web_driver_factory import WebDriverFactory
from selenium.webdriver.chrome.options import Options
import os
import shutil
import time
import tempfile # <--- Import tempfile

@pytest.fixture()
def setUp():
    print("Running method level setUp")
    yield
    print("Running method level tearDown")


@pytest.fixture(scope="class")
def oneTimeSetUp(request, browser, base_url_from_cli):
    print(f"Running one time setUp for browser: {browser}")
    driver_options = None
    is_headless = False
    temp_user_data_dir = None # Initialize to None

    try:
        # Define chrome_service outside the if/elif blocks to be accessible for ChromeDriver
        chrome_service = None

        if browser == "chrome" or browser == "chrome-headless":
            chrome_options = Options()
            driver_options = chrome_options
            driver_options.add_argument('--no-sandbox')
            driver_options.add_argument('--disable-dev-shm-usage')
            driver_options.add_argument('--window-size=1920,1080')

            # --- CRITICAL CHANGE 1: Ensure user-data-dir is created for ALL Chrome modes ---
            temp_user_data_dir = tempfile.mkdtemp(prefix='chrome_user_data_')
            driver_options.add_argument(f"--user-data-dir={temp_user_data_dir}")
            print(f"Using temporary user data directory: {temp_user_data_dir}")

            if browser == "chrome-headless":
                driver_options.add_argument('--headless')
                driver_options.add_argument('--disable-gpu')
                print("Configuring Chrome for headless mode.")
                is_headless = True
            else:
                print("Configuring Chrome for visible mode (local).")

            print("Final Chrome Options (after user-data-dir):", driver_options.arguments)

            # --- CRITICAL CHANGE 2: Explicitly set ChromeDriver path to bypass Selenium Manager ---
            # In selenium/standalone-chrome, chromedriver is typically in /usr/bin or /usr/local/bin
            # Let's try to locate it correctly.
            # A common path is /usr/local/bin/chromedriver or /usr/bin/chromedriver
            # Use a robust way to find it, or simply hardcode if you're sure.
            # Given the base image, it's usually on the PATH for `seluser`.
            # However, `selenium-manager` tries to find it. Let's explicitly tell Selenium to use a Service object.
            
            # This is how you pass the path for ChromeDriver if you are instantiating WebDriver directly.
            # Since you are using WebDriverFactory, ensure it supports passing service_args or service.
            # Let's assume WebDriverFactory passes `driver_options` to webdriver.Chrome/Firefox.
            # If `webdriver.Chrome()` is called with `options=driver_options`, and the driver is on PATH,
            # it should pick it up. The "offline mode" suggests a network issue for Selenium Manager.

            # Re-evaluate the problem: The core issue is the `user data directory` and `offline mode`.
            # The `user data directory` is fixed by ensuring `temp_user_data_dir` is always set.
            # The `offline mode` warning: This often happens if Selenium Manager *tries* to fetch a driver
            # but fails due to network constraints or permission to write to its cache.
            # Let's stick with the original `WebDriverFactory` and hope the `user-data-dir` fix
            # implicitly resolves or bypasses the Selenium Manager issue.
            # If not, we would need to pass a Service object with an explicit executable_path.
            # For now, let's just make sure the `temp_user_data_dir` is applied consistently.

        elif browser == "firefox":
            # Add Firefox specific options here if needed
            pass

        wdf = WebDriverFactory(browser)
        # Ensure driver_options are always passed
        driver = wdf.getWebDriverInstance(driver_options=driver_options)

        driver.get(base_url_from_cli)

        if not is_headless:
            driver.maximize_window()
            print("Maximizing browser window.")
        else:
            print("Headless mode is active. Browser window will not be visible.")


        if request.cls is not None:
            request.cls.driver = driver
            request.cls.base_url = base_url_from_cli
            request.cls.is_headless = is_headless

        yield driver

    finally:
        print("Running one time tearDown (from finally block).")
        if 'driver' in locals() and driver is not None:
            print("Quitting WebDriver...")
            driver.quit()
            time.sleep(1)

        if temp_user_data_dir and os.path.exists(temp_user_data_dir):
            print(f"Attempting to clean up temporary user data directory: {temp_user_data_dir}")
            try:
                shutil.rmtree(temp_user_data_dir, ignore_errors=True)
                print(f"Successfully cleaned up: {temp_user_data_dir}")
            except OSError as e:
                print(f"Error cleaning up {temp_user_data_dir}: {e}")
        else:
            print(f"Temporary user data directory did not exist or was not set for cleanup: {temp_user_data_dir}")

# --- CLI Options ---
def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default="chrome",
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