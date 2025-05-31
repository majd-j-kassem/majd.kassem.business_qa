# No logging import
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from base.selenium_driver import SeleniumDriver
import time
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, StaleElementReferenceException

class AdminLoginPage(SeleniumDriver):

    def __init__(self, driver, base_url):
        super().__init__(driver, base_url) # Pass base_url to the parent class
        # IMPORTANT: Explicitly assign base_url to self here as well
        # This acts as a safeguard to ensure it's available in this specific class's instance
        self.base_url = base_url # <--- ADD THIS LINE HERE

        # Locators
        # Now self.base_url should definitely be available
        self._admin_login_url = f"{self.base_url}admin/"
        self._username_input = "//input[@placeholder='Username']"
        self._password_input = "//input[@placeholder='Password']"
        self._login_button = "//button[normalize-space()='Log in' or @type='submit']"
        self._dashboard_header = "//h1[@class='h4 m-0 pr-3 mr-3 border-right']"
        self._error_message = "//p[contains(text(),'Please enter the correct username and password for')]"

        # Locators for logout
        self._profile_dropdown_trigger = "//i[@class='far fa-user']"
        self._logout_button_locator = "//button[@type='submit' and normalize-space()='Log out']" 

    def navigate_to_admin_login_page(self):
        print(f"Navigating to Admin Login Page: {self._admin_login_url}")
        self.driver.get(self._admin_login_url)
        self.wait_for_page_load()

    def enter_username(self, username):
        self.send_keys_element(username, self._username_input, locatorType="xpath")
        print(f"Entered username: {username}")

    def enter_password(self, password):
        self.send_keys_element(password, self._password_input, locatorType="xpath")
        print("Entered password.")

    def click_login_button(self):
        self.click_element(self._login_button, locatorType="xpath")
        print("Clicked login button.")

    def admin_login(self, username, password):
        self.navigate_to_admin_login_page()
        self.enter_username(username)
        self.enter_password(password)
        self.click_login_button()
        
        if self.is_element_visible(self._error_message, locatorType="xpath", timeout=2):
            print("Login failed: Error message visible.")
            return False
        elif self.is_element_visible(self._dashboard_header, locatorType="xpath", timeout=10):
            print("Admin login successful.")
            return True
        else:
            print("Login failed: Neither dashboard nor error message detected. Unknown state.")
            self.take_screenshot_on_failure("admin_login_unknown_state", "page")
            return False

    def is_logged_in_as_admin(self):
        is_visible = self.is_element_visible(self._dashboard_header, locatorType="xpath")
        if is_visible:
            print("Admin dashboard element visible after login.")
        else:
            print("Admin dashboard element NOT visible after login.")
        return is_visible

    def get_login_error_message(self):
        error_element = self.get_element(self._error_message, locatorType="xpath", timeout=2)
        if error_element:
            return error_element.text.strip()
        return None

    def logout(self):
        print("Attempting to log out from admin dashboard.")
        try:
            profile_dropdown_clicked = self.click_element(self._profile_dropdown_trigger, locatorType="xpath", timeout=10)

            if profile_dropdown_clicked:
                print("Clicked profile dropdown trigger.")
                time.sleep(0.5)

                if not self.click_element(self._logout_button_locator, locatorType="xpath", timeout=10):
                    print(f"Failed to click logout button: '{self._logout_button_locator}'")
                    raise ElementClickInterceptedException(f"Logout button not clickable after multiple attempts: {self._logout_button_locator}")

                print("Successfully clicked logout button.")
                
                if not self.is_element_visible(self._username_input, locatorType="xpath", timeout=10):
                     print("Logout failed: Did not redirect to login page or username input not visible after logout.")
                     self.take_screenshot_on_failure("logout_redirection_failure", "page")
                     raise TimeoutException("Logout failed: Did not land on login page as expected.")

                print("Confirmed logout by verifying login page elements.")
            else:
                print("Profile dropdown trigger not found or not clickable for logout. Could not initiate logout flow.")
                raise TimeoutException("Profile dropdown trigger not available for logout.")

        except (ElementClickInterceptedException, TimeoutException, StaleElementReferenceException) as e:
            print(f"An expected error occurred during logout: {e}")
            self.take_screenshot_on_failure("logout_expected_failure", "page")
            raise
        except Exception as e:
            print(f"A critical unexpected error occurred during logout: {e}")
            self.take_screenshot_on_failure("logout_critical_failure", "page")
            raise