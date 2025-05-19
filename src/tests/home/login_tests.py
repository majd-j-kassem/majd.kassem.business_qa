from selenium import webdriver
from selenium.webdriver.common.by import By


class TestLogin():
    def test_valid_login(self):
        base_url = "https://majd-kassem-business.onrender.com/"
        driver = webdriver.Chrome()
        driver.maximize_window()
        driver.implicitly_wait(3)
        
        driver.get(base_url)
        login_link = driver.find_element(By.LINK_TEXT,"Login")
        login_link.click()
        
        email_field = driver.find_element(By.ID, "id_username")
        email_field.send_keys("mjdkassem")
        
        password_field = driver.find_element(By.ID, "id_password")
        password_field.send_keys("mjd0957708653A")
        
        login_button = driver.find_element(By.XPATH, "//button[@class = 'login-button']")
        login_button.click()
        
        logout_link = driver.find_element(By.LINK_TEXT, "Logout")
        
        if logout_link is not None:
            print("we Logged in Successfully")
        else:
            print("Loin Faild")
ff = TestLogin()
ff.test_valid_login()