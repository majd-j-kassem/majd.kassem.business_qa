import pytest
from selenium import webdriver
from base.web_driver_factory import WebDriverFactory

@pytest.yield_fixture()
def setUp():
    print("Running method level setUp")
    yield
    print("Running method level tearDown")


@pytest.yield_fixture(scope="class")
def oneTimeSetUp(request, browser):
    base_url = "http://127.0.0.1:8000/"
    wdf = WebDriverFactory(driver)
    driver = wdf.getWebDriverInstance()
    print("Running one time setUp")

    if request.cls is not None:
        request.cls.driver = driver
    yield driver
    driver.quit()
    print("Running one time tearDown")

def pytest_addoption(parser):
    parser.addoption( "--browser", action="store", default="chrome", 
                     help="browser to execute tests (chrome or firefox)")
    parser.addoption("--osType", help="Type of operating system")

@pytest.fixture(scope="session")
def browser(request):
    return request.config.getoption("--browser")

@pytest.fixture(scope="session")
def osType(request):
    return request.config.getoption("--osType")