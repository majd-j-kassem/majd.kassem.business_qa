from selenium.webdriver.common.by import By
from base.selenium_driver import SeleniumDriver

class LoginPage(SeleniumDriver):
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver 
    #Locator
    login_locator = "Login"
    email_loctor = "id_username"
    password_locator = "id_password"
    login_button_locator = "//button[@class = 'login-button']"
    
    def click_login_link(self):
        self.click_element(self.login_locator, locatorType="linktext")
    def enter_username(self, username):
        self.send_keys_element(username, self.email_loctor, locatorType="id")
    def enter_password(self, password):
        self.send_keys_element(password, self.password_locator, locatorType="id")
    def click_login_button(self):
        self.click_element(self.login_button_locator, locatorType="xpath")
        
    def login(self, username, password):
        self.click_login_link()
        self.enter_username(username)
        self.enter_password(password)
        self.click_login_button()