from selenium.webdriver.common.by import By
from base.selenium_driver import SeleniumDriver
import utilities.custome_logger as cl
import logging

class SignupPage(SeleniumDriver):
    def __init__(self, driver, base_url):
        super().__init__(driver, base_url)
        self.driver = driver        

        self.login_link_locator = "//a[normalize-space()='Login']"
        self.email_input_loctor = "id_username"
        self.password_input_locator = "id_password"
        self.login_button_locator = "//button[normalize-space()='Login']"
        self.logout_link_locator = "//a[normalize-space()='Logout']"
        self.error_message_login_locator = "//li[@class='error approval-message']"

        ############### For Studend ------------------------------------------------
        self.user_name_input_locator   =   "//input[@id='id_username']"
        self.user_emil_imput_locator   =   "//input[@id='id_email']"
        self.user_full_name_en_locator = "//input[@id='id_full_name_en']"
        self.user_full_name_ar_locator = "//input[@id='id_full_name_en']"
        self.user_password_input_locator = "//input[@id='id_password1']"
        self.user_password_input_locator2 ="//input[@id='id_password2']"
        self._user_profile_image_input_locator = "//input[@id='id_profile_picture']"
        self.user_bio_input_locator = "//textarea[@id='id_bio']"
        self.signup_link_locator = "//a[normalize-space()='Sign Up']"
        self.submitt_button_locator = "//button[@type='submit']"
        
        #---------------------------------------------------------
    ############################

    def click_login_link(self):
        self.click_element(self.login_link_locator, locatorType="xpath")

    def click_signup_link(self):
        self.click_element(self.signup_link_locator, locatorType="xpath")

    def enter_username(self, username):
        self.send_keys_element(username, self.user_name_input_locator, locatorType="xpath")

    def enter_email(self, email):
        self.send_keys_element(email, self.user_emil_imput_locator, locatorType="xpath")

    def enter_full_name_ar(self, full_name_ar):
        self.send_keys_element(full_name_ar, self.user_full_name_ar_locator, locatorType="xpath")

    def enter_full_name_en(self, full_name_en):
        self.send_keys_element(full_name_en, self.user_full_name_en_locator, locatorType="xpath")

    def enter_password(self, password):
        self.send_keys_element(password, self.user_password_input_locator, locatorType="xpath")

    def enter_password_2(self, password_2):
        self.send_keys_element(password_2, self.user_password_input_locator2, locatorType="xpath")

    def enter_user_profile_image(self, profile_image):
        self.send_keys_element(profile_image, self._user_profile_image_input_locator, locatorType="xpath")

    def enter_bio(self, bio):
        self.send_keys_element(bio, self.user_bio_input_locator, locatorType="xpath")

    def cick_signup_button(self):
        self.click_element(self.submitt_button_locator, locatorType="xpath")




    def signup_student(self, username="", email="", full_name_ar="", full_name_en="",
                       password="", password_2="", profile_image="",
                       bio=""):
        self.click_login_link()
        self.click_signup_link()
        self.enter_username(username)
        self.enter_email(email)
        self.enter_username(username)
        self.enter_full_name_en(full_name_en)
        self.enter_full_name_ar(full_name_ar)
       
        self.enter_password(password)
        self.enter_password_2(password_2)
        self.enter_user_profile_image(profile_image)
        self.enter_bio(bio)
        self.cick_signup_button()
        
    