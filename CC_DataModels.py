import re
import os
from helper_functions.slacknotifier import send_slack_notice
from helper_functions.uilities import date_converter
from helper_functions.uilities import SetChrome
from helper_functions.uilities import print_log
from helper_functions.BrowserActions import enter_field_value, click_element, get_element_text, get_number_of_elements, \
    check_page_loaded

LOGIN_URL = "https://global.americanexpress.com/login/en-US?noRedirect=true"
DASHBOARD_PAGE_URL = "https://global.americanexpress.com/dashboard?inav=MYCA_Home"
LOGOFF_URL = "https://online.americanexpress.com/myca/logon/us/action/LogLogoffHandler?request_type=LogLogoffHandler&Face=en_US"

USER_ID_FIELD = '//*[@id="eliloUserID"]'
PASSWORD_FIELD = '//*[@id="eliloPassword"]'
SUBMIT_FIELD = '//*[@id="loginSubmit"]'

CARD_EXPANDER = '(//*[@class="axp-account-switcher"])[1]'
CARD_EXPANDER_CLOSE = '(//button[contains(@class,"axp-account-switcher__accountSwitcher__togglerButton")])[1]'
CARD_ELEMENTS = '(//*[contains(@class,"bg account-row")])'
CARD_NUMBER_REGEX = re.compile(r"\(-(\d+)")
CARD_NAME_REGEX = re.compile(r"([\w\s]+)")

CARD_ACTIVITY_CONTAINER = '(//div[@class="activity-container"])'
CARD_BALANCE_CONTAINER = '(//div[@data-module-name="axp-balance-payment"])'

CLOSING_DATE_REGEX = re.compile(r'Closing\s+(.+?)\)')
PAYMENT_DUE_REGEX = re.compile(r'Payment\s+Due\s+\$([\d.,]+)')
PAYMENT_DUE_DATE_REGEX = re.compile(r"Please\s+Pay\s+By\s+(.+)")
PAYMENT_DUE_DATE_REGEX_2 = re.compile(r"Payment.+?Due.+?on\s+(.+)")
AVAILABLE_CREDIT_REGEX = re.compile(r'Available\s+(to\sSpend|Credit)\s+\$([\d,.]+)')  # USE GROUP 2
NO_PRESET_LIMIT_REGEX = re.compile(r'(No\s+Pre-Set\s+Spending)')
STATEMENT_BALANCE_REGEX = re.compile(r'Statement\s+Balance\s+\$([\d,.]+)')
STANDARD_BALANCE_REGEX = re.compile(r'Standard\s+Balance\s+\$([\d,.]+)')
TOTAL_BALANCE_REGEX = re.compile(r'Total\s+Balance\s+\$([\d,.]+)')
PREVIOUS_ACTIVITY_REGEX = re.compile(r'Previous\sActivity\s+\$([\d,.]+)')

VIEW_ALL_BUTTON = '(//*[@title="View All"])'

HOME_BUTTON = "(//*[contains(@class,'axp-site-area-nav-container')]//*[contains(text(),'Home')])[1]"


class CardInfo:
    def __init__(self, card_number, user_id):
        self.card_number = card_number
        self.user_id = user_id
        self.card_identifier = None
        self.card_name = None
        self.closing_date = None
        self.payment_due_amount = None
        self.payment_due_date = None
        self.statement_balance = None
        self.total_balance = None
        self.available_credit = None
        self.previous_activity = None

    def update_card_identifier(self):
        self.card_identifier = f"{self.user_id}-{self.card_number}-{self.card_name}"

    def __str__(self):
        readable_form = f"\nCard User ID: {self.user_id}\nCard Number: {self.card_number}\nCard Name: {self.card_name}" \
                        f"\nClosing Date: {self.closing_date}\nPayment Due ${self.payment_due_amount}" \
                        f"\nPayment Due Date: {self.payment_due_date}\nStatement Balance: ${self.statement_balance}" \
                        f"\nTotal Balance: ${self.total_balance}\nAvailable Credit: ${self.available_credit}\nPrevious Activity: ${self.previous_activity}\n"

        return readable_form


class CardUser:
    def __init__(self, user_id, password, chrome_profile_dir=None):
        self.user_id = user_id
        self.password = password
        self.list_of_user_cards_objects = []
        self.driver = None
        self.number_of_cards = None
        self.chrome_profile_dir = chrome_profile_dir

    def show_all_cards_info(self):
        for card_object in self.list_of_user_cards_objects:
            print_log(card_object)

    def set_driver(self):
        if not self.chrome_profile_dir:
            self.chrome_profile_dir = self.user_id
        chrome = SetChrome(self.chrome_profile_dir)
        self.driver = chrome.get_driver()

    def get_num_cards(self):
        current_page = self.driver.current_url
        if current_page != DASHBOARD_PAGE_URL:
            go_home = click_element(self.driver, xpath=HOME_BUTTON)
        click_element(self.driver, xpath=CARD_EXPANDER)
        click_element(self.driver, xpath=VIEW_ALL_BUTTON)
        self.number_of_cards = get_number_of_elements(self.driver, xpath=CARD_ELEMENTS)
        click_element(self.driver, xpath=f"{CARD_ELEMENTS}[1]")

        return self.number_of_cards

    def logout_user(self):
        if not self.driver:
            self.set_driver()
        self.driver.get(LOGOFF_URL)

    def check_login_issues(self):
        current_page = self.driver.current_url
        if "/myca/logon/us/action/LogLogonHandler" in current_page:
            msg = f"LOG ERROR: AMEX Login information incorrect for {self.user_id}. From File: {os.path.basename(__file__)}"
            print_log(f"{msg}")
            send_slack_notice(response=msg)
            return True

        return False

    def login_user(self):
        if not self.driver:
            self.set_driver()

        self.driver.get(LOGIN_URL)

        enter_user_id = enter_field_value(self.driver, USER_ID_FIELD, self.user_id)
        if enter_user_id is True:
            print_log(f"LOG INFO: User Id entered successfully")
        else:
            print_log(f"LOG ERROR: Error Entering user id in field")

        enter_password = enter_field_value(self.driver, PASSWORD_FIELD, self.password)
        if enter_password is True:
            print_log(f"LOG INFO: Password entered successfully")
        else:
            print_log(f"LOG ERROR: Error entering password in field")

        enter_submit = click_element(self.driver, SUBMIT_FIELD)
        if enter_submit is True:
            print_log(f"LOG INFO: Submit clicked successfully")
        else:
            print_log(f"LOG ERROR: Error clicking submit button")

        # AFTER CLICKING SUBMIT, NEXT PAGE SEEN SHOULD BE THE DASHBOARD SCREEN

        page_loaded = check_page_loaded(self.driver, CARD_ACTIVITY_CONTAINER)
        if not page_loaded:
            go_home = click_element(self.driver, xpath=HOME_BUTTON)
            page_loaded = check_page_loaded(self.driver, CARD_ACTIVITY_CONTAINER)
            if not page_loaded:
                print_log(f"LOG WARN: Could not load Amex Home Page!!")

    def scrape_all_card_info(self):
        current_page = self.driver.current_url
        if current_page != DASHBOARD_PAGE_URL:
            go_home = click_element(self.driver, xpath=HOME_BUTTON)

        if self.number_of_cards is None:
            self.get_num_cards()

        click_element(self.driver, xpath=CARD_EXPANDER)
        click_element(self.driver, xpath=VIEW_ALL_BUTTON)

        for card_idx in range(1, self.number_of_cards + 1):
            current_card_xpath = f"{CARD_ELEMENTS}[{card_idx}]"
            card_text = get_element_text(self.driver, current_card_xpath, time_delay=5)
            print_log(f"\n{card_text}\n")

            # GET SOME DETAILS FROM CARD SELECTOR DROP DOWN HERE
            try:
                card_number = CARD_NUMBER_REGEX.search(card_text).group(1).strip()
                print_log(f'LOG SUCCESS: Card Number: {card_number}')
            except:
                print_log(f"LOG ERROR:Error Getting card number")
                card_number = None

            try:
                card_name = CARD_NAME_REGEX.search(card_text).group(1).strip()
                print_log(f"LOG SUCCESS: Card Name: {card_name}")
            except:
                print_log(f"LOG ERROR: Error getting card name")
                card_name = None

            if card_name:
                if card_name == "Personal Savings":
                    continue

            card_selected_details = CardInfo(card_number=card_number, user_id=self.user_id)
            card_selected_details.card_name = card_name

            # CLICK ON CARD FROM CARD SELECTOR DROPDOWN HERE
            click_element(self.driver, current_card_xpath, time_delay=4)

            # CHECK IF PAGE IS LOADED
            page_loaded = check_page_loaded(self.driver, page_load_xpath=CARD_ACTIVITY_CONTAINER)
            if not page_loaded:
                go_home = click_element(self.driver, xpath=HOME_BUTTON)
                page_loaded = check_page_loaded(self.driver, page_load_xpath=CARD_ACTIVITY_CONTAINER)

            # ON PAGE FOR SPECIFIC CARD FROM HERE
            card_activity_text = get_element_text(self.driver, xpath=CARD_ACTIVITY_CONTAINER)
            print_log(f"\n{card_activity_text}\n")

            try:
                closing_date = CLOSING_DATE_REGEX.search(card_activity_text).group(1).strip()
                print_log(f"LOG SUCCESS: Closing date {closing_date}")
            except:
                print_log(f"LOG ERROR: Error getting closing date")
                closing_date = None

            date = date_converter(closing_date)

            card_selected_details.closing_date = date

            card_balances_text = get_element_text(self.driver, xpath=CARD_BALANCE_CONTAINER)
            print_log(f"\n{card_balances_text}\n")

            # GET PAYMENT AMOUNT DUE
            try:
                payment_due_amount = PAYMENT_DUE_REGEX.search(card_balances_text).group(1).strip()
                payment_due_amount = payment_due_amount.replace(",", "")
                payment_due_amount = float(payment_due_amount)
                print_log(f"LOG SUCCESS: Payment Due: {payment_due_amount}")
            except:
                print_log(f"LOG ERROR: No Payment due amount")
                payment_due_amount = 0
            card_selected_details.payment_due_amount = payment_due_amount

            # GET STATEMENT BALANCE
            try:
                statement_balance = STATEMENT_BALANCE_REGEX.search(card_balances_text).group(1).strip()
                statement_balance = statement_balance.replace(",", "")
                statement_balance = float(statement_balance)
                print_log(f"LOG SUCCESS: Statement balance: {statement_balance}")
            except:
                print_log(f"LOG ERROR: No statement balance")
                statement_balance = 0

            if payment_due_amount > 0 and statement_balance <= 0:
                statement_balance = payment_due_amount

            card_selected_details.statement_balance = statement_balance

            # GET PREVIOUS ACTIVITY (IF ANY)
            try:
                previous_activity = PREVIOUS_ACTIVITY_REGEX.search(card_balances_text).group(1).strip()
                previous_activity = previous_activity.replace(",", "")
                previous_activity = float(previous_activity)
                print_log(f"LOG SUCCESS: Previous Activity: {previous_activity}")
            except:
                print_log(f"LOG ERROR: No previous activity displayed")
                previous_activity = None

            card_selected_details.previous_activity = previous_activity

            # GET STANDARD BALANCE IF ANY AND UPDATE STATEMENT BALANCE WITH STANDARD BALANCE AMOUNT IF STATEMENT BALANCE IS NOT AVAILABLE
            try:
                standard_balance = STANDARD_BALANCE_REGEX.search(card_balances_text).group(1).strip()
                standard_balance = standard_balance.replace(",", "")
                standard_balance = float(standard_balance)
                print_log(f"LOG SUCCESS: Standard Balance found: {standard_balance}")
            except:
                print_log(f"LOG INFO: No standard balance present for this account")
                standard_balance = None

            if standard_balance:
                if standard_balance > statement_balance:
                    statement_balance = standard_balance
                    card_selected_details.statement_balance = statement_balance

            if payment_due_amount < statement_balance:
                payment_due_amount = statement_balance
                card_selected_details.payment_due_amount = payment_due_amount

            # GET AVAILABLE CREDIT AMOUNT
            try:
                available_credit = AVAILABLE_CREDIT_REGEX.search(card_balances_text).group(2).strip()
                available_credit = available_credit.replace(",", "")
                available_credit = float(available_credit)
                print_log(f"LOG SUCCESS: Available credit: {available_credit}")
            except:
                try:
                    available_credit = NO_PRESET_LIMIT_REGEX.search(card_balances_text).group(1).strip()
                    print_log(f"LOG SUCCESS: Available credit: {available_credit}")
                except:
                    print_log(f"LOG ERROR: Error getting available credit")
                    available_credit = None
            card_selected_details.available_credit = available_credit

            # GET PAYMENT DUE DATE
            try:
                payment_due_date = PAYMENT_DUE_DATE_REGEX.search(card_balances_text).group(1).strip()
                print_log(f'LOG SUCCESS: Payment due date {payment_due_date}')
            except:
                try:
                    payment_due_date = PAYMENT_DUE_DATE_REGEX_2.search(card_balances_text).group(1).strip()
                    print_log(f'LOG SUCCESS: Payment due date {payment_due_date}')
                except:
                    print_log(f"LOG ERROR: Error getting payment due date")
                    payment_due_date = None

            if payment_due_date:
                payment_due_date = date_converter(payment_due_date)
            card_selected_details.payment_due_date = payment_due_date

            # GET TOTAL BALANCE
            try:
                total_balance = TOTAL_BALANCE_REGEX.search(card_balances_text).group(1).strip()
                total_balance = total_balance.replace(",", "")
                total_balance = float(total_balance)
                print_log(f"LOG SUCCESS: Total Balance: {total_balance}")
            except:
                print_log(f"LOG ERROR: Error getting total balance")
                total_balance = 0
            card_selected_details.total_balance = total_balance

            card_selected_details.update_card_identifier()

            # ADD CURRENT CARD TO LIST OF CARDS FOR THIS USER ID
            self.list_of_user_cards_objects.append(card_selected_details)

            # click_element(self.driver, current_card_xpath)
            click_element(self.driver, xpath=CARD_EXPANDER)

    def close_browser_sessions(self):
        self.driver.close()
        self.driver.quit()
