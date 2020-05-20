import os
import time
import traceback
import sys

from CC_DataModels import CardUser, CardInfo
from helper_functions.uilities import runJobs
from helper_functions.CmdArgParser import argument_parser
from helper_functions.excel_converter import convert_excel_to_list_of_dict, list_of_json_to_excel
import collections

# UpdateMondaySite module is located in the directory above, which has been added to the path python will search for modules
# monday_helper folder is in the PriceScrapingScripts folder defined below
ADDITIONAL_SOURCES_PATH = r'C:\pythonscripts\PurchasingScripts\DealScriptsSettingsZim\PriceScrapingScripts'
sys.path.append(ADDITIONAL_SOURCES_PATH)
from monday_helper.UpdateMondaySite import ZoeBoardActions

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILES_DIR = os.path.join(PROJECT_DIR, 'DataFiles')
print(f"LOG INFO:: PROJECT_DIR: {PROJECT_DIR}")
print(f"LOG INFO:: DATA_FILES_DIR:{DATA_FILES_DIR}")


def test_case_single_user():
    card_details = CardUser(user_id="test_account", password="life1545")
    card_details.login_user()

    login_problem = card_details.check_login_issues()
    if not login_problem:
        cards = card_details.get_num_cards()
        print(f"# Cards: {cards}")

        card_details.scrape_all_card_info()
        card_details.show_all_cards_info()
        card_details.close_browser_sessions()

        # ADD CARD INFORMATION TO BOARD
        for single_card in card_details.list_of_user_cards_objects:
            scraper_monday_upload(single_card)

        return card_details.list_of_user_cards_objects

    card_details.show_all_cards_info()
    card_details.close_browser_sessions()


def single_user_job(user_info_dict: dict):
    try:
        user_id = user_info_dict.get("user_id")
        password = user_info_dict.get("password")
        chrome_profile_dir = user_info_dict.get("chrome_profile_dir")

        card_details = CardUser(user_id, password, chrome_profile_dir)
        card_details.login_user()
        card_details.scrape_all_card_info()
        card_details.close_browser_sessions()

        # ADD CARD INFORMATION TO BOARD
        for single_card in card_details.list_of_user_cards_objects:
            scraper_monday_upload(single_card)

        # A LIST OF CARD OBJECTS FOR THE USER
        return card_details.list_of_user_cards_objects
    except:
        traceback.print_exc()
        return []


def scraper_monday_upload(single_card_details: CardInfo):
    item_name = single_card_details.card_identifier

    user_id = single_card_details.user_id
    ending_digits = single_card_details.card_number
    card_name = single_card_details.card_name

    closing_date = single_card_details.closing_date
    payment_due = single_card_details.payment_due_amount
    payment_due_date = single_card_details.payment_due_date
    statement_balance = single_card_details.statement_balance
    total_balance = single_card_details.total_balance
    available_credit = single_card_details.available_credit
    previous_activity = single_card_details.previous_activity

    card_upload = ZoeBoardActions(board_name="Amex Card Balances")
    card_upload.add_new_item_to_board(item_name=item_name)

    current_closing_date_in_sheet = card_upload.get_value_of_column_for_item(item_name=item_name, col_title="Closing Date")
    if current_closing_date_in_sheet:
        if current_closing_date_in_sheet != closing_date:
            print(f"LOG INFO: New closing date for item {item_name}")

    card_upload.change_value_of_column(item_name=item_name, col_title="Closing Date", new_value=closing_date)

    if payment_due is not None:
        card_upload.change_value_of_column(item_name=item_name, col_title="Payment Due", new_value=payment_due)
        new_status_value = "No Amount Due"
        if payment_due <= 0:
            new_status_value = "No Amount Due"
            card_upload.move_item_to_group(item_name=item_name, group_name="Next Month")
        elif payment_due > 0:
            new_status_value = "Due Soon"
            card_upload.move_item_to_group(item_name=item_name, group_name="Urgent")
        card_upload.change_value_of_column(item_name=item_name, col_title="Status", new_value=new_status_value)

    if payment_due_date is not None:
        card_upload.change_value_of_column(item_name=item_name, col_title="Payment Due Date", new_value=payment_due_date)

    if statement_balance is not None:
        card_upload.change_value_of_column(item_name=item_name, col_title="Statement Balance", new_value=statement_balance)

    if total_balance is not None:
        card_upload.change_value_of_column(item_name=item_name, col_title="Total Balance", new_value=total_balance)

    if available_credit:
        card_upload.change_value_of_column(item_name=item_name, col_title="Available Credit", new_value=available_credit)

    if previous_activity:
        card_upload.change_value_of_column(item_name=item_name, col_title="Previous Activity", new_value=previous_activity)

    current_user_id = card_upload.get_value_of_column_for_item(item_name=item_name, col_title="Card User ID")
    if user_id != current_user_id:
        card_upload.change_value_of_column(item_name=item_name, col_title="Card User ID", new_value=user_id)

    current_ending_digits = card_upload.get_value_of_column_for_item(item_name=item_name, col_title="Card Ending Digits")
    if ending_digits != current_ending_digits:
        card_upload.change_value_of_column(item_name=item_name, col_title="Card Ending Digits", new_value=ending_digits)

    current_card_name = card_upload.get_value_of_column_for_item(item_name=item_name, col_title="Card Name")
    if card_name != current_card_name:
        card_upload.change_value_of_column(item_name=item_name, col_title="Card Name", new_value=card_name)


def scrape_with_options(multiprocess=False, num_proc=3, account_ids=None):
    start_time = time.time()
    accounts_sheet_file_name = "accounts.xlsx"
    accounts_sheet_full_path = os.path.join(DATA_FILES_DIR, accounts_sheet_file_name)

    accounts_sheet_converted = convert_excel_to_list_of_dict(accounts_sheet_full_path)

    # FILTER LIST ACCORDING TO ACCOUNTS IF ACCOUNTS LIST IS PASSED AS PARAMETERS
    filtered_accounts_list = []
    if account_ids:
        print(f"LOG INFO: Will check for accounts {account_ids}")
        for user_id in account_ids:
            for login_account_detail in accounts_sheet_converted:
                if login_account_detail.get("user_id") == user_id:
                    filtered_accounts_list.append(login_account_detail)
                    break
        accounts_sheet_converted = filtered_accounts_list
    else:
        print(f"LOG INFO: Will check for all accounts in accounts sheet.")

    if multiprocess is True:
        # A LIST OF SMALLER LISTS
        results_list = runJobs(single_user_job, listInputs=accounts_sheet_converted, numberOfProcesses=num_proc)
    else:
        results_list = []  # A LIST OF SMALLER LISTS
        for account in accounts_sheet_converted:
            result = single_user_job(account)
            results_list.append(result)

    # FOR SAVING TO EXCEL
    list_of_jsons = []

    # USED AS RETURN VALUE (EASILY ACCESSIBLE OBJECTS)
    list_of_card_objects = []

    for user_card_group in results_list:
        for card_info_object in user_card_group:
            print(card_info_object)
            card_details_dict = collections.OrderedDict()
            card_details_dict['Card Identifier'] = card_info_object.card_identifier
            card_details_dict['Card User ID'] = card_info_object.user_id
            card_details_dict['Card Ending Digits'] = card_info_object.card_number
            card_details_dict['Card Name'] = card_info_object.card_name
            card_details_dict['Closing Date'] = card_info_object.closing_date
            card_details_dict['Payment Due'] = card_info_object.payment_due_amount
            card_details_dict['Payment Due Date'] = card_info_object.payment_due_date
            card_details_dict['Statement Balance'] = card_info_object.statement_balance
            card_details_dict['Total Balance'] = card_info_object.total_balance
            card_details_dict['Available Credit'] = card_info_object.available_credit
            card_details_dict['Previous Activity'] = card_info_object.previous_activity

            list_of_card_objects.append(card_info_object)
            list_of_jsons.append(card_details_dict)

    list_of_json_to_excel(jsonList=list_of_jsons, subdirectory_name="Amex_Card_Scraping_Results", fullDestfilename="Amex_card_info")
    duration = time.time() - start_time
    print(f"LOG INFO: Process completed in {duration} seconds")

    return list_of_card_objects


def run_main():
    cmd_args = argument_parser()

    if cmd_args.account:
        account_ids = cmd_args.account
    else:
        account_ids = None

    if cmd_args.multithreaded:
        num_proc = cmd_args.multithreaded
        multiprocess = True
        scrape_with_options(multiprocess=multiprocess, num_proc=num_proc, account_ids=account_ids)
    else:
        scrape_with_options(account_ids=account_ids)


if __name__ == "__main__":
    # test_case_single_user()
    run_main()
