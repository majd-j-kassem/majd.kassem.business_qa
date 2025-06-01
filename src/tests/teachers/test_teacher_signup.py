from utilities.test_status import StatusVerifier
import unittest
import pytest
from pages.home.login_page import LoginPage
from pages.home.home_page import HomePage
from pages.teachers.teacher_signup_page import TeacherSignPage

import time




@pytest.mark.usefixtures("oneTimeSetUp", "setUp")
class TestTeacher(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def objectSetup(self, oneTimeSetUp, base_url):
        #self.login_page = LoginPage(self.driver)
        #self.login_page.login("ali", "Dinamo12@")
        time.sleep(3)
        self.home_page = HomePage(self.driver, self.base_url)
        self.home_page.go_to_teacher_signup_page()
        time.sleep(3)
        self.join_as_teacher_page = TeacherSignPage(self.driver, self.base_url)
        self.ts = StatusVerifier(self.driver, self.base_url)
        

    #@pytest.mark.run(order=1)
    @pytest.mark.nondestructive
    def test_valid_teacher_joining(self):
        #self.courses.enterCourseName("JavaScript")
        #self.courses.selectCourseToEnroll("JavaScript for beginners")
        self.join_as_teacher_page.teacher_join(full_name_en="Kuwaitnet", full_name_ar="كويت نت", email="mjd.kassem+1@kuwaitnet.email", 
                                               phone_number="00965957708653", year_of_exp="12", 
                                               university_attend="Damascus University", graduate_year="2009", 
                                               major_study="Math", bio_teacher="We build people mind", 
                                               password="Dinamo12@", password_2="Dinamo12@")
        
        result = self.join_as_teacher_page.verify_joining_succssed()
        self.ts.markFinal("test_invalidEnrollment", result,
                          "Enrollment Failed Verification")
        
    @pytest.mark.nondestructive
    def test_teacher_login_pending(self):
        
        pending_teacher_email = "pending_teacher_" + str(int(time.time())) + "@kuwaitnet.email"
        pending_teacher_password = "PendingPass123!" # A strong unique password

        
        # Navigate back to teacher signup page if not already there from previous test
        self.driver.get(self.home_page.base_url) # Go back to base URL
        self.home_page.go_to_teacher_signup_page() # Navigate to signup page
        time.sleep(2) # Give page time to load

        self.join_as_teacher_page.teacher_join(full_name_en="Pending Teacher", full_name_ar="معلم قيد الانتظار", 
                                               email=pending_teacher_email, 
                                               phone_number="00965957708659", year_of_exp="5", 
                                               university_attend="Cairo University", graduate_year="2015", 
                                               major_study="Chemistry", bio_teacher="Eager to teach", 
                                               password=pending_teacher_password, password_2=pending_teacher_password)
        
        # Verify signup success first (this means the account is created, but not necessarily approved)
        signup_result = self.join_as_teacher_page.verify_joining_succssed()
        self.ts.mark("test_teacher_login_pending - Signup", signup_result, "Signup for pending teacher failed.")
        assert signup_result, "Failed to sign up the teacher account for pending login test."

        self.driver.get(self.login_page.base_url) # Go back to base URL to get to the main login
        self.home_page.go_to_login_page() # Assuming you have a method to go to the main login page
        time.sleep(2) # Give page time to load

        
        self.login_page.login(pending_teacher_email, pending_teacher_password)
        time.sleep(3) 
        is_logged_in = self.login_page.verify_login_successful() # Assuming this method exists
        
        error_message_text = self.login_page.get_login_error_message() # Implement this method in LoginPage
        
        expected_error_keywords = ["pending", "approval", "not active", "disabled"]
        is_error_message_present = any(keyword in error_message_text.lower() for keyword in expected_error_keywords)
        
        self.ts.markFinal("test_teacher_login_pending", not is_logged_in and is_error_message_present,
                          "Pending teacher login test failed: Either logged in or wrong error message.")
        
        assert not is_logged_in, "Pending teacher was able to log in successfully!"
        assert is_error_message_present, f"Expected pending/approval error message, but got: '{error_message_text}'"
        
        log.info(f"Test 'test_teacher_login_pending' passed: Pending teacher '{pending_teacher_email}' could not log in as expected.")

