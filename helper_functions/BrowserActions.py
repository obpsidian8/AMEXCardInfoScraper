from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
from os import path
import traceback
import time

def clearPauseFile():
    checkFile = path.exists('purchasing_stopscript.txt')

    if checkFile is True:
        print("Clearing pause file")
        os.remove("purchasing_stopscript.txt")
    return

def check_stop_file():
    checkFile = path.exists('purchasing_stopscript.txt')

    while checkFile is True:
        print("Pause file present. Pausing script for 5 seconds")
        timer = 0
        while timer < 6:
            print(f"Waiting: {timer}")
            time.sleep(1)
            timer += 1

        print("Checking if pause file is present")
        checkFile = path.exists('purchasing_stopscript.txt')

    print("No pause file.Continuing script")
    return

def enter_field_value(driver, xpath, value, time_delay=3.0):
    check_stop_file()
    try:
        empty_field = WebDriverWait(driver, time_delay).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        time.sleep(1.5)
        empty_field.click()
        empty_field.clear()
        empty_field.send_keys(str(value))
        print(f"\nEntered value into field at {xpath}")
    except:
        try:
            empty_field = WebDriverWait(driver, time_delay).until(EC.element_to_be_clickable((By.XPATH, xpath)))
            time.sleep(1.5)
            empty_field.click()
            empty_field.send_keys(str(value))
            print(f"\nEntered value into field at {xpath}")
        except:
            traceback.print_exc()
            print(f"\nError entering value for the element given by xpath {xpath}")
            return False

    return True


def click_element(driver, xpath, time_delay=3.0, pause_after_action=0.01):
    check_stop_file()
    try:
        element = WebDriverWait(driver, time_delay).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        element.click()
        print(f"\nElement at {xpath}  successfully clicked")
        time.sleep(pause_after_action)
    except:
        traceback.print_exc()
        print(f"\nError clicking element given by xpath {xpath}")
        return False

    return True

def find_presence_of_element(driver, xpath, time_delay=3.0):
    check_stop_file()
    try:
        element = WebDriverWait(driver, time_delay).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        print(f"\nElement {element} at {xpath}  present")
    except:
        traceback.print_exc()
        print(f"\nError clicking element given by xpath {xpath}")
        return False

    return True



def get_element_text(driver, xpath, time_delay=3.0):
    check_stop_file()
    try:
        element = WebDriverWait(driver, time_delay).until(EC.presence_of_element_located((By.XPATH, xpath)))
        element_text = element.text
        print(f"\nGetting text for element at  {xpath}")
    except:
        traceback.print_exc()
        print(f"\nError getting text for the element given by xpath {xpath}")
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
        return None

    return numElements

def getHtmlElementObjectAsText(driver,xpath, time_delay =3.0):
    try:
        elementObject = WebDriverWait(driver, time_delay).until(EC.presence_of_element_located((By.XPATH, xpath)))
        elementObjectText = elementObject.get_attribute("innerHTML")
    except:
        print(f"\nError finding element given by xpath {xpath}")
        traceback.print_exc()
        return None

    return elementObjectText
