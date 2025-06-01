from selenium.webdriver.common.by import By
from base.selenium_driver import SeleniumDriver
from selenium.webdriver.support.ui import Select
import utilities.custome_logger as cl 
import logging 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, NoAlertPresentException, StaleElementReferenceException
import time 


class CourseAddingPage(SeleniumDriver):

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
    add_new_course_button = "//a[@class='btn btn-success']"
    course_title_locator = "//input[@id='id_title']"
    course_describtion_locator = " //textarea[@id='id_description']"
    course_price_locator = "//input[@id='id_price']" 


    COURSE_LANGUAGE = "English"
    COURSE_CATALOGE = "IT"
    COURSE_LEVER = "Starter"

    ############################
    ### Element Interactions ###
    ############################



    def click_add_new_course_button(self):
        self.log.info("Clicking 'Pay Now' button.")
        # `click_element` will handle waiting for clickability and scrolling.
        self.click_element(locator=self.add_new_course_button, locatorType="xpath")
        self.log.info("Successfully clicked 'Pay Now' button.")

    def select_course_language(self, card_exp_month):
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
    


    def add_new_course(self):
        self.click_add_new_course_button()