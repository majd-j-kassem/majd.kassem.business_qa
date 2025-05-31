import pytest
import time
import logging

from pages.admin.admin_login_page import AdminLoginPage
from pages.admin.admin_dashboard_page import AdminDashboardPage
from base.selenium_driver import SeleniumDriver

# Get the logger for this module
log = logging.getLogger(__name__)

@pytest.mark.usefixtures("oneTimeSetUp") # Ensures oneTimeSetUp is run for the class
class TestAdminDashboardFeatures:

    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "admin"
    PENDING_TEACHER_EMAIL = "azeez@admin.com" # Ensure this email exists and is in a 'pending' state for the test

    # classSetup will now return a tuple of initialized page objects
    @pytest.fixture(scope="class", autouse=True)
    def classSetup(self, oneTimeSetUp, base_url_from_cli):
        # oneTimeSetUp yields the driver, so we assign it directly
        self.driver = oneTimeSetUp # Still keep driver and base_url on self for general access
        self.base_url = base_url_from_cli

        log.info("TestAdminDashboardFeatures: classSetup completed (WebDriver and Page Objects initialized).")
        
        # Initialize page objects here
        admin_login_page = AdminLoginPage(self.driver, self.base_url)
        admin_dashboard_page = AdminDashboardPage(self.driver, self.base_url)
        selenium_driver = SeleniumDriver(self.driver, self.base_url)

        # Yield the initialized page objects (and selenium_driver)
        yield admin_login_page, admin_dashboard_page, selenium_driver

        log.info("Running class level tearDown (from classSetup fixture).")
        # No specific tear-down here, as the driver is quit by oneTimeSetUp's finally block
        # and logout is handled by methodSetUp's tearDown.

    # This fixture now receives the page objects from classSetup
    @pytest.fixture(autouse=True)
    def methodSetUp(self, classSetup): # Inject classSetup here to get its yielded values
        # Unpack the yielded page objects into instance attributes
        self.admin_login_page, self.admin_dashboard_page, self.selenium_driver = classSetup

        log.info("Running method level setUp: Logging in as admin.")

        # Perform admin login here using the now-assigned page object
        login_success = self.admin_login_page.admin_login(self.ADMIN_USERNAME, self.ADMIN_PASSWORD)
        assert login_success, f"Admin login failed in setUp for user: {self.ADMIN_USERNAME}"
        assert self.admin_login_page.is_logged_in_as_admin(), \
               f"Admin login failed in setUp for user: {self.ADMIN_USERNAME} (Dashboard not visible)."
        log.info(f"Admin {self.ADMIN_USERNAME} logged in successfully in setUp.")

        yield # Yield control to the actual test method

        log.info("Running method level tearDown: Logging out admin.")
        try:
            self.admin_login_page.logout()
        except Exception as e:
            log.error(f"Error during admin logout in tearDown: {e}")
            self.selenium_driver.take_screenshot_on_failure("teardown_logout_error", "page")
            pytest.fail(f"Logout failed during tearDown: {e}")

    def test_admin_approves_pending_teacher(self):
        """
        Tests the functionality of an admin approving a pending teacher's account.
        Pre-condition: A teacher with PENDING_TEACHER_EMAIL must exist in a 'pending' or 'inactive' state.
        """
        log.info("Starting test_admin_approves_pending_teacher.")

        # 1. Navigate to User/Teacher Management section
        assert self.admin_dashboard_page.navigate_to_user_management(), \
            "Failed to navigate to User/Teacher Management section."
        log.info("Successfully navigated to User/Teacher Management section.")

        # 2. Verify the initial status of the pending teacher
        log.info(f"Verifying {self.PENDING_TEACHER_EMAIL} is listed with an initial status (e.g., 'pending' or 'inactive').")
        # It's good practice to ensure the user is NOT already active before attempting to approve.
        initial_status = self.admin_dashboard_page.get_user_status_from_list(self.PENDING_TEACHER_EMAIL)
        log.info(f"Initial status for {self.PENDING_TEACHER_EMAIL}: {initial_status}")
        assert initial_status != "Active", \
            f"Pre-condition failed: {self.PENDING_TEACHER_EMAIL} is already 'Active'. Test requires a pending user."
        
        # 3. Perform the approval action
        log.info(f"Attempting to approve teacher: {self.PENDING_TEACHER_EMAIL} by changing status to 'Active'.")
        # This is where you need to call a method from your AdminDashboardPage
        # that interacts with the UI to change the teacher's status.
        # Replace 'change_user_status' with the actual method name in your page object.
        # This method should encapsulate finding the row for the teacher, locating the status dropdown/button,
        # and performing the action to set it to 'Active'.
        approval_success = self.admin_dashboard_page.change_user_status(self.PENDING_TEACHER_EMAIL, "Active")
        assert approval_success, f"Failed to approve teacher {self.PENDING_TEACHER_EMAIL}."
        log.info(f"Approval action initiated for {self.PENDING_TEACHER_EMAIL}.")

        # Add a small explicit wait to allow the UI to update after the action.
        # This is often necessary in web automation for dynamic content.
        time.sleep(3) # Adjust this wait time based on your application's responsiveness

        # 4. Verify the updated status of the teacher
        log.info(f"Verifying {self.PENDING_TEACHER_EMAIL} status changed to 'Active' in the list view.")
        updated_status = self.admin_dashboard_page.get_user_status_from_list(self.PENDING_TEACHER_EMAIL)
        log.info(f"Updated status for {self.PENDING_TEACHER_EMAIL}: {updated_status}")

        # Assert that the status has indeed changed to 'Active'
        assert updated_status == "Active", \
            f"Expected status 'Active' for {self.PENDING_TEACHER_EMAIL}, but found '{updated_status}' after approval."
        
        log.info(f"Test test_admin_approves_pending_teacher for {self.PENDING_TEACHER_EMAIL} PASSED. Teacher status is now 'Active'.")

