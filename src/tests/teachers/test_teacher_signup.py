from utilities.test_status import StatusVerifier
import unittest
import pytest
from pages.home.login_page import LoginPage
from pages.home.home_page import HomePage
from pages.teachers.teacher_signup_page import TeacherSignPage
import os
import time


@pytest.mark.usefixtures("oneTimeSetUp", "setUp")
class TestTeacher(unittest.TestCase):
    
    @pytest.fixture(autouse=True)
    def objectSetup(self, oneTimeSetUp, base_url):
        self.login_page = LoginPage(self.driver, base_url)
        self.home_page = HomePage(self.driver, self.base_url)
        
        self.join_as_teacher_page = TeacherSignPage(self.driver, self.base_url)
        self.ts = StatusVerifier(self.driver, self.base_url)    
        
    @pytest.mark.run(order=1)
    def test_valid_teacher_joining(self):
        
        self.home_page.go_to_teacher_signup_page()
        pending_teacher_email = "pending_teacher_" + str(int(time.time())) + "@kuwaitnet.email"
        pending_teacher_password = "PendingPass123!" # A strong unique password

        self.join_as_teacher_page.teacher_join(full_name_en="Kuwaitnet", full_name_ar="كويت نت", email=pending_teacher_email, 
                                               phone_number="00965957708653", year_of_exp="12", 
                                               university_attend="Damascus University", graduate_year="2009", 
                                               major_study="Math", bio_teacher="We build people mind", 
                                               password="Dinamo12@", password_2="Dinamo12@")
        
        result = self.join_as_teacher_page.verify_joining_succssed()
        self.home_page.go_to_teacher_signup_page()
        self.ts.markFinal("test_invalidEnrollment", result,
                          "Enrollment Failed Verification")

            
    @pytest.mark.run(order=2)
    def test_teacher_login_pending(self):
        self.home_page.go_to_teacher_signup_page()
        pending_teacher_email = "pending_teacher_" + str(int(time.time())) + "@kuwaitnet.email"
        pending_teacher_password = "PendingPass123!" # A strong unique password

        
        time.sleep(1) # Give page time to load

        self.join_as_teacher_page.teacher_join(full_name_en="Pending Teacher", full_name_ar="معلم قيد الانتظار", 
                                               email=pending_teacher_email, 
                                               phone_number="00965957708659", year_of_exp="5", 
                                               university_attend="Cairo University", graduate_year="2015", 
                                               major_study="Chemistry", bio_teacher="Eager to teach", 
                                               password=pending_teacher_password, password_2=pending_teacher_password)
        
       
        
        self.home_page.go_to_home_page()# Assuming you have a method to go to the main login page
        time.sleep(2) # Give page time to load

        
        self.login_page.login(pending_teacher_email, pending_teacher_password)
        time.sleep(3) 
        is_logged_in = self.login_page.verify_login_faild() # Assuming this method exists
        
        assert is_logged_in is True
        
    def screenShot(self, resultMessage):
        """
        Takes a screenshot and saves it to the 'screenshots' directory.
        The filename will include a timestamp and the result message.
        """
        fileName = resultMessage.replace(" ", "_") + "." + str(int(time.time())) + ".png"
        screenshotDirectory = "../screenshots/" # Relative path from utilities/ to screenshots/
        relativeFileName = screenshotDirectory + fileName
        currentDirectory = os.path.dirname(__file__) # Get the directory of the current file
        destinationFile = os.path.join(currentDirectory, relativeFileName)

        try:
            if not os.path.exists(screenshotDirectory):
                os.makedirs(screenshotDirectory)
                self.log.info(f"Created screenshot directory: {screenshotDirectory}")
            self.driver.save_screenshot(destinationFile)
            self.log.error(f"Screenshot taken: {destinationFile}")
        except Exception as e:
            self.log.error(f"Failed to take screenshot: {e}")

        
