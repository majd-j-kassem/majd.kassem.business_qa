from selenium.webdriver.common.by import By
from base.selenium_driver import SeleniumDriver
import utilities.custome_logger as cl
import logging

class LoginPage(SeleniumDriver):
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver 

    log = cl.customLogger(logging.DEBUG)
    ################
    ### Locators ###
    ################
    login_locator = "Login"
    email_loctor = "id_username"
    password_locator = "id_password"
    login_button_locator = "//button[@class = 'login-button']"
    logout_locator = "Logout"
    error_message_login_locator = "//li[@class='error approval-message']"

    ############################
    ### Element Interactions ###
    ############################
    
    def click_login_link(self):
        self.click_element(self.login_locator, locatorType="linktext")
    def enter_username(self, username):
        self.send_keys_element(username, self.email_loctor, locatorType="id")
    def enter_password(self, password):
        self.send_keys_element(password, self.password_locator, locatorType="id")
    def click_login_button(self):
        self.click_element(self.login_button_locator, locatorType="xpath")
        
    def login(self, username="", password=""):
        self.click_login_link()
        self.clear_fields()
        self.enter_username(username)
        self.enter_password(password)
        self.click_login_button()
    
    def verify_login_success(self):
        is_logged_in = self.isElementPresent(self.logout_locator, locatorType="linktext")
        return is_logged_in
    def verify_login_success_appearnce(self):
        # Use isElementVisible for Logout link, indicating it's truly ready
        # Give it a generous timeout for network latency on Render
        is_logged_in = self.isElementVisible(self.logout_locator, locatorType="linktext", timeout=20)
        if is_logged_in:
            self.log.info("Login successful: Logout link is visible.")
        else:
            self.log.error("Login failed: Logout link is NOT visible.")
        return is_logged_in
    def verify_login_faild(self):
        is_not_logged_in = self.isElementPresent(self.error_message_login_locator, locatorType="xpath")
        return is_not_logged_in
    def clear_fields(self):
        email_field = self.get_element(self.email_loctor, locatorType="id")
        email_field.clear()
        email_password = self.get_element(self.password_locator, locatorType="id")
        email_password.clear()
        

    #Retrive HTML5 Validation Message for Null Login check later  
    def get_username_validation_message(self):
        """
        Retrieves the HTML5 validation message for the username input field.
        """
        username_field = self.driver.find_element(*self.email_loctor)
        # Check if the element has a validation message
        if username_field.get_attribute("validationMessage"):
            return username_field.get_attribute("validationMessage")
        else:
            return "" # Return empty string if no message is displayed