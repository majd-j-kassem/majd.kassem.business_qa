import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from base.selenium_driver import SeleniumDriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException

class AdminDashboardPage(SeleniumDriver):

    def __init__(self, driver, base_url):
        super().__init__(driver, base_url)
        self.log = logging.getLogger(self.__class__.__name__)

        # Locators
        self._dashboard_header = "//h1[normalize-space()='Dashboard' or contains(text(), 'Welcome to the Admin Dashboard')]"
        self._user_profiles_link = "//a[./p[normalize-space()='User Profiles'] and contains(@href, '/admin/accounts/profile/')]"
        self._user_profiles_page_header = "//h1[normalize-space()='User Profiles']" # Or a similar header on the user profiles page
        # Locators for user list table
        # This lambda identifies the row containing the email.
        # It assumes the email is either a link (<a>) or direct text (<td>) within the row.
        self._user_row_by_email = lambda email: f"//tr[.//a[normalize-space()='{email}'] or .//td[normalize-space()='{email}']]"

        # Locators for 'Is teacher application pending' and 'Is teacher approved' columns using images
        # These assume fixed column positions (td[3] and td[4]) and img[@alt='True/False']
        self._is_teacher_pending_status_in_row = lambda email: \
            f"{self._user_row_by_email(email)}/td[3]//img[@alt='True' or @alt='False']" # Third column

        self._is_teacher_approved_status_in_row = lambda email: \
            f"{self._user_row_by_email(email)}/td[4]//img[@alt='True' or @alt='False']" # Fourth column

        # Locator for the clickable link to edit the user (the email itself often acts as the link)
        self._user_edit_link_by_email = lambda email: f"{self._user_row_by_email(email)}//a[normalize-space()='{email}']"

        # Locators for user edit page
        # Confirm these IDs or names on your actual edit page
        self._is_teacher_approved_checkbox = "//input[@id='id_is_teacher_approved']" # Assuming this is the checkbox on the edit page
        self._save_button = "//input[@type='submit' and @value='Save']"
        self._successful_change_message = "//li[contains(@class, 'success') and contains(text(), 'was changed successfully')]"


    def is_on_dashboard_page(self):
        """
        Verifies if the current page is the admin dashboard.
        """
        return self.is_element_visible(self._dashboard_header, locatorType="xpath")

    def navigate_to_user_management(self):
        """
        Navigates to the user management section.
        Based on image_f88b9a.png, the link is 'User Profiles'.
        """
        self.log.info("Attempting to navigate to User Profiles section.")
        
        if self.click_element(self._user_profiles_link, locatorType="xpath"):
            self.log.info("Clicked 'User Profiles' link.")
            self.wait_for_page_load() # Wait for the new page to load
            # Verify we are on the User Profiles list page (e.g., check for a header)
            if self.is_element_visible("//h1[normalize-space()='Select user profile to change']", locatorType="xpath", timeout=5):
                 self.log.info("Successfully navigated to User Profiles list page.")
                 return True
            else:
                 self.log.error("Navigated to 'User Profiles' but list page header not visible.")
                 self.take_screenshot_on_failure("user_profiles_list_page_load_fail", "page")
                 return False
        else:
            self.log.error("Could not find or click the 'User Profiles' link.")
            self.take_screenshot_on_failure("navigate_to_user_profiles_fail", "page")
            return False

    def get_user_status_from_list(self, email, status_type="approved"):
        """
        Retrieves the status of a user from a table/list based on icon presence.
        status_type can be 'pending' (for 'Is teacher application pending') or 'approved' (for 'Is teacher approved').
        Returns 'Approved' (True) or 'Not Approved' (False) based on alt attribute.
        """
        self.log.info(f"Getting '{status_type}' status for user: {email}")
        
        if status_type == "approved":
            status_element_locator = self._is_teacher_approved_status_in_row(email)
        elif status_type == "pending":
            status_element_locator = self._is_teacher_pending_status_in_row(email)
        else:
            self.log.error(f"Invalid status_type: {status_type}. Must be 'pending' or 'approved'.")
            return None

        try:
            status_icon = self.get_element(status_element_locator, locatorType="xpath")
            if status_icon:
                alt_text = status_icon.get_attribute("alt")
                if alt_text == "True":
                    self.log.info(f"Status for {email} is 'Approved' (alt='True').")
                    return "Approved"
                elif alt_text == "False":
                    self.log.info(f"Status for {email} is 'Not Approved' (alt='False').")
                    return "Not Approved"
                else:
                    self.log.warning(f"Unknown alt text for status icon for {email}: {alt_text}")
                    return None
            else:
                self.log.warning(f"Status icon element not found for {email} with locator: {status_element_locator}")
                return None
        except (NoSuchElementException, TimeoutException) as e:
            self.log.error(f"Error finding status icon for user {email} (status_type: {status_type}): {e}")
            self.take_screenshot_on_failure(f"user_status_icon_not_found_{email}_{status_type}", "page")
            return None
        except Exception as e:
            self.log.error(f"An unexpected error occurred while getting user status icon: {e}")
            return None

    def change_user_status_via_edit_page(self, email, new_status="Approved"): # new_status should be 'Approved' or 'Not Approved'
        """
        Navigates to a user's edit page and changes their 'Is teacher approved' status via a checkbox.
        """
        self.log.info(f"Attempting to change 'Is teacher approved' status for {email} to {new_status} via edit page.")
        
        user_edit_link = self._user_edit_link_by_email(email)
        
        if not self.click_element(user_edit_link, locatorType="xpath"):
            self.log.error(f"Failed to click edit link for user {email}. User might not be visible or link locator is incorrect.")
            return False

        self.wait_for_page_load() # Wait for the edit page to load

        self.log.info(f"Navigated to edit page for {email}.")
        
        # We are targeting the 'Is teacher approved' checkbox
        if new_status == "Approved": 
            if not self.check_element_checkbox(self._is_teacher_approved_checkbox, "xpath"):
                self.log.error(f"Failed to check 'Is teacher approved' checkbox for {email}.")
                return False
            self.log.info(f"Checked 'Is teacher approved' checkbox for {email}.")
        elif new_status == "Not Approved":
             if not self.uncheck_element_checkbox(self._is_teacher_approved_checkbox, "xpath"):
                 self.log.error(f"Failed to uncheck 'Is teacher approved' checkbox for {email}.")
                 return False
             self.log.info(f"Unchecked 'Is teacher approved' checkbox for {email}.")
        else:
            self.log.error(f"Invalid new_status for checkbox update: {new_status}. Must be 'Approved' or 'Not Approved'.")
            return False

        # Save the changes
        if self.click_element(self._save_button, locatorType="xpath"):
            self.log.info(f"Clicked save button for {email}.")
            self.wait_for_page_load() # Wait for the save operation to complete and page to reload

            # Verify success message after saving
            if self.is_element_visible(self._successful_change_message, locatorType="xpath", timeout=5):
                self.log.info(f"Successful change message visible for {email}.")
                return True
            else:
                self.log.error(f"Success message not visible after saving changes for {email}.")
                self.take_screenshot_on_failure("save_success_message_missing", "page")
                return False
        else:
            self.log.error(f"Failed to click save button for {email}.")
            return False

    # Helper methods for checkbox manipulation (add these to SeleniumDriver or here if specific to AdminDashboardPage)
    # These are assumed to be in your SeleniumDriver class already. If not, add them.
    # def check_element_checkbox(self, locator, locatorType):
    #     """Checks a checkbox if it's not already checked."""
    #     element = self.get_element(locator, locatorType)
    #     if element and not element.is_selected():
    #         self.click_element(locator, locatorType) # Click to check
    #         return True
    #     elif element and element.is_selected():
    #         self.log.info(f"Checkbox already checked for locator: {locator}")
    #         return True
    #     return False

    # def uncheck_element_checkbox(self, locator, locatorType):
    #     """Unchecks a checkbox if it's not already unchecked."""
    #     element = self.get_element(locator, locatorType)
    #     if element and element.is_selected():
    #         self.click_element(locator, locatorType) # Click to uncheck
    #         return True
    #     elif element and not element.is_selected():
    #         self.log.info(f"Checkbox already unchecked for locator: {locator}")
    #         return True
    #     return False