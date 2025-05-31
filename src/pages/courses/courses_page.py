from selenium.webdriver.common.by import By
from base.selenium_driver import SeleniumDriver
from selenium.webdriver.support.ui import Select
import utilities.custome_logger as cl 
import logging 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, NoAlertPresentException, StaleElementReferenceException
import time 
class CoursesPage(SeleniumDriver):

    def __init__(self, driver, base_url):
        # Call the parent class (SeleniumDriver) constructor first.
        super().__init__(driver, base_url)
        # Explicitly initialize self.log here for CoursesPage.
        # This ensures self.log is always available within this class,
        # even if there are subtle issues with inheritance of instance attributes.
        self.log = cl.CustomLogger(logging.DEBUG) 
        
        # --- DEBUGGING LINE ---
        print(f"DEBUG: CoursesPage initialized. self.driver is: {self.driver is not None}. self.log is: {self.log is not None}")
        print(f"DEBUG: Does CoursesPage have wait_for_element? {'wait_for_element' in dir(self)}")
        # --- END DEBUGGING LINE ---

    ################
    ### Locators ###
    ################
    # It's good practice to make locators distinct attributes or use constants
    # For a search box, you'll need its actual locator.
    # _search_box = (By.ID, "search_input_id") # Example: (By.ID, "id_of_search_box") or (By.XPATH, "//input[@name='q']")
    
    _course_name_template = "//h2[contains(text(),'{course_name}')]" # Template for dynamic course names

    # --- CORRECTED LOCATOR for 'View Details' button ---
    # Based on the HTML, the button text is 'View Details' and it has class 'course-action'.
    # Using CSS Selector for robustness, or XPath with correct text.
    _view_course_details_button = "a.course-action"
    _view_course_details_button_type = "css" # Corresponds to By.CSS_SELECTOR in SeleniumDriver's _get_by_type
    # If you prefer XPath:
    # _view_course_details_button = "//a[normalize-space()='View Details']"
    # _view_course_details_button_type = "xpath"
    # If you prefer Link Text (and it's unique):
    # _view_course_details_button = "View Details"
    # _view_course_details_button_type = "linktext"
    # --- END CORRECTED LOCATOR ---

    _register_button = "//button[normalize-space()='Register for Course']"
    _card_number_input = "//input[@id='id_card_number']" # Assuming this is the correct ID
    _card_expiry_month_selector = "//select[@id='id_expiry_month']" # Assuming this is the correct ID
    _card_expiry_year_selector = "//select[@id='id_expiry_year']" # Assuming this is the correct ID
    _pay_button = "//button[normalize-space()='Pay Now']"
    _enroll_error_message = "//div[@role='alert']" # Common locator for alert messages
    _all_courses_cards = "//div[@class='course-card']" # Changed name for clarity
    
    # Locator for the welcome pop-up's close button, based on your screenshot inspection
    # This is an HTML element, not a browser-native alert.
    # You MUST verify these locators by inspecting the "Welcome back" popup.
    _welcome_popup_container = (By.CSS_SELECTOR, "div.alert.alert-success") # Common, but verify
    _welcome_popup_close_button = (By.CSS_SELECTOR, "div.alert.alert-success button.close") # Common, but verify
    _welcome_popup_close_button_type = "css" # Added explicit type for clarity and consistency

    ############################
    ### Element Interactions ###
    ############################

    def dismiss_browser_alert_popup(self, timeout=5):
        """
        Attempts to dismiss a browser-native alert/prompt (like 'Change your password' with OK).
        This is for browser-level popups, not HTML modals.
        """
        self.log.info(f"Attempting to dismiss browser-native alert pop-up with timeout: {timeout}s.")
        try:
            WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            self.log.info(f"Detected browser alert with text: '{alert_text}'")

            # You can add more specific checks here if you have different types of alerts
            if "password" in alert_text.lower() or "data breach" in alert_text.lower():
                self.log.info("Recognized as a password-related alert. Accepting it.")
                alert.accept() # Clicks 'OK' or 'Accept'
            else:
                self.log.warning(f"Detected an unexpected browser alert. Dismissing it to proceed.")
                alert.dismiss() # Clicks 'Cancel' or 'Dismiss'

            self.log.info("Successfully dismissed browser alert.")
            return True # Indicates alert was found and handled
        except TimeoutException:
            self.log.info("No browser-native alert appeared within the timeout.")
            return False
        except NoAlertPresentException: # Should be caught by TimeoutException, but good for explicit safety
            self.log.info("No alert present when trying to switch_to.alert.")
            return False
        except Exception as e:
            self.log.error(f"An unexpected error occurred while handling a browser alert: {e}")
            return False

    def dismiss_welcome_popup(self, timeout=5):
        """
        Dismisses the 'Welcome back' notification pop-up (HTML modal).
        """
        self.log.info("Attempting to dismiss 'Welcome back' pop-up.")
        try:
            # Pass the locator string (index 1 of the tuple) and the locator type string
            self.wait_for_element(self._welcome_popup_close_button[1], self._welcome_popup_close_button_type, timeout=timeout)
            self.click_element(self._welcome_popup_close_button[1], self._welcome_popup_close_button_type)
            self.log.info("Successfully dismissed 'Welcome back' pop-up.")
            # Optional: Wait for the pop-up itself to become invisible after clicking 'x'
            self.wait_for_element_to_be_invisible(self._welcome_popup_container[1], self._welcome_popup_close_button_type, timeout=timeout)
            return True
        except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
            self.log.warning(f"Welcome back pop-up not found or not clickable within timeout: {e}. Proceeding without dismissing.")
            return False
        except Exception as e:
            self.log.error(f"An unexpected error occurred while trying to dismiss the welcome pop-up: {e}")
            return False

    def enterCourseName(self, name):
        """
        Enters a course name into the search box.
        Requires a locator for the search box (e.g., self._search_box).
        """
        # Uncomment and use if you have a search box locator defined:
        # self.send_keys_element(name, locator=self._search_box[0], locatorType=self._search_box[1])
        self.log.info(f"Entered course name: {name} (Function 'enterCourseName' is not fully implemented yet without a search box locator).")
        pass # Placeholder if no search box is present

    def clickCourseByName(self, courseName):
        """
        Clicks on a course card identified by its name.
        Assumes the course name is within an H2 tag as per your locator template.
        """
        # Dynamically create the XPath for the specific course name
        locator = self._course_name_template.format(course_name=courseName)
        self.log.info(f"Attempting to click on course: '{courseName}' using locator: '{locator}'")
        # click_element will handle scrolling the course name into view if it's not visible
        self.click_element(locator=locator, locatorType="xpath")
        self.log.info(f"Successfully clicked on course: '{courseName}'.")


    def view_course_details(self):
        """
        Clicks the 'View Details' button for a course.
        Leverages SeleniumDriver's click_element to handle waiting and scrolling.
        This method assumes you are already on the Courses Listing page
        and the 'View Details' button is present (e.g., for the first course card).
        """
        self.log.info("Clicking 'View Details' button for a course.")
        # `click_element` now handles scrolling the element into view internally.
        # Corrected locator: Use _view_course_details_button and _view_course_details_button_type
        # The error log shows "//a[normalize-space()='View Course']" which is different.
        # Ensure your _view_course_details_button locator is correct for your application.
        self.click_element(locator=self._view_course_details_button,
                           locatorType=self._view_course_details_button_type)
        self.log.info("Successfully clicked 'View Details' button.")
        # After clicking 'View Details', you're likely on a Course Detail Page or a modal opens.
        # You should return the appropriate Page Object for the next state here.
        # from pages.courses.course_detail_page import CourseDetailPage # Example import
        # return CourseDetailPage(self.driver)


    def click_register_course(self):
        """
        Clicks the 'Register for Course' button.
        This button is typically found on the Course Detail Page/Modal.
        """
        self.log.info("Clicking 'Register for Course' button.")
        # `click_element` will handle waiting for clickability and scrolling.
        self.click_element(locator=self._register_button, locatorType="xpath")
        self.log.info("Successfully clicked 'Register for Course' button.")

    ############## Card Info Functions #######################################################
    def enter_card_num(self, card_num):
        """
        Enters the credit card number.
        """
        self.log.info(f"Entering card number: {card_num}")
        # `send_keys_element` should handle waiting for visibility/interactability.
        self.send_keys_element(card_num, locator=self._card_number_input, locatorType="xpath")
        self.log.info("Card number entered.")

    def select_expiry_month(self, card_exp_month):
        """
        Selects the card expiry month from a dropdown.
        """
        self.log.info(f"Selecting expiry month: {card_exp_month}")
        # `get_element` will wait for the dropdown to be present.
        month_dropdown_element = self.get_element(locator=self._card_expiry_month_selector, locatorType="xpath")
        if month_dropdown_element:
            select = Select(month_dropdown_element)
            select.select_by_value(str(card_exp_month)) # Ensure value is a string
            self.log.info(f"Expiry month '{card_exp_month}' selected.")
        else:
            self.log.error(f"Could not find expiry month dropdown element: {self._card_expiry_month_selector}")
            raise NoSuchElementException(f"Expiry month dropdown not found: {self._card_expiry_month_selector}")
    
    def select_expiry_year(self, card_exp_year):
        """
        Selects the card expiry year from a dropdown.
        """
        self.log.info(f"Selecting expiry year: {card_exp_year}")
        # `get_element` will wait for the dropdown to be present.
        year_dropdown_element = self.get_element(locator=self._card_expiry_year_selector, locatorType="xpath")
        if year_dropdown_element:
            select = Select(year_dropdown_element)
            select.select_by_value(str(card_exp_year)) # Ensure value is a string
            self.log.info(f"Expiry year '{card_exp_year}' selected.")
        else:
            self.log.error(f"Could not find expiry year dropdown element: {self._card_expiry_year_selector}")
            raise NoSuchElementException(f"Expiry year dropdown not found: {self._card_expiry_year_selector}")
            
    ############################################################################################

    def click_pay_button(self):
        """
        Clicks the 'Pay Now' button.
        """
        self.log.info("Clicking 'Pay Now' button.")
        # `click_element` will handle waiting for clickability and scrolling.
        self.click_element(locator=self._pay_button, locatorType="xpath")
        self.log.info("Successfully clicked 'Pay Now' button.")

    def enter_credit_card_info(self, card_num, card_exp_month, card_exp_year):
        """
        Enters all credit card details.
        """
        self.log.info("Entering credit card information.")
        self.enter_card_num(card_num)
        self.select_expiry_month(card_exp_month)
        self.select_expiry_year(card_exp_year)
        self.log.info("Credit card information entered.")

    def enroll_course(self, card_num="", card_exp_month="", card_exp_year=""):
        """
        Comprehensive method to enroll in a course.
        Assumes the test has already navigated to the Courses Listing page.
        """
        self.log.info("Starting course enrollment process.")
        
        # Scroll down if the list of courses is long and the target course is off-screen.
        # This is a general page scroll, not element-specific.
        self.webScroll("down") 

        # View course details: This method now uses the corrected locator and
        # should return the CourseDetailPage object.
        # It also internally handles scrolling the 'View Details' button into view.
        # Make sure your test calls this correctly to get the new page object.
        # Example: self.course_detail_page = self.courses_page.view_course_details()
        self.view_course_details() 
        
        # After clicking 'View Details', if a new page/modal loads and requires further scrolling
        # before the 'Register for Course' button is visible, this scroll might be necessary.
        # However, `click_register_course` (which calls `click_element`) should handle its own scrolling.
        # Keep this if you observe the 'Register for Course' button is still off-screen initially
        # after the Course Detail page/modal loads.
        #self.webScroll("down")
        self.webScroll("down")
        time.sleep(4) 
        self.click_register_course()
        
        # Scroll down again if needed for the payment form fields
        self.webScroll("down")
        self.webScroll("down")
        self.enter_credit_card_info(card_num, card_exp_month, card_exp_year)
        self.click_pay_button()
        self.log.info("Course enrollment process completed (or attempted).")
        # REMOVED: self.dismiss_welcome_popup() - This should be called earlier in the test setup.
        
    def verifyEnrollFailed(self):
        """
        Verifies if an enrollment error message is displayed.
        """
        self.log.info("Verifying if enrollment failed message is present.")
        # Using the new isElementVisible which internally uses get_element and handles exceptions
        result = self.is_element_visible(locator=self._enroll_error_message, locatorType="xpath")
        self.log.info(f"Enrollment failed message visible: {result}")
        return result
