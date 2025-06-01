from selenium.webdriver.common.by import By
from base.selenium_driver import SeleniumDriver
from selenium.webdriver.support.ui import Select
import utilities.custome_logger as cl 
import logging 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, NoAlertPresentException, StaleElementReferenceException
import time 
class TeacherSignPage(SeleniumDriver):

    def __init__(self, driver, base_url):
        # Call the parent class (SeleniumDriver) constructor first.
        super().__init__(driver,base_url)
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

    _full_name_en_input = "//input[@id='id_full_name_en']"
    _full_name_ar_input = "//input[@id='id_full_name_ar']" # Assuming this is the correct ID
    _email_input = "//input[@id='id_email']" # Assuming this is the correct ID
    _phone_number = "//input[@id='id_phone_number']" # Assuming this is the correct ID
    _next_teacher_info_butt = "//button[normalize-space()='Next: Teaching Info']"
    _year_of_experince_input = "//input[@id='id_experience_years']" # Common locator for alert messages
    _university_input = "//input[@id='id_university']" # Changed name for clarity
    _graduate_year_input = "//input[@id='id_graduation_year']"
    _specialization_input = "//input[@id='id_major']"
    _bio_input = "//textarea[@id='id_bio']"
    _next_button = "//button[normalize-space()='Next']"
    _submit_button = "//button[normalize-space()='Submit Application']"
    _password_input = "//input[@id='id_password']"
    _password_input_2 = "//input[@id='id_password_confirm']"
    _set_password = "//button[normalize-space()='Set Password & Submit Application']"
    _success_joining_message = "//h2[normalize-space()='Application Submitted Successfully!']"
    
    # Locator for the welcome pop-up's close button, based on your screenshot inspection
    # This is an HTML element, not a browser-native alert.
    # You MUST verify these locators by inspecting the "Welcome back" popup.
    _welcome_popup_container = (By.CSS_SELECTOR, "div.alert.alert-success") # Common, but verify
    _welcome_popup_close_button = (By.CSS_SELECTOR, "div.alert.alert-success button.close") # Common, but verify
    _welcome_popup_close_button_type = "css" # Added explicit type for clarity and consistency

    ############################
    ### Element Interactions ###
    ############################
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
        self.click_element(locator=self._full_name_en_input, locatorType="xpath")
        self.log.info("Successfully clicked 'Register for Course' button.")

    ############## Step 1: Basic Information ####################################
    def enter_full_name_en(self, full_name_en):
        """
        Enters the credit card number.
        """
        self.log.info(f"Entering Full Name En: {full_name_en}")
        # `send_keys_element` should handle waiting for visibility/interactability.
        self.send_keys_element(full_name_en, locator=self._full_name_en_input, locatorType="xpath")
        self.log.info("Full Name English Entered")

    def enter_full_name_ar(self, full_name_ar):
        """
        Enters the credit card number.
        """
        self.log.info(f"Entering Full Name Ar: {full_name_ar}")
        # `send_keys_element` should handle waiting for visibility/interactability.
        self.send_keys_element(full_name_ar, locator=self._full_name_ar_input, locatorType="xpath")
        self.log.info("Full Name Arabic Entered")

    def enter_email(self, email):
        """
        Enter the email of the neaw teacher
        """
        self.log.info(f"Entering Email: {email}")
        # `send_keys_element` should handle waiting for visibility/interactability.
        self.send_keys_element(email, locator=self._email_input, locatorType="xpath")
        self.log.info("Email Entered")
    
    def enter_phone_no(self, phone_number):
        """
        Enter the Phone Number of the neaw teacher
        """
        self.log.info(f"Entering Phone Number: {phone_number}")
        # `send_keys_element` should handle waiting for visibility/interactability.
        self.send_keys_element(phone_number, locator=self._phone_number, locatorType="xpath")
        self.log.info("Phone number Entered")

    def click_next_to_teacher_info(self):
        """
        Clicks the 'Pay Now' button.
        """
        self.log.info("Clicking 'Pay Now' button.")
        # `click_element` will handle waiting for clickability and scrolling.
        self.click_element(locator=self._next_teacher_info_butt, locatorType="xpath")
        self.log.info("Successfully clicked 'Pay Now' button.")
    ############################################################################################
    ############## Step 2: Step 2: Professional Details ####################################
    def enter_year_of_exp(self, year_of_exp):
        """
        Enters the credit card number.
        """
        self.log.info(f"Entering Full Name En: {year_of_exp}")
        # `send_keys_element` should handle waiting for visibility/interactability.
        self.send_keys_element(year_of_exp, locator=self._year_of_experince_input, locatorType="xpath")
        self.log.info("Full Name English Entered")
    def enter_university_attenf(self, university):
        """
        Enters the credit card number.
        """
        self.log.info(f"Entering Full Name En: {university}")
        # `send_keys_element` should handle waiting for visibility/interactability.
        self.send_keys_element(university, locator=self._university_input, locatorType="xpath")
        self.log.info("Full Name English Entered")
    def enter_graduat_year(self, gradutae_year):
        """
        Enters the credit card number.
        """
        self.log.info(f"Entering Full Name En: {gradutae_year}")
        # `send_keys_element` should handle waiting for visibility/interactability.
        self.send_keys_element(gradutae_year, locator=self._graduate_year_input, locatorType="xpath")
        self.log.info("Full Name English Entered")
    def enter_study_major(self, study_major):
        """
        Enters the credit card number.
        """
        self.log.info(f"Entering Full Name En: {study_major}")
        # `send_keys_element` should handle waiting for visibility/interactability.
        self.send_keys_element(study_major, locator=self._specialization_input, locatorType="xpath")
        self.log.info("Full Name English Entered")
    def enter_bio(self, bio):
        """
        Enters the credit card number.
        """
        self.log.info(f"Entering Full Name En: {bio}")
        # `send_keys_element` should handle waiting for visibility/interactability.
        self.send_keys_element(bio, locator=self._bio_input, locatorType="xpath")
        self.log.info("Full Name English Entered")
    def click_next_to_review_stage(self):
        """
        Clicks the 'Pay Now' button.
        """
        self.log.info("Clicking 'Pay Now' button.")
        # `click_element` will handle waiting for clickability and scrolling.
        self.click_element(locator=self._next_button, locatorType="xpath")
        self.log.info("Successfully clicked 'Pay Now' button.")
    ############################################################################################
    ############## Step 3: Step 3: Review ####################################
    def click_submit_registeration(self):
        """
        Clicks the 'Pay Now' button.
        """
        self.log.info("Clicking 'Pay Now' button.")
        # `click_element` will handle waiting for clickability and scrolling.
        self.click_element(locator=self._submit_button, locatorType="xpath")
        self.log.info("Successfully clicked 'Pay Now' button.")
    ############################################################################################
    ############## Step 4 Step 4: Password set ####################################

    def enter_password(self, password):
        """
        Enter the Phone Number of the neaw teacher
        """
        self.log.info(f"Entering Phone Number: {password}")
        # `send_keys_element` should handle waiting for visibility/interactability.
        self.send_keys_element(password, locator=self._password_input, locatorType="xpath")
        self.log.info("Phone number Entered")
    def enter_password_2(self, password_2):
        """
        Enter the Phone Number of the neaw teacher
        """
        self.log.info(f"Entering Phone Number: {password_2}")
        # `send_keys_element` should handle waiting for visibility/interactability.
        self.send_keys_element(password_2, locator=self._password_input_2, locatorType="xpath")
        self.log.info("Phone number Entered")

    def click_submit_password_set(self):
        """
        Clicks the 'Pay Now' button.
        """
        self.log.info("Clicking 'Pay Now' button.")
        # `click_element` will handle waiting for clickability and scrolling.
        self.click_element(locator=self._set_password, locatorType="xpath")
        self.log.info("Successfully clicked 'Pay Now' button.")

    def enter_teacher_password(self, password, password_2):
        self.enter_password(password)
        self.enter_password_2(password_2)
    ############################################################################################
    def enter_basic_teacher_info(self, full_name_en, full_name_ar, email, phone_number):
        """
        Enters all credit card details.
        """
        self.log.info("Entering credit card information: Step 1: Basic Information")
        self.enter_full_name_en(full_name_en)
        self.enter_full_name_ar(full_name_ar)
        self.enter_email(email)
        self.enter_phone_no(phone_number)
        self.log.info("Step 1: Basic Information Was Entered")
    def enter_profesional_teacher_info(self, year_of_exp, university_attend, 
                                       graduate_year, major_study, bio_teacher):
        """
        Enters all credit card details.
        """
        self.log.info("Entering Teacher Profesional Info: Step 2: Profesional Information")
        self.enter_year_of_exp(year_of_exp)
        self.enter_university_attenf(university_attend)
        self.enter_graduat_year(graduate_year)
        self.enter_study_major(major_study)
        self.enter_bio(bio_teacher)
        self.log.info("Step 1: Basic Information Was Entered")
    
   

    def teacher_join(self, full_name_en="", full_name_ar="", email="", phone_number="",
                     year_of_exp="", university_attend="", graduate_year="", 
                     major_study="", bio_teacher="", password="", password_2=""):
        
        self.enter_basic_teacher_info(full_name_en, full_name_ar, email, phone_number)
        self.click_next_to_teacher_info()
        self.enter_profesional_teacher_info(year_of_exp, university_attend, graduate_year,
                                            major_study, bio_teacher)
        self.click_next_to_review_stage()
        self.click_submit_registeration()
        self.enter_teacher_password(password, password_2)
        self.click_submit_password_set()


    def verify_joining_succssed(self):
        """
        Verifies if an enrollment error message is displayed.
        """
        self.log.info("Verifying if enrollment failed message is present.")
        # Using the new isElementVisible which internally uses get_element and handles exceptions
        result = self.is_element_visible(locator=self._success_joining_message, locatorType="xpath")
        self.log.info(f"Enrollment failed message visible: {result}")
        return result
