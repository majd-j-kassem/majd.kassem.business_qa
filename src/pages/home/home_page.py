from selenium.webdriver.common.by import By
from base.selenium_driver import SeleniumDriver
import utilities.custome_logger as cl
import logging
from pages.courses.courses_page import CoursesPage

class HomePage(SeleniumDriver):
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver 
    # Locators for elements on the home page (e.g., navigation links)
    log = cl.CustomLogger(logging.DEBUG)
    ################
    ### Locators ###
    ################
    course_menu_link = "//a[normalize-space()='Courses']"
    ############################
    ### Element Interactions ###
    ############################
    
    
    def go_to_course_page(self):
        self.click_element(self.course_menu_link, locatorType="xpath")
        #return CoursesPage(self.driver)