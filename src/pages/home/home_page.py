from base.selenium_driver import SeleniumDriver
from selenium.webdriver.common.by import By
import utilities.custome_logger as cl
import logging

class HomePage(SeleniumDriver):

    def __init__(self, driver):
        super().__init__(driver)
        self.log = cl.CustomLogger(logging.DEBUG) # Initialize logger for this page object

    # Locators for elements on the Home Page
    _course_menu_link = "//a[normalize-space()='Courses']"
    _course_menu_link_type = "xpath" # Added explicit type for clarity

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
