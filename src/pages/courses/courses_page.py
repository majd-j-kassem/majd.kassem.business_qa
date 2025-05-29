from selenium.webdriver.common.by import By
from base.selenium_driver import SeleniumDriver
from selenium.webdriver.support.ui import Select
import utilities.custome_logger as cl
import logging

class CoursesPage(SeleniumDriver):
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver 
    ################
    ### Locators ###
    ################
    search_box = ""
    course_name = "//h2[contains(text(),'DevOps: Introduction to Developer Operations Speci')]"
    all_courses = "//div[@class='course-card']"
    view_course_details_button = "//div[@class='courses-page-container']//div[4]//a[1]"
    enroll_button = "//button[normalize-space()='Register for Course']"
    card_number_input = "//input[@id='id_card_number']"
    card_expiry_month_selector = "//select[@id='id_expiry_month']"
    card_expiry_year_selector = "//select[@id='id_expiry_year']"
    pay_button = "//button[normalize-space()='Pay Now']"
    enroll_error_message = "//div[@role='alert']"
    ############################
    ### Element Interactions ###
    ############################
    def enterCourseName(self, name):
        print()
    def selectCourseToEnroll(self, fullCourseName):
        self.click_element(fullCourseName, locatorType="xpath")

    def view_course_details(self):
        self.click_element(locator=self.view_course_details_button,locatorType="xpath") 

    ############## Card Info Function#######################################################
    def enter_card_num(self, card_num):
        self.send_keys_element(card_num, locator=self.card_number_input, locatorType="xpath")

    def select_expiry_month(self, card_exp_mont):
        month_dropdown_element = self.get_element(locator=self.card_expiry_month_selector,
                                                  locatorType="xpath")
        select= Select(month_dropdown_element)
        select.select_by_value(str(card_exp_mont))
    
    def select_expiry_year(self, card_exp_year):
        year_dropdown_element = self.get_element(locator=self.card_expiry_year_selector,
                                                  locatorType="xpath")
        select= Select(year_dropdown_element)
        select.select_by_value(str(card_exp_year))
    ############################################################################################
    def click_pay_button(self):
        self.click_element(locator=self.pay_button, locatorType="xpath")

    def enter_credit_card_info(self,card_num, card_exp_mont, card_exp_year):
        self.enter_card_num(card_num)
        self.select_expiry_month(card_exp_mont)
        self.select_expiry_year(card_exp_year)

    def enroll_course(self,card_num="", card_exp_mont="", card_exp_year=""):
