from selenium.webdriver.common.by import By
from base.selenium_driver import SeleniumDriver
import utilities.custome_logger as cl
import logging

class LoginPage(SeleniumDriver):
    def __init__(self, driver, base_url):
        super().__init__(driver, base_url)
        self.driver = driver        

    log = cl.CustomLogger(logging.DEBUG)
    ################
    ### Locators ###
    ################
    login_link_locator = "//a[normalize-space()='Login']"
    email_input_loctor = "id_username"
    password_input_locator = "id_password"
    login_button_locator = "//button[normalize-space()='Login']"
    logout_link_locator = "//a[normalize-space()='Logout']"
    error_message_login_locator = "//li[@class='error approval-message']"
    ############################
    ### Element Interactions ###
    ############################
    
    def click_login_link(self):
        self.click_element(self.login_link_locator, locatorType="xpath")
    def enter_username(self, username):
        self.send_keys_element(username, self.email_input_loctor, locatorType="id")
    def enter_password(self, password):
        self.send_keys_element(password, self.password_input_locator, locatorType="id")
    def click_login_button(self):
        self.click_element(self.login_button_locator, locatorType="xpath")
    
    def click_logout_link(self):
        self.click_element(self.logout_link_locator, locatorType="xpath")
        
    def login(self, username="", password=""):
        self.click_login_link()
        self.clear_fields()
        self.enter_username(username)
        self.enter_password(password)
        self.click_login_button()
        
    def logout(self):
        self.click_logout_link()
       
    
    def verify_login_success(self):
        is_logged_in = self.isElementPresent(self.logout_link_locator, locatorType="xpath")
        return is_logged_in
    def verify_login_success_appearnce(self):
        # Use isElementVisible for Logout link, indicating it's truly ready
        # Give it a generous timeout for network latency on Render
        is_logged_in = self.is_element_visible(self.logout_link_locator, locatorType="xpath", timeout=20)
        if is_logged_in:
            self.log.info("Login successful: Logout link is visible.")
        else:
            self.log.error("Login failed: Logout link is NOT visible.")
        return is_logged_in
    
    def verify_login_faild(self):
        is_not_logged_in = self.is_element_present(self.error_message_login_locator, locatorType="xpath")
        return is_not_logged_in
    
    def verify_logout_success(self):
        is_not_logged_out = self.is_element_present(self.login_button_locator, locatorType="xpath")
        return is_not_logged_out
    
    
    def clear_fields(self):
        email_field = self.get_element(self.email_input_loctor, locatorType="id")
        email_field.clear()
        email_password = self.get_element(self.password_input_locator, locatorType="id")
        email_password.clear()
        

   