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

         # --- Locators for elements used in this page object ---
        # XPath to locate the link for a specific user (teacher) in the user list table.
        # It handles cases where the user email might be in an `<a>` tag or a `<td>` cell.
        self._USER_LINK_BY_EMAIL = "//tr[.//a[normalize-space()='{}'] or .//td[normalize-space()='{}']]//a[normalize-space()='{}']"

        # XPath for the 'Teacher Application Status' tab on the user's edit page.
        self._TEACHER_APPLICATION_STATUS_TAB = "//a[normalize-space()='Teacher Application Status']"

        # ID for the commission percentage input field.
        # Based on your previous logs, this has an `id` attribute.
        self._COMMISSION_PERCENTAGE_INPUT = "id_commission_percentage"

        # **CRITICAL**: XPath for the "Approve Teacher" button.
        # This is how the approval action is triggered based on your clarification.
        # Button type="submit" name="_approve_teacher" class="button default" style="..." Approve Teacher</button>
        self._APPROVE_TEACHER_BUTTON = "//button[normalize-space()='Approve Teacher' and @name='_approve_teacher']"
        teacher_courses_link = "//a[@class='nav-link active']"
        self._course_published_status_icon = lambda course_name: f"//td[normalize-space()='{course_name}']/following-sibling::td/img[contains(@alt, 'Published:')]"

    ########### For Course Publish ################
    
         # --- NEW LOCATORS FOR COURSE MANAGEMENT ---
        self._teacher_courses_link = "//a[normalize-space()='Teacher Courses']" # Link in admin dashboard
        self._course_list_table = "//table[@id='courseListTable']" # Table containing courses (adjust ID)
        self._course_row_by_name = lambda course_name: f"//td[normalize-space()='{course_name}']/.."
        self._course_checkbox_by_name = lambda course_name: f"//td[normalize-space()='{course_name}']/preceding-sibling::td/input[@type='checkbox']"
        # Example for published status: an image with alt text "Published: True" or "Published: False"
        self._course_published_status_icon = lambda course_name: f"//td[normalize-space()='{course_name}']/following-sibling::td/img[contains(@alt, 'Published:')]"
        self._action_dropdown = "//select[@name='action']" # Name of the action dropdown
        self._go_button = "//button[@value='go']" # Or input[@type='submit' and @value='Go']

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

    def change_user_status_and_commission(self, user_email, new_approval_status=None, commission_value=None):
        """
        Navigates to a user's edit page, updates their commission percentage,
        and changes their teacher approval status (Approved/Not Approved) via button clicks.

        Args:
            user_email (str): The email of the user (teacher) whose details are to be modified.
            new_approval_status (str, optional): Desired approval status: "Approved" or "Not Approved".
                                                If None, no approval action is performed.
            commission_value (str, optional): The new commission percentage to set (e.g., "15.00").
                                                If None, the commission is not changed.

        Returns:
            bool: True if all specified actions were performed successfully, False otherwise.
        """
        self.log.info(f"Attempting to update status and commission for {user_email}.")

        # 1. Navigate to the specific user's edit page by clicking their link in the list.
        user_link_xpath = self._USER_LINK_BY_EMAIL.format(user_email, user_email, user_email)
        if not self.wait_for_element_and_click(user_link_xpath, "xpath"):
            self.log.error(f"Failed to click on user link for {user_email}. Cannot proceed with status/commission change.")
            self.take_screenshot(f"failed_click_user_link_{user_email}_{self.get_current_timestamp()}.png")
            return False

        self.log.info(f"Navigated to edit page for {user_email}.")
        self.wait_for_page_load() # Ensure the user's edit page is fully loaded

        # 2. Click the 'Teacher Application Status' tab to reveal relevant fields.
        self.log.info("Attempting to click 'Teacher Application Status' tab.")
        if not self.wait_for_element_and_click(self._TEACHER_APPLICATION_STATUS_TAB, "xpath"):
            self.log.error("Failed to click 'Teacher Application Status' tab.")
            self.take_screenshot(f"failed_to_click_teacher_status_tab_{user_email}_{self.get_current_timestamp()}.png")
            return False
        self.log.info("Clicked 'Teacher Application Status' tab.")

        # Wait for the tab content to be visible (e.g., the commission input field).
        # This is crucial as tab content often loads dynamically.
        if not self.is_element_visible(self._COMMISSION_PERCENTAGE_INPUT, "id", timeout=5):
            self.log.error("Commission percentage input not visible after clicking 'Teacher Application Status' tab. This might indicate the tab content did not load correctly.")
            self.take_screenshot(f"commission_input_not_visible_{user_email}_{self.get_current_timestamp()}.png")
            return False
        self.log.info("Confirmed 'Teacher Application Status' tab content (commission input) is visible.")

        # 3. Set the commission percentage if a value is provided.
        
        if commission_value is not None:
            self.log.info(f"Attempting to set commission for {user_email} to: {commission_value}")
            if not self.send_keys_element(data=commission_value,locator=self._COMMISSION_PERCENTAGE_INPUT):
                self.log.error(f"Failed to set commission percentage for {user_email}.")
                return False
            self.log.info(f"Successfully set commission to {commission_value}.")

        # 4. Handle teacher approval or disapproval based on the specified status.
        if new_approval_status == "Approved":
            self.log.info(f"Attempting to click 'Approve Teacher' button for {user_email}.")
            if not self.wait_for_element_and_click(self._APPROVE_TEACHER_BUTTON, "xpath"):
                self.log.error(f"Failed to click 'Approve Teacher' button for {user_email}.")
                self.take_screenshot(f"failed_click_approve_button_{user_email}_{self.get_current_timestamp()}.png")
                return False
            self.log.info(f"Successfully clicked 'Approve Teacher' button for {user_email}.")
            self.wait_for_page_load() # Wait for any redirect or refresh after submission

        elif new_approval_status == "Not Approved":
            self.log.info(f"Attempting to click 'Disapprove Teacher' button for {user_email}.")
            # This logic assumes a separate "Disapprove Teacher" button exists in your UI.
            # If your application handles disapproval differently (e.g., toggling the approve button,
            # or a separate status dropdown combined with a generic "Save"),
            # this section will need to be adjusted to match your actual UI.
            if not self.wait_for_element_and_click(self._DISAPPROVE_TEACHER_BUTTON, "xpath"):
                self.log.error(f"Failed to click 'Disapprove Teacher' button for {user_email}.")
                self.take_screenshot(f"failed_click_disapprove_button_{user_email}_{self.get_current_timestamp()}.png")
                return False
            self.log.info(f"Successfully clicked 'Disapprove Teacher' button for {user_email}.")
            self.wait_for_page_load() # Wait for any redirect or refresh after submission

        # 5. Handle a generic "Save" button if only commission was changed or if approval/disapproval buttons don't submit the form.
        # This is a conditional step: it's only attempted if commission_value was provided AND
        # no specific approval/disapproval button was clicked (assuming those buttons handle submission).
        if commission_value is not None and new_approval_status is None:
            self.log.info(f"Only commission was changed for {user_email}. Checking for generic Save button.")
            # Use a shorter timeout as the button might not always be present or needed.
            if self.is_element_visible(self._SAVE_BUTTON, "xpath", timeout=3):
                self.log.info(f"Attempting to click generic Save button for {user_email}.")
                if not self.wait_for_element_and_click(self._SAVE_BUTTON, "xpath"):
                    self.log.error(f"Failed to click generic Save button for {user_email}.")
                    self.take_screenshot(f"failed_click_save_button_{user_email}_{self.get_current_timestamp()}.png")
                    return False
                self.log.info(f"Successfully clicked generic Save button for {user_email}.")
                self.wait_for_page_load()
            else:
                self.log.info("No generic 'Save' button found or needed after commission change (assuming auto-save or form submission by approval button).")

        self.log.info(f"Finished attempting to update status and commission for {user_email}. Returning True.")
        return True # If execution reaches here without returning False, all specified actions were successful
    
    
    #####################Publish Course ##############
    # Inside your AdminDashboardPage class

    def navigate_to_teacher_courses_page(self):
        """Navigates to the section where teacher-added courses are managed."""
        self.log.info("Navigating to Teacher Courses page.")
        try:
            self.element_click(self._teacher_courses_link, "xpath")
            self.wait_for_page_load() # Assuming you have a general page load wait
            # Optionally, add a check for a header specific to the teacher courses page
            return True
        except Exception as e:
            self.log.error(f"Failed to navigate to Teacher Courses page: {e}")
            self.take_screenshot_on_failure("navigate_teacher_courses_fail", "page")
            return False

    def get_course_published_status(self, course_name):
        """
        Gets the published status of a course from the admin list.
        Assumes status is indicated by 'alt' attribute on an image (e.g., green check for True, red X for False).
        Returns "True", "False", or "Unknown" if not found or alt text is unexpected.
        """
        self.log.info(f"Getting published status for course: {course_name}")
        locator = self._course_published_status_icon(course_name)
        try:
            element = self.wait_for_element(locator, "xpath", timeout=5)
            status_alt = element.get_attribute("alt")
            if "Published: True" in status_alt or "True" == status_alt:
                return "True"
            elif "Published: False" in status_alt or "False" == status_alt:
                return "False"
            else:
                self.log.warning(f"Unexpected alt text for course status '{course_name}': {status_alt}")
                return "Unknown"
        except (NoSuchElementException, TimeoutException) as e:
            self.log.error(f"Failed to find published status icon for course '{course_name}': {e}")
            self.take_screenshot_on_failure(f"get_course_status_fail_{course_name}", "element")
            return "Unknown"
        except Exception as e:
            self.log.error(f"An unexpected error occurred getting course status for '{course_name}': {e}")
            return "Unknown"

    def select_course_checkbox(self, course_name):
        """Selects the checkbox next to a specific course in the list."""
        self.log.info(f"Selecting checkbox for course: {course_name}")
        locator = self._course_checkbox_by_name(course_name)
        try:
            self.element_click(locator, "xpath")
            return True
        except Exception as e:
            self.log.error(f"Failed to select checkbox for {course_name}: {e}")
            self.take_screenshot_on_failure(f"select_course_checkbox_fail_{course_name}", "element")
            return False

    def select_action_from_dropdown(self, action_text):
        """Selects an action from the dropdown menu (e.g., 'Mark selected as publish')."""
        self.log.info(f"Selecting action '{action_text}' from dropdown.")
        try:
            # Assumes self.select_by_visible_text is a helper in SeleniumDriver
            select_element = self.wait_for_element(self._action_dropdown, "xpath")
            select = Select(select_element)
            select.select_by_visible_text(action_text)
            return True
        except Exception as e:
            self.log.error(f"Failed to select action '{action_text}': {e}")
            self.take_screenshot_on_failure(f"select_action_dropdown_fail_{action_text}", "element")
            return False

    def click_go_button(self):
        """Clicks the 'Go' button to apply the selected action."""
        self.log.info("Clicking 'Go' button.")
        try:
            self.click_element(self._go_button, "xpath")
            self.wait_for_page_load() # Wait for the page to reload after action
            return True
        except Exception as e:
            self.log.error(f"Failed to click 'Go' button: {e}")
            self.take_screenshot_on_failure("click_go_button_fail", "element")
            return False