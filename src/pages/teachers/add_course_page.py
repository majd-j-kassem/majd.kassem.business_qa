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
    course_price_locator = "id_price" 
    add_course_button = "//button[@type='submit']"
    course_language_list = "id_language"
    course_category_2 = "id_categories_2"
    course_level_locator = "id_level"
    submit_adding_of_course = "//button[@type='submit']"
    successull_adding_course_meesaage = "//div[@role='alert']"
    course_image_locator = "id_course_picture"
    course_video_link_locator = "id_video_trailer_url"


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

    def select_course_language(self, course_language):
        self.log.info(f"Selecting Course Language: {course_language}")
        # `get_element` will wait for the dropdown to be present.
        month_dropdown_element = self.get_element(locator=self.course_language_list, locatorType="id")
        if month_dropdown_element:
            select = Select(month_dropdown_element)
            select.select_by_visible_text(str(course_language)) # Ensure value is a string
            self.log.info(f"Language: '{course_language}' selected.")
        else:
            self.log.error(f"Could not find course lnguage dropdown element: {self.course_language_list}")
            raise NoSuchElementException(f"course lnguage dropdown not found: {self.course_language_list}")
    def select_course_level(self, course_level):
        self.log.info(f"Selecting Course Language: {course_level}")
        # `get_element` will wait for the dropdown to be present.
        month_dropdown_element = self.get_element(locator=self.course_level_locator, locatorType="id")
        if month_dropdown_element:
            select = Select(month_dropdown_element)
            select.select_by_visible_text(str(course_level)) # Ensure value is a string
            self.log.info(f"Language: '{course_level}' selected.")
        else:
            self.log.error(f"Could not find course lnguage dropdown element: {self.course_level_locator}")
            raise NoSuchElementException(f"course lnguage dropdown not found: {self.course_level_locator}")
    
    def enter_course_title(self, course_title):
        self.log.info(f"Entering Course Title: {course_title}")
        # `send_keys_element` should handle waiting for visibility/interactability.
        self.send_keys_element(course_title, locator=self.course_title_locator, locatorType="xpath")
        self.log.info("Course Title Entered")
        
    def enter_course_description(self, course_describtion):
        self.log.info(f"Entering course_describtion_locator : {course_describtion}")
        # `send_keys_element` should handle waiting for visibility/interactability.
        self.send_keys_element(course_describtion, locator=self.course_describtion_locator, locatorType="xpath")
        self.log.info("course_describtion_locator Entered")
        
    def enter_course_price(self, course_price):
        self.log.info(f"Entering course_price : {course_price}")
        # `send_keys_element` should handle waiting for visibility/interactability.
        self.send_keys_element(course_price, locator=self.course_price_locator, locatorType="id")
        self.log.info("course_price Entered")
        
    def click_course_category1(self):
        self.log.info("Clicking 'Pay Now' button.")
        # `click_element` will handle waiting for clickability and scrolling.
        self.click_element(locator=self.course_category_2, locatorType="id")
        self.log.info("Successfully clicked 'Pay Now' button.")
        
    def click_course_add_submit(self):
        self.log.info("Clicking 'Pay Now' button.")
        # `click_element` will handle waiting for clickability and scrolling.
        self.click_element(locator=self.submit_adding_of_course, locatorType="xpath")
        self.log.info("Successfully clicked 'Pay Now' button.")

    def enter_course_image_location(self, course_image_location):
        self.log.info(f"Entering Course Title: {course_image_location}")
        # `send_keys_element` should handle waiting for visibility/interactability.
        self.send_keys_element(course_image_location, locator=self.course_image_locator, locatorType="id")
        self.log.info("Course Title Entered")
        
    def enter_course_video_link(self, course_video_link):
        self.log.info(f"Entering Course Title: {course_video_link}")
        # `send_keys_element` should handle waiting for visibility/interactability.
        self.send_keys_element(course_video_link, locator=self.course_video_link_locator, locatorType="id")
        self.log.info("Course Title Entered")

    def add_new_course(self, course_title="", course_describtion="", course_price=0.0, 
                       course_language="",course_level="", 
                       course_image_location = "", course_video_link=""):
        self.click_add_new_course_button()
        self.enter_course_title(course_title)
        self.enter_course_description(course_describtion)
        self.enter_course_price(course_price)
        self.select_course_language(course_language)
        self.click_course_category1()
        self.select_course_level(course_level)
        self.enter_course_image_location(course_image_location)
        self.enter_course_video_link(course_video_link)
        self.click_course_add_submit()
        
    def verify_adding_course_succssed(self):
        """
        Verifies if an enrollment error message is displayed.
        """
        self.log.info("Verifying if enrollment failed message is present.")
        # Using the new isElementVisible which internally uses get_element and handles exceptions
        result = self.is_element_visible(locator=self.successull_adding_course_meesaage, locatorType="xpath")
        self.log.info(f"Enrollment failed message visible: {result}")
        return result
