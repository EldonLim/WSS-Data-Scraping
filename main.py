from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys  # to give us access to enter key, escape key, etc
import os
import dotenv
from datetime import datetime
import requests
import urllib.parse


dotenv.load_dotenv()
PATH = "C:\Program Files (x86)\chromedriver-win64\chromedriver.exe"

cService = webdriver.ChromeService(executable_path=PATH)   # instantiate
options = webdriver.ChromeOptions()  # instantiate      
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service = cService, options=options)

driver.get("https://venus.wis.ntu.edu.sg/WSS2/Student/ViewAvailableJob.aspx")

def Initialization():
    #-------------------------------------------------------------------------------
    # Username Input Page

    userNameSearch = driver.find_element(By.CSS_SELECTOR, '[name="UserName"]')
    userNameSearch.send_keys('eldo0001')

    domainSearch = driver.find_element(By.CSS_SELECTOR, '[name="Domain"]')
    select = Select(domainSearch)
    select.select_by_value("STUDENT")


    submitSearch = driver.find_element(By.CSS_SELECTOR, '[name="bOption"]')
    submitSearch.click()

    #--------------------------------------------------------------------------------
    # Password Input Page

    passwordSearch = driver.find_element(By.CSS_SELECTOR, '[name="PIN"]')
    passwordSearch.send_keys(os.environ["PASSWORD"])

    submitSearch = driver.find_element(By.CSS_SELECTOR, '[name="bOption"]')
    submitSearch.click()

    #--------------------------------------------------------------------------------
    # Access View Available Assignments Window

    driver.find_element(By.ID, 'ctl00_detail_menuControlStud1_tvCoordt3').click()

    # Store the ID of this window to change tab
    global originalTab 
    originalTab = driver.current_window_handle


# #--------------------------------------------------------------------------------

def ExtractInfo(WorkNo: str) -> bool:
    # Extracting Information from New Job
    AssignmentNo = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, f'{WorkNo}')))
    AssignmentNo = driver.find_element(By.LINK_TEXT, f'{WorkNo}')  
    AssignmentNo.click()
    
    # Change Tabs control
    for window_handle in driver.window_handles:
        if window_handle != originalTab:
            driver.switch_to.window(window_handle)
            break

    driver.implicitly_wait(5)
    Category = driver.find_element(By.ID, "ctl00_detail_ucJobMain1_lblJobCategory").text
    Nature = driver.find_element(By.ID, "ctl00_detail_ucJobMain1_lblJobNature").text
    StartDate = driver.find_element(By.ID, "ctl00_detail_ucJobMain1_lblStartDt").text
    EndDate = driver.find_element(By.ID, "ctl00_detail_ucJobMain1_lblEndDt").text
    Salary = driver.find_element(By.ID, "ctl00_detail_ucJobMain1_lblSalary").text
    Skills = driver.find_element(By.ID, "ctl00_detail_ucJobMain1_lblSkills").text
    
    # URL ENCODING 
    # In URLs, & is used to separate query parameters.
    # If your message content is part of a URL or a query string, the & symbol needs to be URL-encoded as %26
    response = f"Assignment Number: {WorkNo}\n\nCategory: {Category}\n\nNature of Assignment: {Nature}\n\nStart Date: {StartDate}\n\nEnd Date: {EndDate}\n\nSalary: {Salary}\n\nSkills Required: {Skills}\n"
    
    # To check if the assignment has been sent before or no
    # try:
    #     data = load_assignment(fileName)
    #     if data == response:
    #       save_assignment(response, fileName)
    #       print("DONE")
    #       sys.exit('PROGRAM TERMINATED')   # cannot use try except as sys.exit() will raise an exception
    # except:
    #     save_assignment(response, fileName)

    data = load_assignment(fileName)
    if data == response:
        return False
    else:
        save_assignment(response, fileName)

    safeResponse = urllib.parse.quote(response)

    send_msg(safeResponse)

    # Close this tab
    driver.close()
    driver.switch_to.window(originalTab)
    return True

def AddLatestJob():
    # This function will return a list for newAssignments

    count=0 # To store the count on how many job is posted today
    dateList = [] # To store date
    AllAssignments = []
    spanElements = wait.until(EC.element_to_be_clickable((By.TAG_NAME, "Span")))
    spanElements = driver.find_elements(By.TAG_NAME, "Span")
    for i in range(7, len(spanElements)):
        dateList.append(spanElements[i].text[0:5])
    
    for date in dateList:
        if date == datetime.today().strftime('%d/%m'):
            count += 1

    aElements = wait.until(EC.element_to_be_clickable((By.TAG_NAME,'a')))
    aElements = driver.find_elements(By.TAG_NAME,'a')
    for i in range(len(aElements)):
        if aElements[i].text[0:3] == "WS-":
            AllAssignments.append(aElements[i].text)

    for i in range(5,8):
        NewAssignments.append(AllAssignments[i])


def send_msg(text):
   # To send the updates to our telegram bot
   token = os.environ['TELEGRAMTOKEN']
   # chat_id = "1061810735" this is private chat
   # The below chat_id is group chat id
   chat_id = '-1002247369753'
   url_req = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}" 
   results = requests.get(url_req)
   print(results.json())

def save_assignment(text: str, fileName: str):
    with open(fileName, 'w') as f:
            f.write(text)

    
def load_assignment(fileName: str) -> str:   # if file is empty will have error so use try except
    with open(fileName, 'r') as f:
        return f.read()

# Global Variables
NewAssignments = []
fileName = 'database.txt'

def main():

    Initialization()
    global wait 
    wait = WebDriverWait(driver, 10)
    AddLatestJob()

    newJob = True
    if NewAssignments:
        send_msg("New Jobs Incoming!")
        for Assignment in NewAssignments:
            if newJob == True:
                newJob = ExtractInfo(Assignment)
            else:
                break

main()


        
