from selenium import webdriver
from selenium.webdriver.common.by import By
from pages.home.login_page import LoginPage
import unittest
import time
import pytest

@pytest.mark.usefixtures("oneTimeSetUp", "setUp")
class TestLogin(unittest.TestCase):
    
    @pytest.fixture(autouse=True)
    def classSetup(self, oneTimeSetUp, base_url_from_cli):
        self.base_url = base_url_from_cli
        self.driver = oneTimeSetUp
        self.login_page = LoginPage(self.driver, self.base_url)
        self.base_url = self.base_url 
    
    
    @pytest.mark.run(order = 2)
    def test_valid_login(self):
        self.login_page.login("admin", "admin")
        result = self.login_page.verify_login_success_appearnce()
        assert result is True
                
    @pytest.mark.run(order = 1)        
    def test_invalid_login(self):
        self.login_page.login("mjdwassouf", "mjd095770865a")
        result = self.login_page.verify_login_faild()
        assert result is True