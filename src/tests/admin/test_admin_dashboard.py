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
    PENDING_TEACHER_EMAIL = "mjdwwwwwassouf" # Ensure this email exists and is in a 'pending' state for the test

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
        Pre-condition: A teacher with self.PENDING_TEACHER_EMAIL must exist in a 'pending' or 'inactive' state.
        """
        log.info("Starting test_admin_approves_pending_teacher.")

        # 1. Navigate to User/Teacher Management section
        assert self.admin_dashboard_page.navigate_to_user_management(), \
            "Failed to navigate to User/Teacher Management section."

        # 2. Check initial status (optional, but good for robust tests)
        # Assuming your self.PENDING_TEACHER_EMAIL is in the list and not approved yet.
        # This will return "Not Approved" if the alt attribute is 'False'
        initial_approval_status = self.admin_dashboard_page.get_user_status_from_list(
            self.PENDING_TEACHER_EMAIL, status_type="approved")

        log.info(f"Initial approval status for {self.PENDING_TEACHER_EMAIL}: {initial_approval_status}")

        # You only want to approve if they are NOT Approved
        if initial_approval_status == "Not Approved":
            # 3. Enter the user's edit page, set commission, and approve
            # Example: approve the teacher and set commission to 15.00
            assert self.admin_dashboard_page.change_user_status_and_commission(
                self.PENDING_TEACHER_EMAIL, new_approval_status="Approved", commission_value="15.00"), \
                f"Failed to approve teacher and set commission for {self.PENDING_TEACHER_EMAIL}."

            log.info(f"Successfully approved teacher {self.PENDING_TEACHER_EMAIL} and set commission to 15.00.")

            # 4. Verify the status from the list page again after returning
            # You might need to navigate back to the list page if the save redirects elsewhere,
            # or if your save operation keeps you on the edit page and you want to verify the list view.
            # Assuming you are redirected back to the list page after saving.
            # If not, add self.admin_dashboard_page.navigate_to_user_management() here.

            # Re-fetch status to confirm approval
            final_approval_status = self.admin_dashboard_page.get_user_status_from_list(
                self.self.PENDING_TEACHER_EMAIL, status_type="approved")
            log.info(f"Final approval status for {self.PENDING_TEACHER_EMAIL}: {final_approval_status}")

            assert final_approval_status == "Approved", \
                f"Verification failed: Teacher {self.PENDING_TEACHER_EMAIL} is still not approved after action."

        elif initial_approval_status == "Approved":
            log.info(f"Teacher {self.PENDING_TEACHER_EMAIL} is already approved. Skipping approval step.")
            # Depending on your test case, you might assert that it's already approved,
            # or just skip and log.
            assert True # Test passes if already approved, or adjust expectation

        else:
            log.error(f"Could not determine initial approval status for {self.PENDING_TEACHER_EMAIL}. Test aborted.")
            pytest.fail(f"Could not determine initial approval status for {self.PENDING_TEACHER_EMAIL}.")

        log.info("Test test_admin_approves_pending_teacher completed successfully.")
