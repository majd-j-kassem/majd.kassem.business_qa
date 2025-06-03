from base.selenium_driver import SeleniumDriver
from selenium.webdriver.common.by import By
import utilities.custome_logger as cl
import logging

class HomePage(SeleniumDriver):

    def __init__(self, driver,base_url):
        super().__init__(driver, base_url)
        self.log = cl.CustomLogger(logging.DEBUG) # Initialize logger for this page object

    # Locators for elements on the Home Page
        self._course_menu_link = "//a[normalize-space()='Courses']"
        self._course_menu_link_type = "xpath" # Added explicit type for clarity
        self._join_as_teacher_link = "//a[normalize-space()='Join us as a teacher']"
        self._home_page_locator = "//nav[@class='main-nav']//a[normalize-space()='Home']"
        self._teacher_dashboard_link_locator = "//a[normalize-space()='Dashboard']"
        self._course_card_by_name = "//h2[normalize-space()='{course_name}']"

        
    def go_to_course_page(self):
        
        self.log.info("Attempting to navigate to Courses page.")
        try:
            # Re-locate the element just before clicking to avoid StaleElementReferenceException
            self.click_element(locator=self._course_menu_link, locatorType=self._course_menu_link_type)
            self.log.info("Successfully navigated to Courses page.")
        except Exception as e:
            self.log.error(f"Failed to navigate to Courses page. Error: {e}")
            raise # Re-raise the exception to fail the test if navigation fails

    def go_to_teacher_signup_page(self):
       
        try:
            self.click_element(locator=self._join_as_teacher_link, locatorType="xpath")
            self.log.info("Successfully navigated to Join As a Teacher page.")
        except Exception as e:
            self.log.error(f"Failed to navigate to Teacher page. Error: {e}")
            raise # Re-raise the exception to fail the test if navigation fails
    def go_to_home_page(self):
        self.driver.get(self.base_url)
       
        self.log.info("Attempting to navigate to Join as a Teacher page.")
        try:
            # Re-locate the element just before clicking to avoid StaleElementReferenceException
            self.click_element(locator=self._home_page_locator, locatorType="xpath")
            self.log.info("Successfully navigated to Join As a Teacher page.")
        except Exception as e:
            self.log.error(f"Failed to navigate to Teacher page. Error: {e}")
            raise # Re-raise the exception to fail the test if navigation fails

    def go_to_Teacher_Dashboard_page(self):
    
        try:
            # Re-locate the element just before clicking to avoid StaleElementReferenceException
            self.click_element(locator=self._teacher_dashboard_link_locator, locatorType="xpath")
            self.log.info("Successfully navigated to Join As a Teacher page.")
        except Exception as e:
            self.log.error(f"Failed to navigate to Teacher page. Error: {e}")
            raise # Re-raise the exception to fail the test if navigation fails


    def is_course_visible_on_homepage(self, course_name, timeout=10):
        
        self.log.info(f"Checking if course '{course_name}' is visible on the homepage.")
        # Construct the specific locator for the course using the provided name
        course_locator = self._course_card_by_name.format(course_name=course_name)
        is_logged_in = self.is_element_visible(course_locator, locatorType="xpath", timeout=20)
        return is_logged_in

    