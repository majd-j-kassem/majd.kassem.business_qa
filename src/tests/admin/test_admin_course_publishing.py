from utilities.test_status import StatusVerifier
import unittest
import pytest
from pages.home.login_page import LoginPage
from pages.home.home_page import HomePage
from pages.teachers.teacher_signup_page import TeacherSignPage
from pages.teachers.add_course_page import CourseAddingPage
from pages.admin.admin_login_page import AdminLoginPage
from pages.admin.admin_dashboard_page import AdminDashboardPage
import time


@pytest.mark.usefixtures("oneTimeSetUp", "setUp")
class TestAdminCoursePublishing(unittest.TestCase):

    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "admin"

    APPROVED_TEACHER_EMAIL = "asdfs"
    APPROVED_TEACHER_PASSWORD = "Dinamo12@"
    
    
    @pytest.fixture(autouse=True)
    def objectSetup(self, oneTimeSetUp, base_url_from_cli):
        self.base_url = base_url_from_cli
        self.login_page = LoginPage(self.driver, self.base_url)
        self.login_page.login(self.APPROVED_TEACHER_EMAIL, self.APPROVED_TEACHER_PASSWORD)
        self.home_page = HomePage(self.driver, self.base_url)
        self.course_page = CourseAddingPage(self.driver, self.base_url)
        self.admin_login_page = AdminLoginPage(self.driver, self.base_url)
        self.admin_dashboard_page = AdminDashboardPage(self.driver, self.base_url)
        
    
        
    @pytest.mark.run(order=1)
    def test_valid_course_added(self):
        
        self.home_page.go_to_Teacher_Dashboard_page()
        course_name = "testing_course" + str(int(time.time()))
        course_description  = "We are adding random course for testing !" + str(int(time.time())) # A strong unique password
        course_price = int(time.time()/100000)
        course_language = "English"
        course_level = "Advanced"
        course_image_link = "/home/majd/Documents/Majd-Personal-Work/majd.kassem.business_qa/images/student_1.jpg"
        course_video_link = "https://www.google.co.uk/"
        
        
        self.course_page.add_new_course(course_name,course_description,course_price,
                                         course_language,course_level, course_image_link, course_video_link)
        
       
        result = self.course_page.verify_adding_course_succssed()
        teacher_logout_success = self.login_page.logout()
        self.course_name_to_publish = course_name
        print(f"Navigating to Admin Login Page: {self.course_name_to_publish}")


        admin_login_success = self.admin_login_page.admin_login(self.ADMIN_USERNAME, self.ADMIN_PASSWORD)
        result_navigate = self.admin_dashboard_page.navigate_to_teacher_courses_page()
       
        result_select_checkbox = self.admin_dashboard_page.select_course_checkbox(course_name)
        result_select_action = self.admin_dashboard_page.select_action_from_dropdown("Mark selected as Published (Available to Customers)")
        result_click_go = self.admin_dashboard_page.click_go_button()
        
        

         # Give some time for the action to process and page to reload after publish
        time.sleep(3) 

        # 7. Verify the course is now "published = true" in the admin panel (green icon/text)
        final_admin_status = self.admin_dashboard_page.get_course_published_status(course_name)
        print(f"final_admin_status: {final_admin_status}")
        self.admin_login_page.logout()

        # 8. Admin logout is handled by methodSetUp tearDown.

        # 9. Verify on Homepage (public view)
        time.sleep(2) 
        self.login_page = LoginPage(self.driver, self.base_url)
        
        self.login_page.login(self.ADMIN_USERNAME, self.ADMIN_PASSWORD)
        time.sleep(2) 
        self.home_page.go_to_course_page()
        
        # Verify course presence on homepage
        # Give the homepage a moment to load and render updated course list
        
        course_visible_on_homepage = self.home_page.is_course_visible_on_homepage(course_name)
        assert course_visible_on_homepage is True

       

            
    