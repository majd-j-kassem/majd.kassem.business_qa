from selenium.webdriver.common.by import By
from base.selenium_driver import SeleniumDriver
# Removed unused imports: Select, WebDriverWait, expected_conditions as EC, various exceptions, time
# These are handled by SeleniumDriver, so no need to import them directly here.
import utilities.custome_logger as cl
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging

class AdminLoginPage(SeleniumDriver):
    ################
    ### Locators ###
    ################
    _admin_username_input = "//input[@placeholder='Username']"
    _admin_password_input = "//input[@placeholder='Password']" # This is an XPath
    
    # You have 'password_locator = "id_password"'. If this is an actual ID,
    # then your enter_password method will use it.
    # If the password input also uses the placeholder and has no ID, then just use _admin_password_input
    # I'll assume 'password_locator' is indeed an ID for now, as you changed its locatorType to "xpath" in enter_password.
    # Let's clarify: if 'password_locator' is an ID like "id_password", it should be locatorType="id"
    # If the password field is identified by "//input[@placeholder='Password']", then it should be locatorType="xpath"
    # I will stick to 'password_locator' being an ID for now as per previous conversation, but ensure it's correct.
    _password_input_id = "id_password" # Renamed for clarity if it's an ID

    login_button_locator = "//button[@class = 'login-button']"

    # Proper locator for logout if you ever implement it
    _logout_link = (By.LINK_TEXT, "Logout") # Example, needs proper By. locator

    _error_message_login_locator = "//li[@class='error approval-message']" # Consistent naming

    # THIS IS THE LOCATOR YOU NEED TO UPDATE after inspecting your admin dashboard HTML
    _admin_dashboard_header = "//h1[contains(text(), 'Admin Dashboard')]" # Example XPath for a dashboard header
    # OR _admin_dashboard_header = "dashboardHeaderId" # Example ID for a dashboard header

    ADMIN_LOGIN_PATH = "/admin/" # Specific path relative to base_url

    ############################
    ### Element Interactions ###
    ############################

    def __init__(self, driver, base_url):
        super().__init__(driver) # Correctly initializes self.driver and self.log from SeleniumDriver
        # self.driver = driver # REMOVE THIS LINE - it's redundant. self.driver is already set by super()
        self.base_url = base_url # Store base_url
        # self.log = cl.customLogger(logging.DEBUG) # Already initialized in SeleniumDriver's __init__


    def open(self):
        """Navigates directly to the admin login page."""
        full_admin_url = f"{self.base_url}{self.ADMIN_LOGIN_PATH}"
        self.log.info(f"Navigating to Admin Login Page: {full_admin_url}")
        self.driver.get(full_admin_url)
        self.wait_for_page_load() # Good, relies on SeleniumDriver


    def enter_username(self, username):
        # CORRECTED: locatorType should be "xpath" for "//input[@placeholder='Username']"
        self.send_keys_element(username, self._admin_username_input, locatorType="xpath")
        self.log.info(f"Entered username: {username}")


    def enter_password(self, password):
        # You had password_locator = "id_password" and locatorType="xpath".
        # If "id_password" is truly an ID, it should be locatorType="id".
        # If you are using "//input[@placeholder='Password']", it should be locatorType="xpath".
        # I'm going with the placeholder XPath for consistency with username, assuming 'id_password' was a typo or less reliable.
        self.send_keys_element(password, self._admin_password_input, locatorType="xpath")
        self.log.info(f"Entered password.")


    def click_login_button(self):
        self.click_element(self.login_button_locator, locatorType="xpath")
        self.log.info("Clicked login button.")

        try:
            # THIS IS THE LOCATOR THAT NEEDS TO BE UPDATED WITH YOUR ACTUAL DASHBOARD ELEMENT
            # Use the _admin_dashboard_header locator defined above, with its correct type.
            self.get_element(locator=self._admin_dashboard_header, locatorType="xpath", # Example for XPath
                             condition=EC.visibility_of_element_located, timeout=10)
            self.log.info("Admin dashboard element visible after login.")
            # self.wait_for_page_load() # Optional: if you expect a full page refresh here

        except TimeoutException:
            error_msg = self.get_login_error_message()
            if error_msg:
                self.log.error(f"Login failed: {error_msg}")
                raise Exception(f"Login failed: {error_msg}")
            else:
                self.log.critical("Login button clicked, but neither dashboard loaded nor error message found.")
                self.take_screenshot_on_failure("post_login_state", "browser", "unexpected_login_state")
                raise Exception("Unexpected state after login: Dashboard not loaded and no error message.")
        except Exception as e:
            self.log.error(f"An unexpected error occurred during post-login check: {e}")
            raise

    def admin_login(self, username, password):
        """Performs the full admin login sequence."""
        self.open()
        self.enter_username(username)
        self.enter_password(password)
        self.click_login_button()

    def get_login_error_message(self):
        """
        Gets the text of the login error message if it's visible.
        Returns empty string if no error message is found or element not visible.
        """
        return self.get_text_of_element(self._error_message_login_locator, locatorType="xpath", timeout=5)

    def is_logged_in_as_admin(self):
        """
        Checks if the admin is successfully logged in by verifying a unique element
        on the admin dashboard.
        """
        # Uses the _admin_dashboard_header locator defined above
        return self.isElementVisible(self._admin_dashboard_header, locatorType="xpath", timeout=5)