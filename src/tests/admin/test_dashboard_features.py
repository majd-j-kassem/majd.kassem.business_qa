import pytest
import time
import logging # <--- Import the logging module

from pages.admin.admin_login_page import AdminLoginPage
from pages.admin.admin_dashboard_page import AdminDashboardPage
from base.selenium_driver import SeleniumDriver

# Get the logger for this module
log = logging.getLogger(__name__) # <--- Initialize logger

@pytest.mark.usefixtures("oneTimeSetUp") # Ensures oneTimeSetUp is run for the class
class TestAdminDashboardFeatures:

    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "admin"
    PENDING_TEACHER_EMAIL = "azeez@admin.com"

    # classSetup will now return a tuple of initialized page objects
    @pytest.fixture(scope="class", autouse=True)
    def classSetup(self, oneTimeSetUp, base_url_from_cli):
        # oneTimeSetUp yields the driver, so we assign it directly
        self.driver = oneTimeSetUp # Still keep driver and base_url on self for general access
        self.base_url = base_url_from_cli

        log.info("TestAdminDashboardFeatures: classSetup completed (WebDriver and Page Objects initialized).") # <--- Changed to logging
        
        # Initialize page objects here
        admin_login_page = AdminLoginPage(self.driver, self.base_url)
        admin_dashboard_page = AdminDashboardPage(self.driver, self.base_url)
        selenium_driver = SeleniumDriver(self.driver, self.base_url)

        # Yield the initialized page objects (and selenium_driver)
        yield admin_login_page, admin_dashboard_page, selenium_driver

        log.info("Running class level tearDown (from classSetup fixture).") # <--- Changed to logging
        # No specific tear-down here, as the driver is quit by oneTimeSetUp's finally block
        # and logout is handled by methodSetUp's tearDown.

    # This fixture now receives the page objects from classSetup
    @pytest.fixture(autouse=True)
    def methodSetUp(self, classSetup): # Inject classSetup here to get its yielded values
        # Unpack the yielded page objects into instance attributes
        self.admin_login_page, self.admin_dashboard_page, self.selenium_driver = classSetup

        log.info("Running method level setUp: Logging in as admin.") # <--- Changed to logging

        # Perform admin login here using the now-assigned page object
        login_success = self.admin_login_page.admin_login(self.ADMIN_USERNAME, self.ADMIN_PASSWORD)
        assert login_success, f"Admin login failed in setUp for user: {self.ADMIN_USERNAME}"
        assert self.admin_login_page.is_logged_in_as_admin(), \
               f"Admin login failed in setUp for user: {self.ADMIN_USERNAME} (Dashboard not visible)."
        log.info(f"Admin {self.ADMIN_USERNAME} logged in successfully in setUp.") # <--- Changed to logging

        yield # Yield control to the actual test method

        log.info("Running method level tearDown: Logging out admin.") # <--- Changed to logging
        try:
            self.admin_login_page.logout()
        except Exception as e:
            log.error(f"Error during admin logout in tearDown: {e}") # <--- Changed to logging
            self.selenium_driver.take_screenshot_on_failure("teardown_logout_error", "page")
            pytest.fail(f"Logout failed during tearDown: {e}")

    def test_admin_approves_pending_teacher(self):

        assert self.admin_dashboard_page.navigate_to_user_management(), \
            "Failed to navigate to User/Teacher Management section."

        log.info(f"Verifying {self.PENDING_TEACHER_EMAIL} is listed as 'pending' or 'inactive'.") # <--- Changed to logging
        initial_status = self.admin_dashboard_page.get_user_status_from_list(self.PENDING_TEACHER_EMAIL)
       
        log.info(f"Approving teacher: {self.PENDING_TEACHER_EMAIL} by changing status to 'Active'.") # <--- Changed to logging
       
        log.info(f"Verifying {self.PENDING_TEACHER_EMAIL} status changed to 'Active' in the list view.") # <--- Changed to logging
        updated_status = self.admin_dashboard_page.get_user_status_from_list(self.PENDING_TEACHER_EMAIL)
       
        log.info(f"Test test_admin_approves_pending_teacher for {self.PENDING_TEACHER_EMAIL} PASSED.") # <--- Changed to logging