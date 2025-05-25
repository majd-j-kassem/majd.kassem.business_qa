from selenium.webdriver.common.by import By
from traceback import print_stack
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
import time


class SeleniumDriver():
    
    def __init__(self, driver):
        self.driver = driver

    def getByType(self, locatorType):
        locatorType = locatorType.lower()
        if locatorType == "id":
            return By.ID
        elif locatorType == "name":
            return By.NAME
        elif locatorType == "xpath":
            return By.XPATH
        elif locatorType == "css":
            return By.CSS_SELECTOR
        elif locatorType == "classname":
            return By.CLASS_NAME
        elif locatorType == "linktext":
            return By.LINK_TEXT
        else:
            self.log.info("Locator type " + locatorType + " not correct/supported")
        return False
    def click_element(self, locator, locatorType="id"):
        try:  
            element = self.get_element(locator, locatorType)
            element.click()
            self.log.info("Click on the element with locator: " + 
                          str(locator) + " and locator type " + str(locatorType))

        except Exception as e:
            self.log.error("Can not send data on the element with locator: " +
                           str(locator) + " and locator type " + str(locatorType) + f". Error: {e}")
            raise # Re-raise the exception so the test fails
    def get_element(self, locator, locatorType="id"):
        element = None
        try:
            locatorType = locatorType.lower()
            byType = self.getByType(locatorType)
            wait = WebDriverWait(self.driver, 15) 
            element = wait.until(EC.presence_of_element_located((byType, locator)))
            #element = self.driver.find_element(byType, locator)
            self.log.info("Element Found " + str(element))
        except:
            self.log.info("Element not found" + str(element))
        return element
   
    def send_keys_element(self, data, locator, locatorType="id"):
        try:  
            element = self.get_element(locator, locatorType)
            element.send_keys(data)
            self.log.info("Send data on the element with locator: " + 
            locator + " and locator type " + str(element))

        except:
            self.log.info("Can not send data on the element with locator:" + 
            locator + "and locator type " + locatorType )
    def isElementPresent(self, locator, locatorType="id"):
        try:
            element = self.get_element(locator, locatorType)
            if element is not None:
                self.log.info("Element Found " + str(element))
                return True
            else:
                self.log.info("Element not found " + str(element))
                return False
        except:
            print("Element not found")
            return False
    def isElementVisible(self, locator, locatorType="id", timeout=10, pollFrequency=0.5):
        try:
            byType = self.getByType(locatorType)
            if not byType:
                return False

            self.log.info(f"Waiting for VISIBILITY of element with locator: '{locator}' "
                        f"and type: '{locatorType}' for {timeout} seconds.")

            wait = WebDriverWait(self.driver, timeout, poll_frequency=pollFrequency)
            element = wait.until(EC.visibility_of_element_located((byType, locator)))
            self.log.info(f"Element is visible: '{locator}' with type '{locatorType}'")
            return element is not None
        except Exception as e:
            self.log.error(f"Element NOT visible: '{locator}' ({locatorType}) "
                           f"after {timeout} seconds. Error: {e}")
            # --- ADD SCREENSHOT HERE ---
            try:
                screenshot_name = f"element_not_visible_{locator.replace(' ', '_')}_{time.time()}.png"
                self.driver.save_screenshot(f"screenshots/{screenshot_name}")
                self.log.error(f"Screenshot taken: screenshots/{screenshot_name}")
            except Exception as screenshot_e:
                self.log.error(f"Failed to take screenshot: {screenshot_e}")
            # --- END SCREENSHOT ADDITION ---
            return False
    def elementPresenceCheck(self, locator, byType):
        try:
            elementList = self.driver.find_elements(byType, locator)
            if len(elementList) > 0:
                self.log.info("Element Found ")
                return True
            else:
                self.log.info("Element not found")
                return False
        except:
            self.log.info("Element not found")
            return False
    def waitForElement(self, locator, locatorType="id",
                       timeout=10, pollFrequency=0.5):
        element = None
        try:
            self.driver.implicitly_wait(0)
            byType = self.hw.getByType(locatorType)
            self.log.info("Waiting for maximum :: " + str(timeout) +
                          " :: seconds for element to be visible")
            wait = WebDriverWait(self.driver, timeout=timeout, poll_frequency=pollFrequency,
                                 ignored_exceptions=[NoSuchElementException,
                                                     ElementNotVisibleException,
                                                     ElementNotSelectableException])
            element = wait.until(EC.visibility_of_element_located((byType, locator)))
            self.log.info("Element appeared on the web page")
        except:
            self.log.info("Element not appeared on the web page")
        self.driver.implicitly_wait(2)
        return element