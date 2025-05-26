from selenium.webdriver.common.by import By
from traceback import print_stack # Kept for potential advanced debugging if needed
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
import time
import logging
import os # Import os for path manipulation and directory creation
import utilities.custome_logger as cl # Assuming this is your custom logger setup

class SeleniumDriver():

    def __init__(self, driver):
        self.driver = driver
        # Initialize the logger for this class instance
        # Ensure your customLogger returns a logger instance correctly
        self.log = cl.customLogger(logging.DEBUG)

    def getByType(self, locatorType):
        """
        Translates a string locator type into a Selenium By object.
        """
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
        elif locatorType == "partiallinktext":
            return By.PARTIAL_LINK_TEXT
        else:
            self.log.error(f"Locator type '{locatorType}' not correct/supported.")
            return False # Indicate invalid type

    def get_element(self, locator, locatorType="id", timeout=10, pollFrequency=0.5, condition=EC.presence_of_element_located):
        """
        Waits for an element based on a specified expected_condition and returns it.
        Default condition: EC.presence_of_element_located (element in DOM).
        """
        element = None
        try:
            byType = self.getByType(locatorType)
            if not byType:
                self.log.error(f"Invalid locator type provided for '{locator}'. Cannot get element.")
                return None

            self.log.info(f"Waiting for '{condition.__name__}' of element with locator: '{locator}' "
                          f"and type: '{locatorType}' for {timeout} seconds.")

            wait = WebDriverWait(self.driver, timeout, poll_frequency=pollFrequency)
            element = wait.until(condition((byType, locator)))
            self.log.info(f"Element Found and condition met: '{locator}' with type '{locatorType}'")
        except TimeoutException:
            self.log.error(f"Element NOT found or condition '{condition.__name__}' not met: '{locator}' ({locatorType}) "
                           f"after {timeout} seconds. TimeoutException occurred.")
            self.take_screenshot_on_failure(locator, locatorType) # Take screenshot on timeout
        except Exception as e:
            self.log.error(f"An unexpected error occurred while getting element '{locator}' ({locatorType}). Error: {e}")
            self.take_screenshot_on_failure(locator, locatorType) # Take screenshot on other exceptions
        return element

    def take_screenshot_on_failure(self, locator, locatorType):
        """
        Helper method to take a screenshot when an element interaction fails.
        """
        try:
            screenshot_dir = "screenshots"
            # Ensure the screenshots directory exists
            if not os.path.exists(screenshot_dir):
                os.makedirs(screenshot_dir)

            # Sanitize locator for filename, replacing spaces and slashes
            sanitized_locator = locator.replace(' ', '_').replace('/', '_').replace('.', '_')
            screenshot_name = f"failure_{sanitized_locator}_{locatorType}_{time.time()}.png"
            screenshot_path = os.path.join(screenshot_dir, screenshot_name)
            
            self.driver.save_screenshot(screenshot_path)
            self.log.error(f"Screenshot taken: {screenshot_path}")
        except Exception as screenshot_e:
            self.log.error(f"Failed to take screenshot: {screenshot_e}")

    def click_element(self, locator, locatorType="id", timeout=10, pollFrequency=0.5):
        """
        Clicks on an element after waiting for it to be clickable.
        """
        try:
            # Use get_element, explicitly waiting for it to be clickable
            element = self.get_element(locator, locatorType, timeout=timeout,
                                       pollFrequency=pollFrequency, condition=EC.element_to_be_clickable)
            if element: # Check if element was successfully found and is clickable
                element.click()
                self.log.info(f"Clicked element with locator: '{locator}' and type: '{locatorType}'")
            else:
                self.log.error(f"Could not click element: Element was not found or not clickable "
                               f"with locator: '{locator}' and type: '{locatorType}' after {timeout} seconds.")
                # Raise an explicit exception if the element wasn't clickable after the wait
                raise ElementClickInterceptedException(f"Element not clickable: {locator} ({locatorType})")
        except Exception as e:
            self.log.error(f"An error occurred while clicking element '{locator}' ({locatorType}). Error: {e}")
            # The get_element method already calls take_screenshot_on_failure on TimeoutException,
            # but if another exception occurs during the click itself, it's captured here.
            # self.take_screenshot_on_failure(locator, locatorType) # Uncomment if you want an extra screenshot
            raise # Re-raise the exception to fail the test

    def send_keys_element(self, data, locator, locatorType="id", timeout=10, pollFrequency=0.5):
        """
        Sends data to an element after waiting for it to be visible.
        """
        try:
            # Use get_element, explicitly waiting for it to be visible
            element = self.get_element(locator, locatorType, timeout=timeout,
                                       pollFrequency=pollFrequency, condition=EC.visibility_of_element_located)
            if element: # Check if element was successfully found and is visible
                element.send_keys(data)
                self.log.info(f"Sent data '{data}' to element with locator: '{locator}' and type: '{locatorType}'")
            else:
                self.log.error(f"Could not send data: Element was not found or not visible "
                               f"with locator: '{locator}' and type: '{locatorType}' after {timeout} seconds.")
                # Raise an explicit exception if the element wasn't visible after the wait
                raise ElementNotInteractableException(f"Element not interactable (not visible): {locator} ({locatorType})")
        except Exception as e:
            self.log.error(f"An error occurred while sending keys to element '{locator}' ({locatorType}). Error: {e}")
            # self.take_screenshot_on_failure(locator, locatorType) # Uncomment if you want an extra screenshot
            raise # Re-raise the exception to fail the test

    def isElementPresent(self, locator, locatorType="id", timeout=5, pollFrequency=0.5):
        """
        Checks if an element is present in the DOM (not necessarily visible) within a timeout.
        """
        # Re-use get_element, defaulting to presence_of_element_located
        element = self.get_element(locator, locatorType, timeout=timeout,
                                   pollFrequency=pollFrequency, condition=EC.presence_of_element_located)
        if element is not None:
            self.log.info(f"Element found present in DOM: '{locator}' ({locatorType})")
            return True
        else:
            self.log.info(f"Element NOT found present in DOM: '{locator}' ({locatorType}) after {timeout} seconds.")
            return False

    def isElementVisible(self, locator, locatorType="id", timeout=10, pollFrequency=0.5):
        """
        Checks if an element is present in the DOM AND visible within a timeout.
        This method is kept similar to your original, but now internally relies on get_element.
        """
        # Re-use get_element, explicitly waiting for visibility
        element = self.get_element(locator, locatorType, timeout=timeout,
                                   pollFrequency=pollFrequency, condition=EC.visibility_of_element_located)
        if element is not None:
            self.log.info(f"Element is visible: '{locator}' with type '{locatorType}'")
            return True
        else:
            self.log.info(f"Element NOT visible: '{locator}' ({locatorType}) after {timeout} seconds.")
            # Screenshot is already taken by get_element if it timed out.
            return False

    def elementPresenceCheck(self, locator, locatorType="id"): # Renamed from original to be more explicit if used for lists
        """
        Checks if ANY elements match the locator using find_elements, without explicit waits.
        Useful for checking if elements *should not* exist or counting multiple elements.
        """
        try:
            byType = self.getByType(locatorType)
            if not byType:
                self.log.error(f"Invalid locator type provided for '{locator}'. Cannot check element list.")
                return False
            
            elementList = self.driver.find_elements(byType, locator)
            if len(elementList) > 0:
                self.log.info(f"Found {len(elementList)} element(s) for locator: '{locator}' ({locatorType})")
                return True
            else:
                self.log.info(f"No elements found for locator: '{locator}' ({locatorType})")
                return False
        except Exception as e:
            self.log.error(f"An error occurred while checking for element list presence for '{locator}' ({locatorType}). Error: {e}")
            return False

    # The old 'waitForElement' method has been removed. Its functionality is now covered
    # by the enhanced 'get_element' method and the robust 'isElementVisible'.
    # This removes redundant code and avoids problematic implicit_wait manipulations.