import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from base.selenium_driver import SeleniumDriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import utilities.custome_logger as cl

class AdminDashboardPage(SeleniumDriver):

    
    
    def __init__(self, driver, base_url):
        super().__init__(driver, base_url)
        
        # You might also initialize page-specific locators here
        self._teacher_application_status_tab = "//a[normalize-space()='Teacher Application Status']"
        self._commission_percentage_input = "//input[@name='commission_percentage']" # Example, ensure this is correct
        self._is_teacher_approved_checkbox = "//input[@id='id_is_teacher_approved']" # Example, ensure this is correct
        self._save_button = "//button[@type='submit' and normalize-space()='Save']" # Example
        self._successful_change_message = "//li[contains(text(), 'The profile \"Majd\" was changed successfully.')]" # Example
        # ... other locators
        log = cl.CustomLogger(logging.DEBUG)
        # Locators
        self._dashboard_header = "//h1[normalize-space()='Dashboard' or contains(text(), 'Welcome to the Admin Dashboard')]"
        self._user_profiles_link = "//a[./p[normalize-space()='User Profiles'] and contains(@href, '/admin/accounts/profile/')]"
        self._user_profiles_page_header = "//h1[@class='h4 m-0 pr-3 mr-3 border-right']" # Corrected based on screenshots
        # Locator for the 'Teacher Application Status' tab on the user edit page
    # Using normalize-space() for robust text matching
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
        self._commission_percentage_input = "//input[@id='id_commission_percentage']" # **ADD THIS LOCATOR for the commission field**
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
            if self.is_element_visible(self._user_profiles_page_header, locatorType="xpath", timeout=5):
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
            print("Majd")
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

    def change_user_status_and_commission(self, email, new_approval_status="Approved", commission_value=None):
        """
        Navigates to a user's edit page, updates their approval status (approved/pending),
        and optionally sets a commission percentage.

        Args:
            email (str): The email of the user to modify.
            new_approval_status (str): "Approved" to approve, "Pending" to set as pending.
            commission_value (str, optional): The commission percentage (e.g., "15.00").
                                              Defaults to None.

        Returns:
            bool: True if changes are saved successfully and success message is visible, False otherwise.
        """
        self.log.info(f"Attempting to update status and commission for {email}.")
        user_edit_link = self._user_edit_link_by_email(email)

        try:
            # 1. Click on the user's edit link
            if not self.click_element(user_edit_link, locatorType="xpath"):
                self.log.error(f"Failed to click edit link for user {email}. User might not be visible or link locator is incorrect.")
                self.take_screenshot_on_failure(f"click_user_edit_link_fail_{email}", "page")
                return False
            self.wait_for_page_load()
            self.log.info(f"Navigated to edit page for {email}.")

            # 2. Click the 'Teacher Application Status' tab
            self.log.info("Attempting to click 'Teacher Application Status' tab.")
            if not self.click_element(self._teacher_application_status_tab, locatorType="xpath"):
                self.log.error("Failed to click 'Teacher Application Status' tab.")
                self.take_screenshot_on_failure("tab_click_fail", "page")
                return False
            self.log.info("Clicked 'Teacher Application Status' tab.")
            
            # Wait for content inside the tab to be visible (e.g., commission input)
            if not self.get_element(self._commission_percentage_input, 
                                    locatorType="xpath", 
                                    condition=EC.visibility_of_element_located, 
                                    timeout=5):
                self.log.error("Content inside 'Teacher Application Status' tab (commission input) did not become visible within 5 seconds.")
                self.take_screenshot_on_failure("tab_content_not_visible", "page")
                return False
            self.log.info("Confirmed 'Teacher Application Status' tab content is visible.")

            # 3. Handle 'Is teacher approved' checkbox
            checkbox_element = None
            try:
                # Get the checkbox element
                checkbox_element = self.get_element(self._is_teacher_approved_checkbox,
                                                    locatorType="xpath",
                                                    condition=EC.presence_of_element_located)
                
                if not checkbox_element:
                    self.log.error(f"'Is teacher approved' checkbox not found or not visible for {email}.")
                    self.take_screenshot_on_failure(f"find_approved_checkbox_fail_{email}", "page")
                    return False

                # Determine desired state and current state
                is_approved_desired = (new_approval_status.lower() == "approved")
                is_checkbox_checked = checkbox_element.is_selected()

                if is_approved_desired and not is_checkbox_checked:
                    # If desired is approved but not checked, click to check it
                    self.log.info(f"Clicking 'Is teacher approved' checkbox to set to 'Approved' for {email}.")
                    if not self.click_element(self._is_teacher_approved_checkbox, locatorType="xpath"):
                        self.log.error(f"Failed to click 'Is teacher approved' checkbox to approve for {email}.")
                        self.take_screenshot_on_failure(f"click_approve_checkbox_fail_{email}", "page")
                        return False
                elif not is_approved_desired and is_checkbox_checked:
                    # If desired is pending/not approved but checked, click to uncheck it
                    self.log.info(f"Clicking 'Is teacher approved' checkbox to set to 'Pending' for {email}.")
                    if not self.click_element(self._is_teacher_approved_checkbox, locatorType="xpath"):
                        self.log.error(f"Failed to click 'Is teacher approved' checkbox to set pending for {email}.")
                        self.take_screenshot_on_failure(f"click_pending_checkbox_fail_{email}", "page")
                        return False
                else:
                    self.log.info(f"'Is teacher approved' status is already as desired ({new_approval_status}) for {email}.")

            except StaleElementReferenceException:
                self.log.warning(f"StaleElementReferenceException when handling 'Is teacher approved' checkbox for {email}. Attempting to re-find.")
                # Re-try getting the element
                checkbox_element = self.get_element(self._is_teacher_approved_checkbox,
                                                    locatorType="xpath",
                                                    condition=EC.presence_of_element_located)
                if not checkbox_element:
                    self.log.error(f"Failed to re-find 'Is teacher approved' checkbox after stale error for {email}.")
                    self.take_screenshot_on_failure(f"refind_approved_checkbox_fail_{email}", "page")
                    return False
                # Re-attempt the logic
                is_approved_desired = (new_approval_status.lower() == "approved")
                is_checkbox_checked = checkbox_element.is_selected()
                if is_approved_desired and not is_checkbox_checked:
                    self.log.info(f"Re-clicking 'Is teacher approved' checkbox to set to 'Approved' for {email} after stale.")
                    if not self.click_element(self._is_teacher_approved_checkbox, locatorType="xpath"):
                        self.log.error(f"Failed to re-click 'Is teacher approved' checkbox to approve after stale for {email}.")
                        self.take_screenshot_on_failure(f"reclick_approve_checkbox_fail_{email}", "page")
                        return False
                elif not is_approved_desired and is_checkbox_checked:
                    self.log.info(f"Re-clicking 'Is teacher approved' checkbox to set to 'Pending' for {email} after stale.")
                    if not self.click_element(self._is_teacher_approved_checkbox, locatorType="xpath"):
                        self.log.error(f"Failed to re-click 'Is teacher approved' checkbox to set pending after stale for {email}.")
                        self.take_screenshot_on_failure(f"reclick_pending_checkbox_fail_{email}", "page")
                        return False
                else:
                    self.log.info(f"'Is teacher approved' status is already as desired ({new_approval_status}) for {email} after re-check.")

            except Exception as e:
                self.log.error(f"Could not find or interact with 'Is teacher approved' checkbox for {email}: {e}")
                self.take_screenshot_on_failure(f"find_approved_checkbox_error_{email}", "page")
                return False

            # 4. Set commission percentage if provided
            if commission_value is not None:
                self.log.info(f"Attempting to set commission percentage to {commission_value} for {email}.")
                try:
                    # Ensure input field is visible before sending keys
                    if not self.send_keys_element(commission_value, self._commission_percentage_input, locatorType="xpath"):
                        self.log.error(f"Failed to send commission value '{commission_value}' to input field for {email}.")
                        self.take_screenshot_on_failure(f"send_commission_fail_{email}", "page")
                        return False
                    self.log.info(f"Successfully set commission to {commission_value} for {email}.")
                except ElementNotInteractableException as e:
                    self.log.error(f"Commission percentage input field not interactable for {email}: {e}")
                    self.take_screenshot_on_failure(f"commission_input_not_interactable_{email}", "page")
                    return False
                except Exception as e:
                    self.log.error(f"Could not interact with commission percentage input for {email} due to unexpected error: {e}")
                    self.take_screenshot_on_failure(f"commission_input_error_{email}", "page")
                    return False
            else:
                self.log.info(f"No commission value provided for {email}, skipping.")

            # 5. Save changes
            self.log.info(f"Attempting to save changes for {email}.")
            if self.click_element(self._save_button, locatorType="xpath"):
                self.log.info(f"Clicked save button for {email}.")
                # Wait for page to reload or success message to appear
                self.wait_for_page_load() 
                if self.is_element_visible(self._successful_change_message, locatorType="xpath", timeout=5):
                    self.log.info(f"Changes saved successfully and confirmation message visible for {email}.")
                    return True
                else:
                    self.log.error(f"Success message not visible after saving changes for {email}. Check for validation errors or unexpected redirects.")
                    self.take_screenshot_on_failure("save_success_message_missing", "page")
                    # Optionally, check for specific error messages if needed here
                    return False
            else:
                self.log.error(f"Failed to click save button for {email}.")
                self.take_screenshot_on_failure("click_save_button_fail", "page")
                return False

        except Exception as e:
            self.log.error(f"An error occurred while saving changes for {email}: {e}")
            self.take_screenshot_on_failure("save_changes_error", "page")
            return False