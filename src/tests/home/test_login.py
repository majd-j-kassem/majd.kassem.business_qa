from selenium import webdriver
from selenium.webdriver.common.by import By
from pages.home.login_page import LoginPage
import unittest
import time

class TestLogin(unittest.TestCase):
    def test_valid_login(self):
        base_url = "http://127.0.0.1:8000/"
        driver = webdriver.Chrome()
        driver.maximize_window()
        driver.implicitly_wait(5)
        
        driver.get(base_url)
        login_page = LoginPage(driver)
        login_page.login("mjdwassouf", "mjd0957708653A")
        
        logout_link = driver.find_element(By.LINK_TEXT, "Logout")
        time.sleep(5)
        if logout_link is not None:
            print("we Logged in Successfully")
        else:
            print("Loin Faild")