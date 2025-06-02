from utilities.test_status import StatusVerifier
import unittest
import pytest
from pages.home.login_page import LoginPage
from pages.home.home_page import HomePage
from pages.teachers.teacher_signup_page import TeacherSignPage
from pages.teachers.add_course_page import CourseAddingPage

import time


@pytest.mark.usefixtures("oneTimeSetUp", "setUp")
class TestTeacher(unittest.TestCase):
    APPROVED_TEACHER_EMAIL = "asdfs"
    APPROVED_TEACHER_PASSWORD = "Dinamo12@"
    @pytest.fixture(autouse=True)
    def objectSetup(self, oneTimeSetUp, base_url):
        self.login_page = LoginPage(self.driver, base_url)
        self.login_page.login(self.APPROVED_TEACHER_EMAIL, self.APPROVED_TEACHER_PASSWORD)
        self.home_page = HomePage(self.driver, self.base_url)
        
        self.course_page = CourseAddingPage(self.driver, base_url)
    
        
    @pytest.mark.run(order=1)
    def test_valid_course_added(self):
        
        self.home_page.go_to_Teacher_Dashboard_page()
        course_name = "testing_course" + str(int(time.time()))
        course_description  = "We are adding random course for testing !" + str(int(time.time())) # A strong unique password
        course_price = int(time.time() / 1000000)
        course_language = "English"
        course_level = "Advanced"
        course_image_link = "/home/majd/Documents/Majd-Personal-Work/majd.kassem.business_qa/images/student_1.jpg"
        course_video_link = "https://www.google.co.uk/"
        
        
        self.course_page.add_new_course(course_name,course_description,course_price,
                                         course_language,course_level, course_image_link, course_video_link)
        
       
        result = self.course_page.verify_adding_course_succssed()
        assert result is True

            
    