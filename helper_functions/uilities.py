from selenium import webdriver
from multiprocessing import Pool
import re
from datetime import date


def runJobs(function, listInputs, numberOfProcesses):
    """
    Sets up multiprocessing of jobs
    :param function: function. Function to be run multiple times
    :param listInputs: list. List of inputs to be run
    :param numberOfProcesses: int. Number of processes to run concurrently
    :return: list of results from running the function over the given inputs (If the function given has any return value)
    """
    multiProcessPool = Pool(numberOfProcesses)
    with multiProcessPool as p:
        r = p.starmap(function, zip(listInputs))
        return r


class SetChrome:
    def __init__(self, data_dir):
        self.data_dir = f"C:/chromeprofiles_other/{data_dir}"
        print_log(f"LOG INFO: Setting Chrome for user {data_dir}")

    def get_driver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f"--user-data-dir={self.data_dir}")
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1200, 2000)
        return driver


def print_log(msg):
    msg = str(msg)
    if "LOG ERROR" in msg:
        color_prefix = "\u001b[31m"
    elif "LOG SUCCESS" in msg:
        color_prefix = "\u001b[32m"
    elif "LOG WARNING" in msg or "LOG WARN" in msg:
        color_prefix = "\u001b[33m"
    else:
        color_prefix = "\u001b[34m"

    print(f"{color_prefix}{msg}\u001b[0m")


def date_converter(date_str: str):
    if date_str == "Today":
        return date.today()
    date_map = {"Jan": 1,
                "January": 1,
                "Feb": 2,
                "February": 2,
                "Mar": 3,
                "March": 3,
                "Apr": 4,
                "April": 4,
                "May": 5,
                "Jun": 6,
                "June": 6,
                "Jul": 7,
                "July": 7,
                "Aug": 8,
                "August": 8,
                "Sep": 9,
                "September": 9,
                "Oct": 10,
                "October": 10,
                "Nov": 11,
                "November": 11,
                "Dec": 12,
                "December": 12,
                }

    date_regex = re.compile(r'(\w+)\s+(\d+)')
    try:
        month = date_regex.search(date_str).group(1).strip()
        print_log(f"LOG SUCCESS: Month extracted: {month}")
    except:
        print_log(f"LOG ERROR: Error getting month part from date string")
        month = None

    try:
        day = date_regex.search(date_str).group(2).strip()
        day_int = int(day)
        print_log(f"LOG SUCCESS: Day extracted: {day}")
    except:
        print_log(f"LOG ERROR: Error getting day part from date string")
        day_int = None

    if month:
        print_log(f"LOG INFO: Converting month string to int")
        month_int = date_map.get(month)
    else:
        month_int = None

    if day_int and month_int:

        today_date = date.today()
        year = today_date.year

        full_date = date(year=year, month=month_int, day=day_int)

        return full_date
    else:
        return date_str


def test_print():
    message_list = ["LOG ERROR", "LOG SUCCESS", "LOG WARNING", "LOG WARN", "INFO"]
    for msg in message_list:
        print_log(msg)


if __name__ == "__main__":
    test_print()
