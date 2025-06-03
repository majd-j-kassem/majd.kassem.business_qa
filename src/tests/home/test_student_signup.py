from selenium import webdriver
from selenium.webdriver.common.by import By
from pages.home.login_page import LoginPage
from pages.home.signup_student_page import SignupPage
from pages.home.home_page import HomePage

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
        self.student_signup_page = SignupPage(self.driver, self.base_url)
        self.home_page = HomePage(self.driver, self.base_url)

        self.username = "test_user" + str(int(time.time()))
        self.email= "test_user_email" + str(int(time.time())) + "@kuwaitnet.email"
        self.full_ar_name= "test_user_ar_name" + str(int(time.time()))
        self.full_en_name= "test_user_aen_name" + str(int(time.time()))
        self.user_password = "Dinamo12@"
        self.user_password_2 = "Dinamo12@"
        self.user_profile = "/home/majd/Documents/myproject/majd.kassem.business_qa/images/user.jpg"
        self.user_bio = "test_user_bio" +  str(int(time.time()))

        self.home_page.go_to_home_page()
        

    
    @pytest.mark.run(order = 1)
    def test_valid_student_signup(self):
        self.student_signup_page.signup_student(self.username, self.email, self.full_ar_name,
                                                self.full_en_name, self.user_password,
                                                self.user_password_2, self.user_profile,
                                                self.user_bio)
        
        self.home_page.go_to_home_page()
        self.login_page.login(self.username, self.user_password)
        result = self.login_page.verify_login_success()
        assert result is True
        
