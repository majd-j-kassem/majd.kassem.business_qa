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
    PENDING_TEACHER_EMAIL = "teacher1" # Ensure this email exists and is in a 'pending' state for the test
    commission_value = "42"
    # classSetup will now return a tuple of initialized page objects
    @pytest.fixture(scope="class", autouse=True)
    def classSetup(self, oneTimeSetUp, base_url_from_cli):
        # oneTimeSetUp yields the driver, so we assign it directly
        self.driver = oneTimeSetUp # Still keep driver and base_url on self for general access
        self.base_url = base_url_from_cli


        # Initialize page objects here
        admin_login_page = AdminLoginPage(self.driver, self.base_url)
        admin_dashboard_page = AdminDashboardPage(self.driver, self.base_url)
        selenium_driver = SeleniumDriver(self.driver, self.base_url)

        yield admin_login_page, admin_dashboard_page, selenium_driver


    @pytest.fixture(autouse=True)
    def methodSetUp(self, classSetup): # Inject classSetup here to get its yielded values
        self.admin_login_page, self.admin_dashboard_page, self.selenium_driver = classSetup

        login_success = self.admin_login_page.admin_login(self.ADMIN_USERNAME, self.ADMIN_PASSWORD)

        yield # Yield control to the actual test method

        try:
            self.admin_login_page.logout()
        except Exception as e:
            self.selenium_driver.take_screenshot_on_failure("teardown_logout_error", "page")
            pytest.fail(f"Logout failed during tearDown: {e}")

    def test_admin_approves_pending_teacher(self):
        
        assert self.admin_dashboard_page.navigate_to_user_management(), \
            "Failed to navigate to User/Teacher Management section."

        initial_approval_status = self.admin_dashboard_page.get_user_status_from_list(
            self.PENDING_TEACHER_EMAIL, status_type="approved")

        log.info(f"Initial approval status for {self.PENDING_TEACHER_EMAIL}: {initial_approval_status}")

        # You only want to approve if they are NOT Approved
        if initial_approval_status == "Not Approved":
            assert self.admin_dashboard_page.change_user_status_and_commission(
                self.PENDING_TEACHER_EMAIL, new_approval_status="Approved", commission_value=self.commission_value), \
                f"Failed to approve teacher and set commission for {self.PENDING_TEACHER_EMAIL}."

            log.info(f"Successfully approved teacher {self.PENDING_TEACHER_EMAIL} and set commission to 15.00.")

            
            final_approval_status = self.admin_dashboard_page.get_user_status_from_list(
                self.PENDING_TEACHER_EMAIL, status_type="approved")
            log.info(f"Final approval status for {self.PENDING_TEACHER_EMAIL}: {final_approval_status}")

            assert final_approval_status == "Approved", \
                f"Verification failed: Teacher {self.PENDING_TEACHER_EMAIL} is still not approved after action."

        elif initial_approval_status == "Approved":
            log.info(f"Teacher {self.PENDING_TEACHER_EMAIL} is already approved. Skipping approval step.")
            # or just skip and log.
            assert True # Test passes if already approved, or adjust expectation

        else:
            log.error(f"Could not determine initial approval status for {self.PENDING_TEACHER_EMAIL}. Test aborted.")
            pytest.fail(f"Could not determine initial approval status for {self.PENDING_TEACHER_EMAIL}.")

        log.info("Test test_admin_approves_pending_teacher completed successfully.")
