from base.selenium_driver import SeleniumDriver
from selenium.webdriver.common.by import By
import utilities.custome_logger as cl
import logging

class HomePage(SeleniumDriver):

    def __init__(self, driver,base_url):
        super().__init__(driver, base_url)
        self.log = cl.CustomLogger(logging.DEBUG) # Initialize logger for this page object

    # Locators for elements on the Home Page
    _course_menu_link = "//a[normalize-space()='Courses']"
    _course_menu_link_type = "xpath" # Added explicit type for clarity
    _join_as_teacher_link = "//a[normalize-space()='Join us as a teacher']"

    def go_to_course_page(self):
        """
        Navigates to the Courses page by clicking the 'Courses' link in the menu.
        """
        self.log.info("Attempting to navigate to Courses page.")
        try:
            # Re-locate the element just before clicking to avoid StaleElementReferenceException
            self.click_element(locator=self._course_menu_link, locatorType=self._course_menu_link_type)
            self.log.info("Successfully navigated to Courses page.")
        except Exception as e:
            self.log.error(f"Failed to navigate to Courses page. Error: {e}")
            raise # Re-raise the exception to fail the test if navigation fails

    def go_to_teacher_signup_page(self):
        """
        Navigates to the Teacher Join flow page by clicking the 'Join us as a teacher' link in the Footer.
        """
        self.log.info("Attempting to navigate to Join as a Teacher page.")
        try:
            # Re-locate the element just before clicking to avoid StaleElementReferenceException
            self.click_element(locator=self._join_as_teacher_link, locatorType="xpath")
            self.log.info("Successfully navigated to Join As a Teacher page.")
        except Exception as e:
            self.log.error(f"Failed to navigate to Teacher page. Error: {e}")
            raise # Re-raise the exception to fail the test if navigation fails
