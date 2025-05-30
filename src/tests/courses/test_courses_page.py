from pages.courses.courses_page import CoursesPage
from utilities.test_status import StatusVerifier
import unittest
import pytest
from pages.home.login_page import LoginPage
from pages.home.home_page import HomePage
import time




@pytest.mark.usefixtures("oneTimeSetUp", "setUp")
class RegisterCoursesTests(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def objectSetup(self, oneTimeSetUp):
        self.login_page = LoginPage(self.driver)
        self.login_page.login("ali", "Dinamo12@")
        time.sleep(3)
        self.home_page = HomePage(self.driver)
        self.home_page.go_to_course_page()
        time.sleep(3)
        self.courses_page = CoursesPage(self.driver)
        self.ts = StatusVerifier(self.driver)
        
        

    #@pytest.mark.run(order=1)
    @pytest.mark.nondestructive
    def test_invalidEnrollment(self):
        #self.courses.enterCourseName("JavaScript")
        #self.courses.selectCourseToEnroll("JavaScript for beginners")
        self.courses_page.enroll_course(card_num="1234", card_exp_month="1", card_exp_year="2026")
        result = self.courses_page.verifyEnrollFailed()
        self.ts.markFinal("test_invalidEnrollment", result,
                          "Enrollment Failed Verification")