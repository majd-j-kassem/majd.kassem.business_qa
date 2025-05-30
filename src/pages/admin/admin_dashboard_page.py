# src/pages/admin/admin_dashboard_page.py

from selenium.webdriver.common.by import By
from base.selenium_driver import SeleniumDriver
import utilities.custome_logger as cl
import logging
from selenium.webdriver.support import expected_conditions as EC # Make sure this is imported
# from selenium.webdriver.support.ui import Select # Only needed if you use Select dropdowns here

class AdminDashboardPage(SeleniumDriver):

    def __init__(self, driver):
        super().__init__(driver)
        # self.log is already initialized by super().__init__(driver)

    ################
    ### Locators ###
    ################
    # Example locators - YOU MUST UPDATE THESE BASED ON YOUR UI
    # !! CRITICAL: These locators are placeholders and need to be verified against your actual HTML.
    # !! The "_teachers_menu_link" using "//tbody/tr[7]/td[1]" is very brittle.
    # !! The "_pending_teachers_table" using "//form[@id='changelist-search']" is likely wrong (it's a form, not the table).
    _teachers_menu_link = "//a[contains(@href, 'your_teacher_management_url') or contains(., 'User Profiles') or contains(., 'Teachers')]" # <--- STRONGLY SUGGEST YOU FIND A BETTER LOCATOR
    _pending_teachers_table = "//table[@class='results_list']" # <--- This is a common pattern for tables, but VERIFY YOURS
    
    _teacher_row_by_email = "//table//td[contains(text(), '{email}')]/ancestor::tr"
    _approve_button_in_row = ".//button[text()='Approve']" # Relative XPath within a teacher row (if it's a button)
    # If it's an anchor tag: _approve_link_in_row = ".//a[text()='Approve']"
    
    _approval_success_message = "//div[@class='alert alert-success' or contains(@class, 'message success')]" # Example for a success message

    ############################
    ### Element Interactions ###
    ############################

    def go_to_teachers_section(self):
        """Navigates to the section listing teachers (e.g., pending approvals)."""
        self.log.info("Navigating to Teachers section.")
        # CORRECTED: Removed 'self' as first argument
        self.click_element(locator=self._teachers_menu_link, locatorType="xpath") 
        self.wait_for_page_load() # Wait for the new page to load
        # Or wait for a specific element on the teachers list page to confirm navigation
        # CORRECTED: Removed 'self' as first argument
        self.get_element(locator=self._pending_teachers_table, locatorType="xpath",
                         condition=EC.presence_of_element_located, timeout=10)
        self.log.info("Landed on Teachers section.")

    def approve_teacher(self, teacher_email):
        """
        Approves a specific teacher by their email.
        Assumes we are already on the teachers approval page OR this method navigates there.
        (Current implementation assumes it navigates via go_to_teachers_section).
        """
        self.log.info(f"Attempting to approve teacher: {teacher_email}")
        
        # Ensure we are on the correct page (optional, but good for robust flows)
        self.go_to_teachers_section() 

        # Construct XPath to the row containing the teacher's email
        row_locator_xpath = self._teacher_row_by_email.format(email=teacher_email)
        
        try:
            # Get the specific row element
            teacher_row = self.get_element(row_locator_xpath, locatorType="xpath",
                                           condition=EC.presence_of_element_located, timeout=10)
            
            if teacher_row:
                self.log.info(f"Found row for teacher: {teacher_email}. Locating Approve button...")
                # Find the Approve button *within* that row
                approve_button = self.get_element(self._approve_button_in_row, parentElement=teacher_row,
                                                  locatorType="xpath", condition=EC.element_to_be_clickable)
                
                if approve_button:
                    self.click_element(locator=self._approve_button_in_row, parentElement=teacher_row,
                                       locatorType="xpath") # Use parentElement for context
                    self.log.info(f"Clicked 'Approve' for teacher: {teacher_email}")
                    
                    # IMPORTANT: Add a wait here for the approval action to complete
                    # CORRECTED: _approval_success_message is a string, not a tuple
                    self.isElementVisible(self._approval_success_message, locatorType="xpath", timeout=5)
                    self.wait_for_element_to_be_invisible(self._approval_success_message, locatorType="xpath", timeout=10)
                    self.log.info(f"Confirmed approval success message for {teacher_email}.")
                    return True
                else:
                    self.log.error(f"Approve button not found or not clickable for teacher: {teacher_email}")
                    self.take_screenshot_on_failure(f"approve_{teacher_email}", "button", "approve_button_missing")
                    return False
            else:
                self.log.error(f"Teacher row not found for email: {teacher_email}. Is the teacher pending?")
                self.take_screenshot_on_failure(f"teacher_row_{teacher_email}", "row", "teacher_row_missing")
                return False
        except Exception as e:
            self.log.error(f"Error approving teacher {teacher_email}: {e}")
            self.take_screenshot_on_failure(f"approve_teacher_error_{teacher_email}", "general", "approve_error")
            raise # Re-raise to fail the test
    
    def is_teacher_present_in_pending_list(self, teacher_email):
        """Checks if a teacher is still present in the pending list."""
        self.go_to_teachers_section() # Ensure we're on the right page to check
        row_locator_xpath = self._teacher_row_by_email.format(email=teacher_email)
        return self.isElementPresent(row_locator_xpath, locatorType="xpath", timeout=5)

    def is_teacher_approved_successfully(self, teacher_email):
        """
        Verifies if a teacher was successfully approved.
        This might involve navigating to an 'Approved Teachers' list,
        or just confirming they are no longer in 'Pending'.
        For simplicity, we'll check absence from pending list for now.
        """
        self.log.info(f"Verifying if teacher {teacher_email} is approved (i.e., no longer in pending list).")
        # If the teacher is NOT present in the pending list, it implies approval
        return not self.is_teacher_present_in_pending_list(teacher_email)