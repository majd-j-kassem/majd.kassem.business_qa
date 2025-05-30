# src/tests/admin/test_dashboard_features.py

import pytest
import unittest
# Import necessary page objects
from pages.admin.admin_login_page import AdminLoginPage
from pages.admin.admin_dashboard_page import AdminDashboardPage


@pytest.mark.usefixtures("oneTimeSetUp", "setUp")
class TestAdminDashboardFeatures(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def classSetup(self, oneTimeSetUp):
        """
        Sets up page objects for each test method within this class.
        'oneTimeSetUp' fixture provides the WebDriver instance.
        """
                                               # This should match the --baseurl option or default in conftest.py
        self.admin_login_page = AdminLoginPage(self.driver)
        self.admin_dashboard_page = AdminDashboardPage(self.driver)
        # self.log is available from the base class (SeleniumDriver -> BasePage)
        # which is usually inherited by test classes using pytest.mark.usefixtures setup.

    def test_admin_approves_pending_teacher(self, create_pending_teacher_api):
        """
        Tests that an admin can successfully approve a teacher whose status is pending.
        This test utilizes an API fixture ('create_pending_teacher_api') to set up 
        the precondition (a pending teacher exists) without UI interaction, 
        making the test faster and more focused on the dashboard's approval functionality.
        """
        self.log.info("--- Starting test_admin_approves_pending_teacher ---")
        
        # The 'create_pending_teacher_api' fixture will be executed before this test method.
        # It yields the email of the newly created pending teacher, which we capture here.
        teacher_email = create_pending_teacher_api 
        self.log.info(f"Test data setup: Pending teacher created via API with email: {teacher_email}")

        # 1. Admin Logs In to the Dashboard
        self.log.info("Step 1: Admin logging in to the application.")
        # !! IMPORTANT: Replace with your actual admin username and password for UI login
        admin_username = "your_admin_username" 
        admin_password = "your_admin_password" 
        self.admin_login_page.admin_login(admin_username, admin_password)
        self.assertTrue(self.admin_login_page.is_logged_in_as_admin(), 
                        "Admin login failed: Expected admin user not logged in successfully.")
        self.log.info("Admin logged in successfully.")

        # 2. Verify Teacher is Initially Present in the Pending List
        self.log.info(f"Step 2: Verifying teacher '{teacher_email}' is initially present in the pending list on the dashboard.")
        # The 'is_teacher_present_in_pending_list' method in AdminDashboardPage
        # includes navigation to the teachers section if not already there.
        is_initially_present = self.admin_dashboard_page.is_teacher_present_in_pending_list(teacher_email)
        self.assertTrue(is_initially_present,
                        f"Precondition failed: Teacher '{teacher_email}' not found in pending list before approval attempt.")
        self.log.info(f"Confirmed: Teacher '{teacher_email}' is present in the pending list as expected.")

        # 3. Approve the Teacher via Admin Dashboard UI
        self.log.info(f"Step 3: Attempting to approve teacher '{teacher_email}' via the Admin Dashboard UI.")
        # The 'approve_teacher' method in AdminDashboardPage also handles navigation to the teachers section.
        approval_action_successful = self.admin_dashboard_page.approve_teacher(teacher_email)
        self.assertTrue(approval_action_successful, 
                        f"Teacher approval action failed or did not complete as expected for: {teacher_email}.")
        self.log.info(f"Approval process completed for teacher: {teacher_email}")

        # 4. Verify Teacher Approval Status (no longer in pending list)
        self.log.info(f"Step 4: Verifying final approval status for teacher '{teacher_email}' (i.e., removed from pending list).")
        # 'is_teacher_approved_successfully' re-navigates and checks for absence from the pending list.
        is_approved = self.admin_dashboard_page.is_teacher_approved_successfully(teacher_email)
        self.assertTrue(is_approved, 
                        f"Verification failed: Teacher '{teacher_email}' is still present in pending list or approval status check failed.")
        self.log.info(f"Teacher '{teacher_email}' successfully approved and verified (no longer in pending list).")
        
        # Optional: Log out admin after the test is complete
        # self.admin_login_page.logout() 

        self.log.info("--- Test test_admin_approves_pending_teacher finished successfully ---")

    # You would add more tests here related to other dashboard features, e.g.:
    # def test_admin_can_search_teachers(self):
    #     self.log.info("Testing admin search functionality for teachers.")
    #     # Setup test data (e.g., via API fixture to create multiple teachers)
    #     # Admin login
    #     # Navigate to teachers section
    #     # Use admin_dashboard_page.search_teachers("search_query")
    #     # Assert results
    #     pass

    # def test_admin_can_navigate_to_reports(self):
    #     self.log.info("Testing admin navigation to reports section.")
    #     # Admin login
    #     # Use admin_dashboard_page.go_to_reports_section() (assuming you add this method)
    #     # Assert presence of an element on the reports page
    #     pass