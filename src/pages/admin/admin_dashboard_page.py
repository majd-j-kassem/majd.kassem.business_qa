import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from base.selenium_driver import SeleniumDriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import utilities.custome_logger as cl
import time # Import time for potential short sleeps

class AdminDashboardPage(SeleniumDriver):

    log = cl.CustomLogger(logging.DEBUG)

    def __init__(self, driver, base_url):
        super().__init__(driver, base_url) # Pass base_url to super() if SeleniumDriver uses it
        self.driver = driver # Redundant but harmless, as super().__init__ already sets it
        
        # --- Page-specific Locators ---
        self._teacher_application_status_tab = "//a[normalize-space()='Teacher Application Status']"
        self._commission_percentage_input = "id_commission_percentage" # Assuming this is an ID
        self._is_teacher_approved_checkbox = "//input[@id='id_is_teacher_approved']" # Example, ensure this is correct
        self._save_button = "//button[@type='submit' and normalize-space()='Save']" # Example
        self._successful_change_message = "//div[contains(@class, 'alert-success') and contains(., 'was changed successfully.')]" # Example
        self._dashboard_header = "//i[@class='far fa-user']"
        self._user_profiles_link = "//a[@class='nav-link active']"
        self._user_profiles_page_header = "//a[@class='d-block']" # Corrected based on screenshots
        self.teacher_profile_link = "//p[normalize-space()='User Profiles']"







        # XPath to locate the link for a specific user (teacher) in the user list table.
        self._USER_LINK_BY_EMAIL = "//tr[.//a[normalize-space()='{}'] or .//td[normalize-space()='{}']]//a[normalize-space()='{}']"

        # XPath for the 'Teacher Application Status' tab on the user's edit page.
        self._TEACHER_APPLICATION_STATUS_TAB = "//a[normalize-space()='Teacher Application Status']"

        # **CRITICAL**: XPath for the "Approve Teacher" button.
        self._APPROVE_TEACHER_BUTTON = "//button[normalize-space()='Approve Teacher' and @name='_approve_teacher']"
        # Assuming there might be a "Disapprove Teacher" button, if not, remove/adjust
        self._DISAPPROVE_TEACHER_BUTTON = "//button[normalize-space()='Disapprove Teacher' and @name='_disapprove_teacher']"


        # --- NEW LOCATORS FOR COURSE MANAGEMENT ---
        self._teacher_courses_link = "//a[./p[normalize-space()='Teacher Courses']]" # Link in admin dashboard
        self._course_list_table = "//table[@id='courseListTable']" # Table containing courses (adjust ID)
        self._course_row_by_name = lambda course_name: f"//td[normalize-space()='{course_name}']/.."
        self._course_checkbox_by_name = lambda course_name: f"//input[@type='checkbox' and contains(@aria-label, '{course_name}')]"
        self.user_link_profile__locator = lambda email: (f"//a[normalize-space()='{email.split('@')[0]}']")
        self._course_published_status_icon = lambda course_name: f"//td[normalize-space()='{course_name}']"
        self._action_dropdown = "//select[@name='action']" # Name of the action dropdown
        self._go_button = "//button[@title='Run the selected action']" # Or input[@type='submit' and @value='Go']
        self.teadher_user_name = self._user_edit_link_by_email = lambda email: f"//a[normalize-space()='{email.split('@')[0]}']"
        self.teacher_app_status_tabe = "//a[normalize-space()='Teacher Application Status']"
        self.commitin_input_text = "//input[@id='id_commission_percentage']"
        self.approve_button_locator = "//button[@name='_approve_teacher']"
        # Locators for user list table
        self._user_row_by_email = lambda email: f"//tr[.//a[normalize-space()='{email}'] or .//td[normalize-space()='{email}']]"
        self._is_teacher_pending_status_in_row = lambda email: \
            f"{self._user_row_by_email(email)}/td[3]//img[@alt='True' or @alt='False']" # Third column
        self._is_teacher_approved_status_in_row = lambda email: \
            f"{self._user_row_by_email(email)}/td[4]//img[@alt='True' or @alt='False']" # Fourth column

        self._user_edit_link_by_email = lambda email: f"{self._user_row_by_email(email)}//a[normalize-space()='{email}']"
        self._is_teacher_approved_checkbox = "//input[@id='id_is_teacher_approved']"
        self._save_button_generic = "//input[@type='submit' and @value='Save']" # Renamed to avoid conflict if you have a specific 'Save' for commission
        self._successful_change_message_generic = "//li[contains(@class, 'success') and contains(text(), 'was changed successfully')]" # Renamed

    def is_on_dashboard_page(self):
        """
        Verifies if the current page is the admin dashboard.
        """
        return self.is_element_visible(self._dashboard_header, locatorType="xpath")

    def navigate_to_user_management(self):
        self.log.info("Attempting to navigate to User Profiles section.")

        if self.click_element(self.teacher_profile_link, locatorType="xpath"): # Using click_element
            self.wait_for_page_load() # Wait for the new page to load
            # Verify we are on the User Profiles list page (e.g., check for a header)
            if self.is_element_visible(self._user_profiles_page_header, locatorType="xpath", timeout=5):
                 self.log.info("Successfully navigated to User Profiles list page.")
                 return True
            else:
                 self.log.error("Navigated to 'User Profiles' but list page header not visible.")
                 self.take_screenshot("user_profiles_list_page_load_fail.png") # Use generic take_screenshot
                 return False
        else:
            self.log.error("Could not find or click the 'User Profiles' link.")
            self.take_screenshot("navigate_to_user_profiles_fail.png") # Use generic take_screenshot
            return False

    def get_user_status_from_list(self, email, status_type="approved"):
        """
        Retrieves the status of a user from a table/list based on icon presence.
        status_type can be 'pending' (for 'Is teacher application pending') or 'approved' (for 'Is teacher approved').
        Returns 'True' or 'False' (as strings) based on alt attribute, or None if element not found.
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
            status_icon = self.get_element(status_element_locator, locatorType="xpath") # Using get_element
            if status_icon:
                alt_text = status_icon.get_attribute("alt")
                if alt_text == "True":
                    self.log.info(f"Status for {email} is 'True' (alt='True').")
                    return "True"
                elif alt_text == "False":
                    self.log.info(f"Status for {email} is 'False' (alt='False').")
                    return "False"
                else:
                    self.log.warning(f"Unknown alt text for status icon for {email}: {alt_text}")
                    return None
            else:
                self.log.warning(f"Status icon element not found for {email} with locator: {status_element_locator}")
                return None
        except Exception as e: # Catch all exceptions from _wait_for_element
            self.log.error(f"Error finding status icon for user {email} (status_type: {status_type}): {e}")
            self.take_screenshot(f"user_status_icon_not_found_{email}_{status_type}_{self.get_current_timestamp()}.png")
            return None

    def change_user_status_and_commission(self, user_email, new_approval_status=None, commission_value=None):
        
        self.log.info(f"Selecting checkbox for course: {user_email}")
        locator_1 = self.teadher_user_name(user_email)
        
        self.click_element(locator_1, "xpath")
        time.sleep(1)
        self.click_element(self.teacher_app_status_tabe, "xpath")
        time.sleep(1)
        self.send_keys_element(commission_value, self.commitin_input_text, "xpath")
        time.sleep(1) 
        self.click_element(self.approve_button_locator, "xpath")
        
      
    

    def navigate_to_teacher_courses_page(self):
        """Navigates to the section where teacher-added courses are managed."""
        self.log.info("Navigating to Teacher Courses page.")
        try:
            # CORRECTED: Use self.click_element instead of self.element_click
            if self.click_element(self._teacher_courses_link, "xpath"):
                return True
            else:
                self.log.error("Clicking teacher courses link failed.")
                return False
        except Exception as e:
            self.log.error(f"An unexpected error occurred navigating to Teacher Courses page: {e}")
            self.take_screenshot("navigate_teacher_courses_exception.png")
            return False

    def get_course_published_status(self, course_name):
        
        locator = self._course_published_status_icon(course_name)
        try:
            # CORRECTED: Use self.get_element instead of self._wait_for_element
            element = self.get_element(locator, "xpath", timeout=5, condition=EC.presence_of_element_located)
            if element:
                status_alt = element.get_attribute("alt")
                if "Published: True" in status_alt or "True" == status_alt:
                    return "True"
                elif "Published: False" in status_alt or "False" == status_alt:
                    return "False"
                else:
                    self.log.warning(f"Unexpected alt text for course status '{course_name}': {status_alt}")
                    return "Unknown"
            else:
                self.log.error(f"Published status icon element not found for course '{course_name}'.")
                return "Unknown" # get_element already logs and screenshots on failure
        except Exception as e: # Catching general exception for robustness
            self.log.error(f"An unexpected error occurred getting course status for '{course_name}': {e}")
            self.take_screenshot_on_failure(f"get_course_status_fail_unexpected_{course_name}", "element")
            return "Unknown"

    def select_course_checkbox(self, course_name):
        """Selects the checkbox next to a specific course in the list."""
        self.log.info(f"Selecting checkbox for course: {course_name}")
        locator = self._course_checkbox_by_name(course_name)
        try:
            # CORRECTED: Use self.click_element instead of self.element_click
            if self.click_element(locator, "xpath"):
                return True
            else:
                self.log.error(f"Clicking checkbox for {course_name} failed.")
                return False
        except Exception as e:
            self.log.error(f"An unexpected error occurred selecting checkbox for {course_name}: {e}")
            self.take_screenshot(f"select_course_checkbox_exception_{self._clean_locator_name(course_name)}_{self.get_current_timestamp()}.png")
            return False

    def select_action_from_dropdown(self, action_text):
        """Selects an action from the dropdown menu (e.g., 'Mark selected as publish')."""
        self.log.info(f"Selecting action '{action_text}' from dropdown.")
        try:
            # CORRECTED: Use self.get_element to get the Select element
            select_element = self.get_element(self._action_dropdown, "xpath", condition=EC.presence_of_element_located)
            if select_element:
                select = Select(select_element)
                select.select_by_visible_text(action_text)
                self.log.info(f"Successfully selected '{action_text}' from dropdown.")
                return True
            else:
                self.log.error(f"Action dropdown element '{self._action_dropdown}' not found or not present.")
                return False
        except Exception as e:
            self.log.error(f"Failed to select action '{action_text}': {e}")
            self.take_screenshot(f"select_action_dropdown_exception_{self._clean_locator_name(action_text)}_{self.get_current_timestamp()}.png")
            return False

    def click_go_button(self):
        """Clicks the 'Go' button to apply the selected action."""
        self.log.info("Clicking 'Go' button.")
        try:
            # CORRECTED: Use self.click_element
            if self.click_element(self._go_button, "xpath"):
                self.wait_for_page_load() # Wait for the page to reload after action
                return True
            else:
                self.log.error("Clicking 'Go' button failed.")
                return False
        except Exception as e:
            self.log.error(f"An unexpected error occurred clicking 'Go' button: {e}")
            self.take_screenshot("click_go_button_exception.png")
            return False