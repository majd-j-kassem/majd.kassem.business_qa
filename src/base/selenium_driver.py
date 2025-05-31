from selenium.webdriver.common.by import By
from traceback import print_stack
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException, ElementClickInterceptedException,
    StaleElementReferenceException, ElementNotInteractableException
)
import time
import logging
import os
import utilities.custome_logger as cl
from selenium.webdriver.remote.webelement import WebElement # Import WebElement for type hinting

class SeleniumDriver():

    def __init__(self, driver, base_url):
        self.driver = driver
        self.log = cl.CustomLogger(logging.DEBUG)

    def _get_by_type(self, locatorType):
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
            return False

    def get_element(self, locator, locatorType="id", timeout=10, pollFrequency=0.5, condition=EC.presence_of_element_located) -> WebElement:
        """
        Waits for an element based on a specified expected_condition and returns it.
        Default condition: EC.presence_of_element_located (element in DOM).
        Includes error logging and screenshot on failure.
        """
        element = None
        try:
            byType = self._get_by_type(locatorType)
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
            self.take_screenshot_on_failure(locator, locatorType, "timeout")
        except NoSuchElementException:
            self.log.error(f"No such element: '{locator}' ({locatorType}).")
            self.take_screenshot_on_failure(locator, locatorType, "no_such_element")
        except StaleElementReferenceException:
            self.log.error(f"Stale element reference for: '{locator}' ({locatorType}). Element re-rendered.")
            self.take_screenshot_on_failure(locator, locatorType, "stale_element")
        except Exception as e:
            self.log.error(f"An unexpected error occurred while getting element '{locator}' ({locatorType}): {e}")
            self.take_screenshot_on_failure(locator, locatorType, "unexpected_get_error")
        return element

    def take_screenshot_on_failure(self, locator, locatorType, event_type="failure"):
        """
        Helper method to take a screenshot when an element interaction fails.
        `event_type` helps categorize the screenshot (e.g., "timeout", "retry_intercepted").
        """
        try:
            screenshot_dir = "screenshots"
            if not os.path.exists(screenshot_dir):
                os.makedirs(screenshot_dir)

            sanitized_locator = locator.replace(' ', '_').replace('/', '_').replace('.', '_').replace('[', '').replace(']', '').replace('=', '_').replace("'", "")
            screenshot_name = f"{event_type}_{sanitized_locator}_{locatorType}_{int(time.time())}.png"
            screenshot_path = os.path.join(screenshot_dir, screenshot_name)
            
            self.driver.save_screenshot(screenshot_path)
            self.log.error(f"Screenshot taken: {screenshot_path}")
        except Exception as screenshot_e:
            self.log.error(f"Failed to take screenshot: {screenshot_e}")

    def click_element(self, locator, locatorType="id", timeout=10, pollFrequency=0.5, retry_attempts=2):
        """
        Clicks on an element after waiting for it to be clickable.
        Includes robust error handling, scrolling, and a retry mechanism for flakiness.
        """
        attempts = 0
        while attempts <= retry_attempts:
            try:
                # 1. Wait for the element to be clickable
                element = self.get_element(locator, locatorType, timeout=timeout,
                                           pollFrequency=pollFrequency, condition=EC.element_to_be_clickable)
                
                if element:
                    # 2. Scroll the element into view explicitly
                    # Using 'center' for block and inline makes it more robust for various layouts
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", element)
                    time.sleep(0.1) # Small pause after scrolling to let browser render

                    # 3. Attempt the click
                    element.click()
                    self.log.info(f"Clicked element with locator: '{locator}' and type: '{locatorType}' (Attempt {attempts + 1})")
                    return True # Success
                else:
                    self.log.error(f"Element '{locator}' ({locatorType}) not found or not clickable after {timeout}s.")
                    # If get_element returns None, it already logged the reason and took a screenshot.
                    break # Exit loop if element itself wasn't found/clickable after initial wait
            
            except (ElementClickInterceptedException, StaleElementReferenceException) as e:
                self.log.warning(f"Click intercepted or stale element for '{locator}' ({locatorType}). "
                                 f"Attempt {attempts + 1} failed. Retrying... Error: {e}")
                self.take_screenshot_on_failure(locator, locatorType, f"retry_{attempts + 1}_intercepted")
                attempts += 1
                time.sleep(0.5) # Small pause before retrying
            except Exception as e:
                self.log.error(f"An unexpected error occurred while clicking element '{locator}' ({locatorType}). "
                               f"Error: {e}. Attempt {attempts + 1} failed.")
                self.take_screenshot_on_failure(locator, locatorType, f"retry_{attempts + 1}_unexpected")
                attempts += 1
                time.sleep(0.5) # Small pause before retrying
        
        # If all attempts fail, raise a more specific exception for the test to catch
        self.log.critical(f"Failed to click element: '{locator}' ({locatorType}) after {retry_attempts + 1} attempts.")
        self.take_screenshot_on_failure(locator, locatorType, "final_click_failure")
        # Do not raise here, as the click_element is called within AdminDashboardPage methods
        # and those methods expect a True/False return. If we raise, the calling method
        # in AdminDashboardPage might not return False correctly.
        return False # Return False if click failed after all attempts


    def send_keys_element(self, data, locator, locatorType="id", timeout=10, pollFrequency=0.5):
        """
        Sends data to an element after waiting for it to be visible and interactable.
        """
        try:
            element = self.get_element(locator, locatorType, timeout=timeout,
                                       pollFrequency=pollFrequency, condition=EC.visibility_of_element_located)
            if element:
                # Clear existing text before sending keys
                element.clear() 
                element.send_keys(data)
                self.log.info(f"Sent data '{data}' to element with locator: '{locator}' and type: '{locatorType}'")
                return True # Indicate success
            else:
                self.log.error(f"Could not send data: Element was not found or not visible "
                               f"with locator: '{locator}' and type: '{locatorType}' after {timeout} seconds.")
                # Do not raise here, let the calling method handle the False return
                return False
        except Exception as e:
            self.log.error(f"An error occurred while sending keys to element '{locator}' ({locatorType}). Error: {e}")
            self.take_screenshot_on_failure(locator, locatorType, "send_keys_error")
            return False # Indicate failure

    def is_element_present(self, locator, locatorType="id", timeout=5, pollFrequency=0.5):
        """
        Checks if an element is present in the DOM (not necessarily visible) within a timeout.
        """
        element = self.get_element(locator, locatorType, timeout=timeout,
                                   pollFrequency=pollFrequency, condition=EC.presence_of_element_located)
        if element is not None:
            self.log.info(f"Element found present in DOM: '{locator}' ({locatorType})")
            return True
        else:
            self.log.info(f"Element NOT found present in DOM: '{locator}' ({locatorType}) after {timeout} seconds.")
            return False

    def is_element_visible(self, locator, locatorType="id", timeout=10, pollFrequency=0.5):
        """
        Checks if an element is present in the DOM AND visible within a timeout.
        """
        element = self.get_element(locator, locatorType, timeout=timeout,
                                   pollFrequency=pollFrequency, condition=EC.visibility_of_element_located)
        if element is not None:
            self.log.info(f"Element is visible: '{locator}' with type '{locatorType}'")
            return True
        else:
            self.log.info(f"Element NOT visible: '{locator}' ({locatorType}) after {timeout} seconds.")
            return False

    def elementPresenceCheck(self, locator, locatorType="id"):
        """
        Checks if ANY elements match the locator using find_elements, without explicit waits.
        Useful for checking if elements *should not* exist or counting multiple elements.
        """
        try:
            byType = self._get_by_type(locatorType)
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

    def webScroll(self, direction="up"):
        """
        Scrolls the web page up or down.
        """
        if direction == "up":
            self.driver.execute_script("window.scrollBy(0, -800);")
            self.log.info("Scrolled page up by 800 pixels.")
        if direction == "down":
            self.driver.execute_script("window.scrollBy(0, 800);")
            self.log.info("Scrolled page down by 800 pixels.")

    def wait_for_element_to_be_invisible(self, locator, locatorType="id", timeout=10, pollFrequency=0.5):
        """
        Waits for an element to become invisible. Useful for loading spinners or modals.
        """
        try:
            byType = self._get_by_type(locatorType)
            if not byType:
                self.log.error(f"Invalid locator type provided for '{locator}'. Cannot wait for invisibility.")
                return False
            
            self.log.info(f"Waiting for invisibility of element with locator: '{locator}' "
                          f"and type: '{locatorType}' for {timeout} seconds.")
            wait = WebDriverWait(self.driver, timeout, poll_frequency=pollFrequency)
            invisible = wait.until(EC.invisibility_of_element_located((byType, locator)))
            if invisible:
                self.log.info(f"Element '{locator}' ({locatorType}) is now invisible.")
                return True
            else:
                self.log.warning(f"Element '{locator}' ({locatorType}) is still visible after {timeout} seconds.")
                self.take_screenshot_on_failure(locator, locatorType, "still_visible")
                return False
        except TimeoutException:
            self.log.warning(f"Element '{locator}' ({locatorType}) did not become invisible within {timeout} seconds. TimeoutException occurred.")
            self.take_screenshot_on_failure(locator, locatorType, "invisibility_timeout")
            return False
        except Exception as e:
            self.log.error(f"An error occurred while waiting for invisibility of '{locator}' ({locatorType}): {e}")
            self.take_screenshot_on_failure(locator, locatorType, "invisibility_error")
            return False
            
    def wait_for_page_load(self, timeout=30):
        """
        Waits for the page to fully load by checking document.readyState.
        """
        self.log.info(f"Waiting for page to load (document.readyState == 'complete') for up to {timeout} seconds.")
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            self.log.info("Page loaded successfully.")
            return True # Indicate success
        except TimeoutException:
            self.log.error(f"Page did not load within {timeout} seconds (document.readyState != 'complete').")
            self.take_screenshot_on_failure("page_load_timeout", "browser", "page_load_timeout") # Use a generic locator for screenshot
            # Don't re-raise immediately, allow calling method to handle
            return False
        except Exception as e:
            self.log.error(f"An unexpected error occurred while waiting for page load: {e}")
            self.take_screenshot_on_failure("page_load_error", "browser", "page_load_error")
            # Don't re-raise immediately, allow calling method to handle
            return False

    def get_text_of_element(self, locator, locatorType="id", timeout=10, pollFrequency=0.5) -> str:
        """
        Gets the text of an element after waiting for it to be visible.
        Returns empty string if element is not found or has no text.
        """
        element_text = ""
        try:
            element = self.get_element(locator, locatorType, timeout=timeout,
                                       pollFrequency=pollFrequency, condition=EC.visibility_of_element_located)
            if element:
                element_text = element.text
                self.log.info(f"Retrieved text '{element_text}' from element with locator: '{locator}' and type: '{locatorType}'")
            else:
                self.log.warning(f"Could not get text: Element was not found or not visible "
                                 f"with locator: '{locator}' and type: '{locatorType}' after {timeout} seconds.")
        except Exception as e:
            self.log.error(f"An error occurred while getting text from element '{locator}' ({locatorType}). Error: {e}")
            self.take_screenshot_on_failure(locator, locatorType, "get_text_error")
            # Don't re-raise here, return empty string as per function contract
        return element_text
    
    def _wait_for_element(self, locator, locator_type, timeout=10, condition=EC.presence_of_element_located):
        """
        Waits for a specified element to meet a given condition.
        Returns the WebElement if found and condition met, otherwise returns False.
        """
        by_type = self._get_by_type(locator_type)
        try:
            self.log.info(f"Waiting for '{condition.__name__}' of element with locator: '{locator}' and type: '{locator_type}' for {timeout} seconds.")
            element = WebDriverWait(self.driver, timeout).until(condition((by_type, locator)))
            self.log.info(f"Element Found and condition met: '{locator}' with type '{locator_type}'")
            return element
        except TimeoutException:
            self.log.error(f"Element NOT found or condition '{condition.__name__}' not met: '{locator}' ({locator_type}) after {timeout} seconds. TimeoutException occurred.")
            self.take_screenshot(f"timeout_element_{locator_type}_{self._clean_locator_name(locator)}_{self.get_current_timestamp()}.png")
            return False
        except NoSuchElementException:
            self.log.error(f"Element NOT found: '{locator}' ({locator_type}) after {timeout} seconds. NoSuchElementException occurred.")
            self.take_screenshot(f"nosuch_element_{locator_type}_{self._clean_locator_name(locator)}_{self.get_current_timestamp()}.png")
            return False
        except Exception as e:
            self.log.error(f"An unexpected error occurred while waiting for element '{locator}' ({locator_type}): {e}")
            self.take_screenshot(f"error_wait_element_{locator_type}_{self._clean_locator_name(locator)}_{self.get_current_timestamp()}.png")
            return False

    def wait_for_element_and_click(self, locator, locator_type, timeout=10, max_retries=3):
        """
        Waits for an element to be clickable and then clicks it.
        Includes retry logic for StaleElementReferenceException.

        Args:
            locator (str): The locator string (e.g., "//button[@id='submit']").
            locator_type (str): The type of locator (e.g., "xpath", "id", "name", "css").
            timeout (int): Maximum time in seconds to wait for the element to be clickable.
            max_retries (int): Maximum number of retries for StaleElementReferenceException.

        Returns:
            bool: True if the element was successfully clicked, False otherwise.
        """
        attempt = 0
        while attempt < max_retries:
            element = self._wait_for_element(locator, locator_type, timeout, EC.element_to_be_clickable)
            if element:
                try:
                    # Scroll element into view before clicking to ensure visibility and clickability
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    element.click()
                    self.log.info(f"Clicked element with locator: '{locator}' and type: '{locator_type}' (Attempt {attempt + 1})")
                    return True
                except StaleElementReferenceException:
                    self.log.warning(f"StaleElementReferenceException trying to click '{locator}' ({locator_type}). Retrying... (Attempt {attempt + 1})")
                    time.sleep(0.5) # A small pause before retry
                    attempt += 1
                except Exception as e:
                    self.log.error(f"Error clicking element '{locator}' ({locator_type}) (Attempt {attempt + 1}): {e}")
                    self.take_screenshot(f"click_error_{locator_type}_{self._clean_locator_name(locator)}_{self.get_current_timestamp()}.png")
                    return False
            else:
                self.log.error(f"Element '{locator}' ({locator_type}) was not found or not clickable within {timeout} seconds.")
                return False # Element wasn't found even on the first try

        self.log.error(f"Failed to click element '{locator}' ({locator_type}) after {max_retries} retries due to StaleElementReferenceException.")
        self.take_screenshot(f"final_click_fail_{locator_type}_{self._clean_locator_name(locator)}_{self.get_current_timestamp()}.png")
        return False
