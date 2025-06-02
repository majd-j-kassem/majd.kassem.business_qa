import pytest
import time
import logging
import random # For generating unique course names

# Import necessary Page Objects
from pages.admin.admin_login_page import AdminLoginPage
from pages.admin.admin_dashboard_page import AdminDashboardPage # This is your updated file
from pages.home.login_page import LoginPage
from pages.teachers.add_course_page import CourseAddingPage
from pages.home.home_page import HomePage # For final verification on homepage

# Import base classes and utilities
from base.selenium_driver import SeleniumDriver # Your base driver class
from utilities.test_status import StatusVerifier # Your test status verifier

# Get the logger for this module
log = logging.getLogger(__name__)

@pytest.mark.usefixtures("oneTimeSetUp", "setUp")
class TestAdminCoursePublishing:

    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "admin"
    # IMPORTANT: Ensure this teacher exists in your system and is already approved.
    # If not, you'd need another pre-condition (e.g., creating and approving a teacher).
    APPROVED_TEACHER_EMAIL = "asdf"
    APPROVED_TEACHER_PASSWORD = "Dinamo12@"

    @pytest.fixture(autouse=True)
    def objectSetup(self, oneTimeSetUp, base_url):
        """
        Initializes the WebDriver and all necessary Page Objects for the test class.
        This fixture runs once per test class.
        """
        
        log.info("TestAdminCoursePublishing: classSetup starting...")

        # Initialize all necessary page objects and StatusVerifier
        self.admin_login_page = AdminLoginPage(self.driver, base_url)
        self.admin_dashboard_page = AdminDashboardPage(self.driver, base_url)
        self.login_page = LoginPage(self.driver, base_url)
        self.course_page = CourseAddingPage(self.driver, base_url)
        self.home_page = HomePage(self.driver, base_url)
        # Initialize StatusVerifier with the driver for logging and screenshots
        ts = StatusVerifier(self.driver, base_url)

    @pytest.mark.run(order=1) # You can use pytest-ordering if you need specific order, otherwise remove
    def test_admin_publishes_course(self):
        """
        Tests the administrative flow to publish a pending course.
        Steps:
        1. Log in as admin (handled by methodSetUp).
        2. Navigate to Teacher Courses / Course Management section.
        3. Verify initial "published = false" status for the newly created course.
        4. Select the course's checkbox.
        5. Select "Mark selected as publish" from the action dropdown.
        6. Click the "Go" button.
        7. Verify the course is now "published = true" in the admin panel.
        8. Log out from admin.
        9. Verify the course is visible on the public homepage.
        """
        course_name = f"Automation Course {random.randint(10000, 99999)}"
        course_description  = "We are adding random course for testing !" + str(int(time.time())) # A strong unique password
        course_price = int(time.time() / 1000000)
        course_language = "English"
        course_level = "Advanced"
        course_image_link = "/home/majd/Documents/Majd-Personal-Work/majd.kassem.business_qa/images/student_1.jpg"
        course_video_link = "https://www.google.co.uk/"
        
        log.info(f"Pre-condition: Attempting to create pending course '{course_name}' via teacher.")
        self.login_page.login(self.APPROVED_TEACHER_EMAIL, self.APPROVED_TEACHER_PASSWORD)
        time.sleep(1)
        self.home_page.go_to_Teacher_Dashboard_page()
        self.course_page.add_new_course(course_name,course_description,course_price,
                                         course_language,course_level, course_image_link, course_video_link)
               
        teacher_logout_success = self.login_page.logout()
       
        self.course_name_to_publish = course_name # Store the unique course name for the test method

        log.info(f"Starting test_admin_publishes_course for course: {self.course_name_to_publish}")

        # 1. Admin login is handled by methodSetUp.
        admin_login_success = self.admin_login_page.admin_login(self.ADMIN_USERNAME, self.ADMIN_PASSWORD)
        # 2. Access Teacher Courses / Course Management section
        result_navigate = self.admin_dashboard_page.navigate_to_teacher_courses_page()
        self.ts.mark(result_navigate, "Navigated to Teacher Courses page.")
        assert result_navigate, "Test failed: Could not navigate to Teacher Courses page."
        
        # 3. Verify initial "published = false" status (red icon/text)
        # Give a moment for the list to load if it's dynamic
        time.sleep(1) 
        initial_status = self.admin_dashboard_page.get_course_published_status(self.course_name_to_publish)
        self.ts.mark(initial_status == "False",
                     f"Initial published status for '{self.course_name_to_publish}' is 'False'.")
        assert initial_status == "False", \
            f"Test failed: Course '{self.course_name_to_publish}' initial status is not 'False'."

        # 4. Select the course checkbox
        result_select_checkbox = self.admin_dashboard_page.select_course_checkbox(self.course_name_to_publish)
        self.ts.mark(result_select_checkbox, f"Checkbox selected for course '{self.course_name_to_publish}'.")
        assert result_select_checkbox, \
            f"Test failed: Could not select checkbox for course '{self.course_name_to_publish}'."

        # 5. Select "Mark selected as publish" from action dropdown
        result_select_action = self.admin_dashboard_page.select_action_from_dropdown("Mark selected as publish")
        self.ts.mark(result_select_action, "Selected 'Mark selected as publish' from dropdown.")
        assert result_select_action, "Test failed: Could not select 'Mark selected as publish' action."

        # 6. Click "Go" button
        result_click_go = self.admin_dashboard_page.click_go_button()
        self.ts.mark(result_click_go, "Clicked 'Go' button.")
        assert result_click_go, "Test failed: Could not click 'Go' button."

        # Give some time for the action to process and page to reload after publish
        time.sleep(3) 

        # 7. Verify the course is now "published = true" in the admin panel (green icon/text)
        final_admin_status = self.admin_dashboard_page.get_course_published_status(self.course_name_to_publish)
        self.ts.mark(final_admin_status == "True",
                     f"Final published status for '{self.course_name_to_publish}' is 'True' in admin panel.")
        assert final_admin_status == "True", \
            f"Test failed: Course '{self.course_name_to_publish}' final status is not 'True' in admin panel."

        log.info(f"Course '{self.course_name_to_publish}' successfully published by admin.")

        # 8. Admin logout is handled by methodSetUp tearDown.

        # 9. Verify on Homepage (public view)
        self.home_page.navigate_to_home_page()
        self.ts.mark(True, "Navigated to homepage for final verification.") # Always mark navigation as True unless it throws exception
        
        # Verify course presence on homepage
        # Give the homepage a moment to load and render updated course list
        time.sleep(2) 
        course_visible_on_homepage = self.home_page.is_course_visible_on_homepage(self.course_name_to_publish)
        
        # Final assertion using StatusVerifier's markFinal
        self.ts.markFinal("test_admin_publishes_course", course_visible_on_homepage,
                         f"Course '{self.course_name_to_publish}' is visible on homepage after publishing.")

        log.info("Test test_admin_publishes_course completed.")