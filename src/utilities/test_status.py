"""
@package utilities

CheckPoint class implementation
It provides functionality to assert the result

Example:
    self.check_point.markFinal("Test Name", result, "Message")
"""
import utilities.custome_logger as cl
import logging
from base.selenium_driver import SeleniumDriver
from traceback import print_stack
import os

class StatusVerifier(SeleniumDriver):

    log = cl.CustomLogger(logging.INFO)

    def __init__(self, driver, base_url):
        """
        Inits CheckPoint class
        """
        super(StatusVerifier, self).__init__(driver, base_url)
        self.resultList = []

    def setResult(self, result, resultMessage):
        try:
            if result is not None:
                if result:
                    self.resultList.append("PASS")
                    self.log.info("### VERIFICATION SUCCESSFUL :: + " + resultMessage)
                else:
                    self.resultList.append("FAIL")
                    self.log.error("### VERIFICATION FAILED :: + " + resultMessage)
                    self.screenShot(resultMessage)
            else:
                self.resultList.append("FAIL")
                self.log.error("### VERIFICATION FAILED :: + " + resultMessage)
                self.screenShot(resultMessage)
        except:
            self.resultList.append("FAIL")
            self.log.error("### Exception Occurred !!!")
            self.screenShot(resultMessage)
            print_stack()

    def mark(self, result, resultMessage):
        """
        Mark the result of the verification point in a test case
        """
        self.setResult(result, resultMessage)

    def markFinal(self, testName, result, resultMessage):
        """
        Mark the final result of the verification point in a test case
        This needs to be called at least once in a test case
        This should be final test status of the test case
        """
        self.setResult(result, resultMessage)

        if "FAIL" in self.resultList:
            self.log.error(testName +  " ### TEST FAILED")
            self.resultList.clear()
            assert True == False
        else:
            self.log.info(testName + " ### TEST SUCCESSFUL")
            self.resultList.clear()
            assert True == True
            
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
