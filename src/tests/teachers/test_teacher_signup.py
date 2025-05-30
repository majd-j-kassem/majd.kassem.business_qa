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
    def objectSetup(self, oneTimeSetUp):
        #self.login_page = LoginPage(self.driver)
        #self.login_page.login("ali", "Dinamo12@")
        time.sleep(3)
        self.home_page = HomePage(self.driver)
        self.home_page.go_to_teacher_signup_page()
        time.sleep(3)
        self.join_as_teacher_page = TeacherSignPage(self.driver)
        self.ts = StatusVerifier(self.driver)
        
        

    #@pytest.mark.run(order=1)
    @pytest.mark.nondestructive
    def test_valid_teacher_joining(self):
        #self.courses.enterCourseName("JavaScript")
        #self.courses.selectCourseToEnroll("JavaScript for beginners")
        self.join_as_teacher_page.teacher_join(full_name_en="Kuwaitnet", full_name_ar="كويت نت", email="mjd.kassem@kuwaitnet.email", 
                                               phone_number="00965957708653", year_of_exp="12", 
                                               university_attend="Damascus University", graduate_year="2009", 
                                               major_study="Math", bio_teacher="We build people mind", 
                                               password="Dinamo12@", password_2="Dinamo12@")
        
        result = self.join_as_teacher_page.verify_joining_succssed()
        self.ts.markFinal("test_invalidEnrollment", result,
                          "Enrollment Failed Verification")