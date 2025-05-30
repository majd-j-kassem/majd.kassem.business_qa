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

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default="chrome", help="Type of browser: chrome or firefox")
    parser.addoption("--baseurl", action="store", default="http://127.0.0.1:8000/", help="Base URL for testing")

# Move browser and base_url fixtures to the top and ensure they are session scoped
@pytest.fixture(scope="session")
def browser(request):
    """Fixture to get the --browser option value."""
    return request.config.getoption("--browser")

@pytest.fixture(scope="session")
def base_url_from_cli(request):
    """Fixture to get the --base-url option value."""
    return request.config.getoption("--baseurl")

# --- NEW FIXTURE FOR CREATING PENDING TEACHER VIA API/DB ---
# This fixture has function scope because we want a new pending teacher for each test that uses it.
@pytest.fixture(scope="function")
def create_pending_teacher_api():
    """
    Fixture to create a new teacher with a 'pending' status via API (or direct DB insert).
    This avoids UI interaction for setting up test data, making the test faster and more focused.
    Yields the email of the created pending teacher.
    """
    teacher_email = f"pending_teacher_{int(time.time() * 1000)}@example.com"
    teacher_password = "TestPassword123!" # A strong, consistent password for this test user

    # --- CONFIGURATION FOR YOUR API (REPLACE THESE) ---
    API_BASE_URL = "http://127.0.0.1:8000/api" # <-- **UPDATE THIS to your actual API base URL**
    ADMIN_API_HEADERS = {
        "Content-Type": "application/json",
        "Authorization": "Token your_admin_api_token_here" # <-- **UPDATE THIS with your actual admin API token/auth**
                                                            # (e.g., 'Bearer <token>', 'Basic <credentials>', etc.)
    }
    # Example API endpoint for registering a user that defaults to pending
    # Or, an admin endpoint to create a user with a specific status
    REGISTER_API_ENDPOINT = f"{API_BASE_URL}/users/register/"
    # Example API endpoint for deleting a user (for teardown)
    DELETE_USER_API_ENDPOINT = f"{API_BASE_URL}/admin/users/delete_by_email/"


    log.info(f"\n[Fixture] Attempting to create pending teacher: {teacher_email} via API.")
    
    try:
        # --- YOUR APPLICATION-SPECIFIC API CALL TO CREATE PENDING USER ---
        # This is a generic example. You need to adapt it to your actual API.
        # It might be a registration endpoint where new users are pending by default,
        # or an admin endpoint to directly create a user with a specific status.
        payload = {
            "email": teacher_email,
            "password": teacher_password,
            "role": "teacher", # Assuming your system has roles, and this registers a teacher
            "is_active": False, # Often, pending users are not 'active'
            "status": "pending" # If your system has a direct status field on registration
        }
        
        # Example: Using requests to make an API call
        response = requests.post(REGISTER_API_ENDPOINT, json=payload, headers=ADMIN_API_HEADERS)
        response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
        
        # If your registration API returns user details, you might want to log/store them
        user_data = response.json()
        log.info(f"[Fixture] Successfully created user via API. Response: {user_data}")
        
        yield teacher_email # This is what the test function will receive

    except requests.exceptions.RequestException as e:
        log.error(f"[Fixture] Failed to create pending teacher via API: {e}")
        pytest.fail(f"Fixture failed to create pending teacher via API. Ensure API is running and configured: {e}")
    except Exception as e:
        log.error(f"[Fixture] An unexpected error occurred during pending teacher creation: {e}")
        pytest.fail(f"Fixture failed due to unexpected error: {e}")
    finally:
        # --- TEARDOWN: CLEAN UP THE CREATED TEACHER ---
        log.info(f"[Fixture] Cleaning up created teacher: {teacher_email}")
        try:
            # Example: API call to delete the user by email
            delete_payload = {"email": teacher_email}
            delete_response = requests.delete(DELETE_USER_API_ENDPOINT, json=delete_payload, headers=ADMIN_API_HEADERS)
            delete_response.raise_for_status()
            log.info(f"[Fixture] Successfully cleaned up teacher: {teacher_email}")
        except requests.exceptions.RequestException as e:
            log.error(f"[Fixture] Failed to delete teacher {teacher_email} via API during cleanup: {e}")
            # Do not fail the test here, but log the cleanup issue.
        except Exception as e:
            log.error(f"[Fixture] Unexpected error during teacher cleanup for {teacher_email}: {e}")

# --- EXISTING FIXTURES CONTINUE BELOW ---

@pytest.fixture(scope="class")
def oneTimeSetUp(request, browser, base_url_from_cli): # Now these are correctly passed as arguments
    log.info(f"Running one time setUp for browser: {browser}")
    driver_options = None
    temp_user_data_dir = None
    driver = None # Initialize driver to None

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
            log.info("Configuring Firefox browser.")
            # Example:
            # firefox_options = webdriver.FirefoxOptions()
            # driver_options = firefox_options
            pass # Keep pass if no specific options are needed

        # --- CRITICAL CHANGE HERE ---
        wdf = WebDriverFactory(browser)
        try:
            # Pass driver_options to the factory method
            driver = wdf.getWebDriverInstance(driver_options=driver_options)
            log.info("WebDriver instance obtained successfully.")
        except Exception as e:
            # Catch common WebDriver-related exceptions and skip tests explicitly
            log.error(f"Failed to get WebDriver instance: {e}")
            pytest.skip(f"Could not initialize WebDriver for browser '{browser}': {e}. Please check driver compatibility and installation.")
            return # This ensures the rest of the fixture doesn't run if skipped

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