from selenium import webdriver
from selenium.webdriver.common.by import By
from pages.home.login_page import LoginPage
import unittest

class TestLogin(unittest):
    def test_valid_login(self):
        base_url = "https://majd-kassem-business.onrender.com/"
        driver = webdriver.Chrome()
        driver.maximize_window()
        driver.implicitly_wait(3)
        
        driver.get(base_url)
        login_page = LoginPage(driver)
        login_page.login("admin", "admin")
        
        logout_link = driver.find_element(By.LINK_TEXT, "Logout")
        
        if logout_link is not None:
            print("we Logged in Successfully")
        else:
            print("Loin Faild")