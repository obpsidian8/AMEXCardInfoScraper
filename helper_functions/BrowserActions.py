from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
from os import path
import traceback
import time
from selenium.webdriver.common.keys import Keys
from helper_functions.uilities import print_log


def clearPauseFile():
    checkFile = path.exists('pause.txt')

    if checkFile is True:
        print_log("LOG INFO: Clearing pause file")
        os.remove("pause.txt")
    return


def check_stop_file():
    checkFile = path.exists('pause.txt')

    while checkFile is True:
        print_log("LOG WARN: Pause file present. Pausing script for 5 seconds")
        timer = 0
        while timer < 6:
            print_log(f"LOG INFO; Waiting: {timer}")
            time.sleep(1)
            timer += 1

        print_log("LOG INFO: Checking if pause file is present")
        checkFile = path.exists('pause.txt')

    print_log("LOG INFO: No pause file.Continuing script")
    return


def enter_field_value(driver, xpath, value, time_delay=3.0, pause_after_action=0.01):
    check_stop_file()
    try:
        empty_field = WebDriverWait(driver, time_delay).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        sleepTime = time_delay/2
        time.sleep(sleepTime)
        empty_field.click()
        empty_field.clear()
        empty_field.send_keys(str(value))
        print_log(f"\nLOG INFO: Entered value into field at {xpath}")
    except:
        try:
            empty_field = WebDriverWait(driver, time_delay).until(EC.element_to_be_clickable((By.XPATH, xpath)))
            sleepTime = time_delay / 2
            time.sleep(sleepTime)
            empty_field.send_keys(str(value))
            print_log(f"\nLOG INFO: Entered value into field at {xpath}")
        except:
            #traceback.print_exc()
            print_log(f"\nLOG ERROR: Error entering value for the element given by xpath {xpath}")
            return False
    time.sleep(pause_after_action)
    return True

def sendReturnKey(driver,xpath,time_delay=3.0, pause_after_action=0.01):
    try:
        empty_field = WebDriverWait(driver, time_delay).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        sleepTime = time_delay / 2
        time.sleep(sleepTime)
        empty_field.send_keys(Keys.ENTER)
        print_log(f"\nLOG INFO: ENTER Key sent into field at {xpath}")
    except:
        # traceback.print_exc()
        print_log(f"\nLOG ERROR: Error entering value for the element given by xpath {xpath}")
        return False

    time.sleep(pause_after_action)
    return True


def click_element(driver, xpath, time_delay=1.0, pause_after_action=0.01):
    check_stop_file()
    try:
        element = WebDriverWait(driver, time_delay).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        sleepTime = time_delay/2
        time.sleep(sleepTime)
        element.click()
        print_log(f"\nLOG INFO: Element at {xpath}  successfully clicked")
        time.sleep(pause_after_action)
    except:
        traceback.print_exc()
        print_log(f"\nLOG ERROR: Error clicking element given by xpath {xpath}")
        return False

    return True


def find_presence_of_element(driver, xpath, time_delay=3.0):
    check_stop_file()
    try:
        element = WebDriverWait(driver, time_delay).until(EC.presence_of_element_located((By.XPATH, xpath)))
        print_log(f"\nLOG INFO: Element {element} at {xpath}  present")
    except:
        # traceback.print_exc()
        print_log(f"\nLOG ERROR: Error finding element given by xpath {xpath}")
        return False

    return True


def get_element_text(driver, xpath, time_delay=3.0):
    check_stop_file()
    try:
        element = WebDriverWait(driver, time_delay).until(EC.presence_of_element_located((By.XPATH, xpath)))
        element_text = element.text
        print_log(f"\nLOG INFO: Text found for element at  {xpath}")
    except:
        # traceback.print_exc()
        print_log(f"\nLOG ERROR: Errorgetting text for the element given by xpath {xpath}")
        script = "return document.getElementById('hidden_div').innerHTML"
        element_text = None

    return element_text


def get_number_of_elements(driver, xpath, time_delay=2.0):
    check_stop_file()
    time.sleep(time_delay)
    try:
        elements = driver.find_elements_by_xpath(xpath)
        numElements = len(elements)
    except:
        return 0

    return numElements


def getHtmlElementObjectAsText(driver, xpath, time_delay=3.0):
    try:
        elementObject = WebDriverWait(driver, time_delay).until(EC.presence_of_element_located((By.XPATH, xpath)))
        elementObjectText = elementObject.get_attribute("outerHTML")
        print_log(f"LOG INFO: Found html element at {elementObject}")
    except:
        return None

    return elementObjectText




def getElementAttributeAsText(driver, xpath, attribute_name: str, time_delay = 3.0):
    try:
        elementObject = WebDriverWait(driver, time_delay).until(EC.presence_of_element_located((By.XPATH, xpath)))
        elementObjectAttributeText = elementObject.get_attribute(attribute_name)
    except:
        print_log(f"\nLOG ERROR: Error getting text for the element given by xpath {xpath} or no attribute with name {attribute_name}")
        return None

    return elementObjectAttributeText


def check_page_loaded(driver, page_load_xpath):
        """
        :param page_load_xpath: Xpath of Element that is present for page to be considered fully loaded
        :return:
        """
        start_time = time.time()
        current_page = driver.current_url
        print_log(f"LOG INFO: Waiting for page to load: {current_page}")
        # BEFORE CHECKING FOR TRACKING NUMBERS ON PAGE. CHECK IF PAGE IS LOADED
        pageLoadComplete = find_presence_of_element(driver, page_load_xpath, time_delay=18)
        if pageLoadComplete is True:
            print_log(f"LOG SUCCESS: Page loading complete after {time.time() - start_time} seconds")
        else:
            print_log("LOG WARNING: Page did not load on first try. Waiting")
            pageLoadComplete = find_presence_of_element(driver, page_load_xpath, time_delay=18)
            if pageLoadComplete is True:
                print_log(f"LOG SUCCESS: Page fully loaded after {time.time() - start_time} seconds")
            else:
                print_log(f"LOG ERROR: Page did not load completely. Total wait time: {time.time() - start_time} seconds")

        return pageLoadComplete
