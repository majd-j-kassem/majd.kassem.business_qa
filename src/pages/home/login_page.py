from selenium.webdriver.common.by import By

class LoginPage(self, driver):
    def __init__(self):
        self.driver = driver 
    def login(self, username, password):
        login_link = self.driver.find_element(By.LINK_TEXT,"Login")
        login_link.click()
        
        email_field = self.driver.find_element(By.ID, "id_username")
        email_field.send_keys("mjdkassem")
        
        password_field = self.driver.find_element(By.ID, "id_password")
        password_field.send_keys("mjd0957708653A")
        
        login_button = self.driver.find_element(By.XPATH, "//button[@class = 'login-button']")
        login_button.click()