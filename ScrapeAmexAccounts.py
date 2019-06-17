from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json
import time
import pyexcel
import datetime
import os
import re
import collections
from helper_functions.BrowserActions import enter_field_value, click_element, find_presence_of_element, get_element_text, get_number_of_elements, getHtmlElementObjectAsText


def login_user(driver, user, url):
    print("\nFn: \"login_user\" ")
    driver.get(url)
    time.sleep(5)
    pageTitle = driver.title
    if 'dashboard' in pageTitle.lower():
        print("Account Logged in")
        return


    try:
        inputUserID = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='eliloUserID']")))
        inputUserID.send_keys(user['Username'])
    except Exception as exc:
        print(exc)
        print("\nTrying again for userID field")
        inputUserID = None

    if inputUserID == None:
        try:
            inputUserID = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='lilo_userName']")))
            inputUserID.send_keys(user['Username'])
        except Exception as exc:
            print(exc)
            print("Error with sign in elements(userID)")

    try:
        inputPW = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='eliloPassword']")))
        inputPW.send_keys(user['UserPwd'])
    except Exception as exc:
        print(exc)
        print("\nTrying again for password field")
        inputPW = None

    if inputPW == None:
        try:
            inputPW = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='lilo_password']")))
            inputPW.send_keys(user['UserPwd'])
        except Exception as exc:
            print(exc)
            print("Error with sign in elements(Password)")

    try:
        loginButton = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
        loginButton.submit()
    except Exception as exc:
        print(exc)
        print("\nTrying again for login button")
        loginButton = None

    if loginButton == None:
        try:
            loginButton = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//input[@id='lilo_formSubmit']")))
            loginButton.submit()
        except Exception as exc:
            print(exc)
            print("Error with sign in elements(login button)")

    print("\nPage Loading....")
    time.sleep(5)
    print("Checking if page is logged in")
    pageTitle = driver.title
    if 'dashboard' in pageTitle.lower():
        print("Account Logged in")
        return True
    else:
        return False


def logout_user(driver):
    print("\nFn: \"logout_user\" ")
    driver.get('https://global.americanexpress.com/dashboard')
    try:
        logOut_button = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, "//*[text()[contains(.,'Log Out')]]")))
        logOut_button.click()
    except:
        print("error logging out")
    time.sleep(3)

    return None


def add_to_records(single_record, listofCardDetails):
    """Append record of a single order to list of records """
    print("\nFn: \"add_to_records\" ")
    try:
        listofCardDetails.append(single_record)
        print("record added")
        print("\nCurrent record ")
        print(json.dumps(single_record, indent=2))
        print("\n")
    except:
        print("record not added")
    return listofCardDetails


def crateCurrentRecord(paymentDueAmountFloat, totalBalanceFloat, statementBalanceFloat, creditAvailableFloat, recentPaymentCreditsFloat, nextClosingDateText, paymentRequiredOn, cardName="Null"):
    currentDealRecord = collections.OrderedDict()
    currentDealRecord['Card Name'] = cardName
    currentDealRecord['Total Balance'] = totalBalanceFloat
    currentDealRecord['Statement Balance'] = statementBalanceFloat
    currentDealRecord['Next Closing Date'] = nextClosingDateText
    currentDealRecord['Recent Payments and Credits'] = recentPaymentCreditsFloat
    currentDealRecord['Payment Amount Due'] = paymentDueAmountFloat
    currentDealRecord['Payment Required On'] = paymentRequiredOn
    currentDealRecord['Credit Available'] = creditAvailableFloat

    return currentDealRecord


def convertDate(nextClosingDate):
    print("Extracting month portion from date")
    monthRegex = re.compile(r'(\D+)')

    try:
        monthPortion = monthRegex.search(nextClosingDate).group(1).strip()
    except:
        print("Error extracting month portion")
        return nextClosingDate

    dayRegex = re.compile(r'\D+\s*(\d+)')
    try:
        dayPortion = dayRegex.search(nextClosingDate).group(1).strip()
    except:
        print("Error extracting day portion")
        return nextClosingDate

    datetext_to_digits = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                          'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                          'Sep': '09', 'Sept': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}

    try:
        for key in datetext_to_digits.keys():
            if key == monthPortion:
                next_closing_date_month = datetext_to_digits[key]
                print(next_closing_date_month)
                return f"{next_closing_date_month}/{dayPortion}"
            else:
                next_closing_date_month = nextClosingDate
                print("No match found yet")

    except Exception as exc:
        print(exc)
        print("\nError with month text to digit conversion")

    return nextClosingDate


def setChromeBroswer(profilefolder):
    path_to_dir = "C:/Chromeprofiles_CCAccounts"
    profilefolder = profilefolder
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('user-data-dir=' + path_to_dir)
    chrome_options.add_argument('--profile-directory=' + profilefolder)

    print("\nSetting Chrome Options.")
    driver = webdriver.Chrome(options=chrome_options)
    driver.delete_all_cookies()

    return driver


def navMainDashboard(driver):
    """
    FOR EACH CARD, WE NEED TO GET THE INFORMATION FROM EACH TAB.
    FUNCTION REPRESENTS ONE INSTANCE OF GETTING TAB INFORMATION
    """

    # TAB 1
    paymentBalanceTabXpath = "//div[contains(@class,'DynamicLayout')]//section[contains(@data-module-name,'axp-balance-summary')]"
    balanceTabText = get_element_text(driver, paymentBalanceTabXpath)

    if balanceTabText is None:
        paymentBalanceTabXpath = "//div[contains(@class,'DynamicLayout')]//section[contains(@data-module-name,'axp-activity-summary')]"
        balanceTabText = get_element_text(driver, paymentBalanceTabXpath)

    print(balanceTabText)

    try:
        paymentDueRegex = re.compile('Payment\s*Due[\s\S]*?\$([\d,.]+)')
        paymentDueAmountText = paymentDueRegex.search(balanceTabText).group(1).strip()
        paymentDueAmountFloat = float(paymentDueAmountText.replace(",", ""))
    except:
        paymentDueAmountFloat = None

    try:
        statementBalanceRegex = re.compile('Statement\s*Balance[\s\S]*?\$([\d,.]+)')
        statementBalanceText = statementBalanceRegex.search(balanceTabText).group(1).strip()
        statementBalanceFloat = float(statementBalanceText.replace(",", ""))
    except:
        try:
            statementBalanceRegex = re.compile('Previous\s*Activity[\s\S]*?\$([\d,.]+)')
            statementBalanceText = statementBalanceRegex.search(balanceTabText).group(1).strip()
            statementBalanceFloat = float(statementBalanceText.replace(",", ""))
        except:
            statementBalanceFloat = None

    try:
        totalBalanceRegex = re.compile('Total\s*Balance[\s\S]*?\$([\d,.]+)')
        totalBalanceText = totalBalanceRegex.search(balanceTabText).group(1).strip()
        totalBalanceFloat = float(totalBalanceText.replace(",", ""))
    except:
        try:
            totalBalanceRegex = re.compile('Recent\s*Activity[\s\S]*?\$([\d,.]+)')
            totalBalanceText = totalBalanceRegex.search(balanceTabText).group(1).strip()
            totalBalanceFloat = float(totalBalanceText.replace(",", ""))

            totalBalanceFloat = totalBalanceFloat + statementBalanceFloat
        except:
            totalBalanceFloat = None

    try:
        creditAvailableRegex = re.compile('Available[\s\S]*?\$([\d,.]+)')
        creditAvailableText = creditAvailableRegex.search(balanceTabText).group(1).strip()
        creditAvailableFloat = float(creditAvailableText.replace(",", ""))
    except:
        creditAvailableFloat = 0.00

    # DETAILS UNDER TAB 1
    balanceDetailsTab1Xpath = "//button[contains(@title,'Details')]"
    click_element(driver, balanceDetailsTab1Xpath, pause_after_action=2)

    detailsTextXpath = "//table[@class='balance-details-list']"
    balanceDetailsText = get_element_text(driver, detailsTextXpath)
    print(balanceDetailsText)

    try:
        statementPeriodRegex = re.compile(r'Statement\sBalance\s*(.+)')
        statementPeriodText = statementPeriodRegex.search(balanceDetailsText).group(1).strip()
    except:
        statementPeriodText = "Null"

    print(f"Statement Period: {statementPeriodText}")

    if statementBalanceFloat is None:
        try:
            statementBalanceRegex = re.compile(r'Statement\sBalance[\s\S]*?\$([\d,.]+)')
            statementBalanceText = statementBalanceRegex.search(balanceDetailsText).group(1).strip()
            statementBalanceFloat = float(statementBalanceText.replace(",", ""))
        except:
            statementBalanceFloat = 0.00

    try:
        recentPaymentCreditsRegex = re.compile(r'Recent\s*Payment[\s\S]*?\$([\d,.]+)')
        recentPaymentCreditsText = recentPaymentCreditsRegex.search(balanceDetailsText).group(1).strip()
        recentPaymentCreditsFloat = float(recentPaymentCreditsText.replace(",", ""))
    except:
        recentPaymentCreditsFloat = 0.00

    if paymentDueAmountFloat is None:
        try:
            paymentDueRegex = re.compile(r'Payment\s*Due[\s\S]*?=\s*\$([\d.,]+)')
            paymentDueAmountText = paymentDueRegex.search(balanceDetailsText).group(1).strip()
            paymentDueAmountFloat = float(paymentDueAmountText.replace(",", ""))
        except:
            paymentDueAmountFloat = 0.00

    try:
        nextClosingDateRegex = re.compile(r'Next\s*Closing\sDate\s*(.+?)\)')
        nextClosingDateText = nextClosingDateRegex.search(balanceDetailsText).group(1).strip()
    except:
        nextClosingDateText = "Null"

    nextClosingDateText = convertDate(nextClosingDateText)

    if totalBalanceFloat is None:
        try:
            totalBalanceRegex = re.compile(r'Total\s*Balance[\s\S]*?=\s*\$([\d,.]+)')
            totalBalanceText = totalBalanceRegex.search(balanceDetailsText).group(1).strip()
            totalBalanceFloat = float(totalBalanceText.replace(",", ""))
        except:
            totalBalanceFloat = 0.00

    print("\nRESULTS FROM TAB 1/TAB 1 DETAILS****************************************")
    print(f"Payment Due: {paymentDueAmountFloat}")
    print(f"Total Balance: {totalBalanceFloat}")
    print(f"Statement Balance: {statementBalanceFloat}")
    print(f"Credit Available: {creditAvailableFloat}")
    print(f"Recent Payments and Credits: {recentPaymentCreditsFloat}")
    print(f"Next Closing Date: {nextClosingDateText}")

    # BACK TO MAIN PAGE
    backToMainPageXpath = '//button[@title="Return to summary"]'
    click_element(driver, backToMainPageXpath, pause_after_action=2)

    if nextClosingDateText == "Null":
        activityContainerXpath = '//div[@class="activity-container"]'
        activityContainerText = get_element_text(driver,activityContainerXpath)

        try:
            nextClosingDateRegex = re.compile(r'Closing\s+(\w+\s+\d+)')
            nextClosingDateText = nextClosingDateRegex.search(activityContainerText).group(1).strip()
        except:
            nextClosingDateText = "Null"

        nextClosingDateText = convertDate(nextClosingDateText)
        print(f"Next Closing Date: {nextClosingDateText}")


    # TAB 2
    paymentRequiredTabXpath = "//div[contains(@class,'DynamicLayout')]//section[contains(@data-module-name,'axp-payment-summary')]"
    paymentrequiredText = get_element_text(driver, paymentRequiredTabXpath)
    # print(paymentrequiredText)

    try:
        paymentRequiredOnRegex = re.compile(r'(not\s+required.+)')
        paymentRequiredOn = paymentRequiredOnRegex.search(paymentrequiredText).group(1).strip()
    except:
        try:
            paymentRequiredOnRegex = re.compile(r'Payment[\s\S]*?Due\s*on\s*(.+)')
            paymentRequiredOn = paymentRequiredOnRegex.search(paymentrequiredText).group(1).strip()
        except:
            try:
                paymentRequiredOnRegex = re.compile(r'Pay\s*By\s*(.+)')
                paymentRequiredOn = paymentRequiredOnRegex.search(paymentrequiredText).group(1).strip()
            except:
                paymentRequiredOn = "Null"

    print("\nRESULTS FROM TAB 2****************************************")
    print(f"Payment Required On: {paymentRequiredOn}")

    cardInfo = crateCurrentRecord(paymentDueAmountFloat, totalBalanceFloat, statementBalanceFloat, creditAvailableFloat, recentPaymentCreditsFloat, nextClosingDateText, paymentRequiredOn,
                                  cardName="Null")

    return cardInfo


def openCardSwitcherAll(driver):
    # Check for multiple cards
    # Open card switcher account
    cardAccountAwitcherXpath = "//button[contains(@class,'accountSwitcher')]"
    clickCardSwitcherOk = click_element(driver, cardAccountAwitcherXpath, pause_after_action=1)
    if clickCardSwitcherOk is False:
        print("Error clicking card switcher")

    cardsViewAllXpath = "//*[@title='View All']"
    clickViewAllOk = click_element(driver, cardsViewAllXpath, pause_after_action=1)
    if clickViewAllOk is False:
        print("No View all Pane found")


def get_AmexBal_main():
    amexAcc_MgrURL = 'https://global.americanexpress.com/login?inav=iNavLnkLog'

    # Open list of accounts
    amexAccounts = json.load(open('AmexAccounts.json'))

    # Define empty list for card details obtained.
    listofCardDetails = []
    idx = 1

    for user in amexAccounts:
        print(f"PROCESSING ACCOUNT {idx}")
        userProfile = user['Username']
        print(f"\nCURRENT ACCOUNT USERNAME {userProfile}\n=============================================")
        driver = setChromeBroswer(userProfile)
        loginAccountOk = login_user(driver, user, amexAcc_MgrURL)
        if loginAccountOk is False:
            print("Login information incorrect")
            driver.quit()
            idx += 1
            continue

        # Check for multiple cards
        openCardSwitcherAll(driver)

        # Find out number of card accounts
        cardAccountsXpath = '(//section[contains(@class,"account-row")])'
        numberOfCards = get_number_of_elements(driver, cardAccountsXpath)
        if numberOfCards is None:
            print("Error getting number of cards")
        else:
            print(f"Number of Card Accounts: {numberOfCards}")

            for idx in range(1, numberOfCards + 1):
                cardName = "Null"
                singleCardAccountXpath = f"{cardAccountsXpath}[{idx}]"
                selectSingleCardAccountOk = click_element(driver, singleCardAccountXpath)

                # Open Card Switcher View
                openCardSwitcherAll(driver)

                if selectSingleCardAccountOk is True:
                    print("Single Card Account Selected")
                    currentCardElement = getHtmlElementObjectAsText(driver, singleCardAccountXpath)
                    if currentCardElement is not None:
                        print("Getting card information")
                        cardNameRegex = re.compile(r'productDescription[\s\S]*?title="[\s\S]*?>(.+?)<')
                        try:
                            cardName = cardNameRegex.search(currentCardElement).group(1).strip()
                            cardName = cardName.replace("(", "")
                            cardName = cardName.replace(")", "")
                        except:
                            cardName = "Null"

                # Close Card Switcher
                selectSingleCardAccountOk = click_element(driver, singleCardAccountXpath)

                print(f"Card Name: {cardName}")
                cardInfo = navMainDashboard(driver)
                cardInfo['Card Name'] = cardName
                cardInfo['Card Login'] = userProfile

                add_to_records(cardInfo, listofCardDetails)

                # Open Card Switcher view again
                openCardSwitcherAll(driver)

        driver.quit()
        idx += 1

    print(listofCardDetails)

    # This will format the current time at a string so that we can append it to the file name
    moment = time.strftime("%Y-%b-%d__%H_%M_%S", time.localtime())

    try:
        # Define the destination file name and save to the destination
        fileName = f"Card_Details_at_{moment}.xlsx"
        directoryName = "C:/AmexCardDetails/"
        dest_file_name = f"{directoryName}{fileName}"

        pyexcel.save_as(records=listofCardDetails, dest_file_name=dest_file_name)
        print(f"File Saved to {dest_file_name}")
    except:
        print("Specified path not present. Making path.")
        directoryName = "C:/AmexCardDetails/"
        os.mkdir(directoryName)
        print("Directory created.")
        try:
            # Define the destination file name and save to the destination
            fileName = f"Card_Details_at_{moment}.xlsx"
            directoryName = "C:/AmexCardDetails/"
            dest_file_name = f"{directoryName}{fileName}"

            pyexcel.save_as(records=listofCardDetails, dest_file_name=dest_file_name)
            print(f"File Saved to {dest_file_name}")
        except:
            print("Failed to save results")


if __name__ == '__main__':
    get_AmexBal_main()
