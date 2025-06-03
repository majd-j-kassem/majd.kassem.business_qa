import pytest
import time
import logging
import unittest
from pages.admin.admin_login_page import AdminLoginPage
from pages.admin.admin_dashboard_page import AdminDashboardPage
from base.selenium_driver import SeleniumDriver
from pages.teachers.teacher_signup_page import TeacherSignPage
from pages.home.login_page import LoginPage
from pages.home.home_page import HomePage
import random


@pytest.mark.usefixtures("oneTimeSetUp", "setUp")
class TestAdminDashboardFeatures(unittest.TestCase):

    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "admin"
    PENDING_TEACHER_EMAIL = "teacher1" # Ensure this email exists and is in a 'pending' state for the test
    commission_value = "42"
    # classSetup will now return a tuple of initialized page objects
    @pytest.fixture(autouse=True)
    def objectSetup(self, oneTimeSetUp, base_url_from_cli):
        
        self.base_url = base_url_from_cli
        self.join_as_teacher_page = TeacherSignPage(self.driver, self.base_url)

        self.admin_login_page = AdminLoginPage(self.driver, self.base_url)
        self.admin_dashboard_page = AdminDashboardPage(self.driver, self.base_url)
    
        self.home_page = HomePage(self.driver, self.base_url)
        self.loginpage = LoginPage(self.driver, self.base_url)
        self.join_as_teacher_page = TeacherSignPage(self.driver, self.base_url)
        self.loginpage = LoginPage(self.driver, self.base_url)


    @pytest.mark.run(order=1)
    def test_admin_approves_pending_teacher(self):
        
        self.home_page.go_to_teacher_signup_page()
        
        timestamp_suffix = str(int(time.time() * 1000))[-4:]
        random_suffix = random.randint(1, 999)
        unique_id = f"{timestamp_suffix}{random_suffix}"
        pending_teacher_email = f"P_Teacher_{unique_id}@kuwaitnet.email"
        username_login = f"P_Teacher_{unique_id}"
        #pending_teacher_email = "pending_teacher_" + str(int(time.time())) + "@kuwaitnet.email"
        pending_teacher_password = "Dinamo12@" # A strong unique password

       # 1. Teacher Signup
        self.join_as_teacher_page.teacher_join(
            full_name_en="Kuwaitnet",
            full_name_ar="كويت نت",
            email=pending_teacher_email,
            phone_number="00965957708653",
            year_of_exp="12",
            university_attend="Damascus University",
            graduate_year="2009",
            major_study="Math",
            bio_teacher="We build people mind",
            password=pending_teacher_password,
            password_2=pending_teacher_password,
        )
        self.join_as_teacher_page.verify_joining_succssed()

        # 2. Admin Login
        self.admin_login_page.admin_login(self.ADMIN_USERNAME, self.ADMIN_PASSWORD)

        # 3. Admin Approves Teacher
        self.admin_dashboard_page.navigate_to_user_management()
        self.admin_dashboard_page.change_user_status_and_commission(
            pending_teacher_email, commission_value=self.commission_value
        )
        time.sleep(5) # A short pause after approval, just in case of backend latency

        # 4. Admin Logout
        self.admin_login_page.logout()
         # Navigate back to base URL after logout

        # 5. DUMMY LOGIN TO TRIGGER ACTIVATION / CLEAR STATE (NEW STEP)
        # Use a known, reliable account for this, e.g., a student or even admin again.
        # This simulates what you found manually.
        # For example, create a dummy student account if you have one, or just re-login as admin.
        
        # Option A: Re-login as Admin (briefly)
        #self.loginpage.login(self.ADMIN_USERNAME, self.ADMIN_PASSWORD)

        #time.sleep(2) # Short pause
        #self.loginpage.logout() # Logout the admin again
        

        # Option B: Use a dummy student account (if your app has one)
        # dummy_student_email = "dummy.student@example.com"
        # dummy_student_password = "Password123!"
        # self.loginpage.login(dummy_student_email, dummy_student_password)
        # self.loginpage.verify_login_success_student() # Assuming you have a method to verify student login
        # time.sleep(2)
        # self.loginpage.logout() # Logout the dummy student
        # self.driver.get(self.base_url)
        self.driver.get(self.base_url)
        # 6. Attempt Teacher Login
        self.loginpage.login(username_login, pending_teacher_password)
        result = self.loginpage.verify_login_success() # This should now pass!

        assert result is True