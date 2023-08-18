import time
import argparse
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import random

## to do >> handle if the ticket time is 00:00 or 00:15
## to do >> add come back at done
## beutiful output
## handle if password is wrong!!

file_path = "D:\password_tts.txt"
if not os.path.exists(file_path):
    print("TTS Credentials not found!\nWrite it only this time ..")
    with open(file_path, 'w') as f:
        username = input("Enter TTS username: ")
        password = input("Enter TTS password: ")
        f.write(f"{username}\n{password}")
os.system('color')


current_time = time.strftime("%H:%M", time.localtime())
def calculate_times(pool_time,pc_time= current_time):
    # simple input time >> 16:20
    pool_time =pool_time.split('.')[0]
    pool_time = pool_time[:5]
    h1, m1 = map(int, pc_time.split(':'))
    h2, m2 = map(int, pool_time.split(':'))
    # adding two hours to pool_time (SLA)
    h2 += 2
    # Convert the pool_time  to minutes and subtract it from the current_time (PC time)
    current_time_minutes = h1 * 60 + m1
    pool_time_minutes = h2 * 60 + m2
    remaining_time_minutes = pool_time_minutes - current_time_minutes
    # convert the remaining time minutes to hours
    remaining_hours = remaining_time_minutes // 60
    remaining_time_minutes %= 60
    return f'{remaining_hours:02d}:{remaining_time_minutes:02d}'
def add_times(time1, time2):
    hours1, minutes1 = map(int, time1.split(':'))
    hours2, minutes2 = map(int, time2.split(':'))
    total_minutes = (minutes1 + minutes2) % 60
    total_hours = hours1 + hours2 + (minutes1 + minutes2) // 60
    return '{:02d}:{:02d}'.format(total_hours, total_minutes)
def arrange(adict):
    #from smallest to biggest
    return dict(sorted(adict.items(), key=lambda item: item[1]))
"""
this funcion takes the o/p dictionary from scarping and turn it to a list ... 
it have on argument x >> represents the number of returned list (tickets have least time)
"""
def format_dic(data, x):
    if len(data) < x :
        x = len(data)
    formatted = []
    for key, value in data.items():
        formatted.append(
            "Account," + key + "," + value[1] + ",Remaining Time," + value[0] + ",Type," + value[2] + ",Count," + value[
                3]+ " Come back at " + add_times(current_time,value[0]))
        if len(formatted) == x:
            return formatted

"""
This function takes the transfered list from format_dic function and split it with delimeter ',' and then print the tickets.
"""
def print_account_list(formatted_list):
    for line in formatted_list:
        parts = line.split(',')
        account_str = f"{parts[0]} {parts[1]}"
        type_str = f"{parts[2]}"
        time_str = " ".join(parts[3:4])
        the_time = parts[4]
        product_count = f" ".join(parts[6:])
        print(f"{account_str.ljust(20)} {type_str.ljust(20)} {time_str.rjust(20)}" + " " + check_time_color(
            the_time) + " " + " " + product_count)

def check_time_color(the_time):
    x_hours, x_minutes = map(int, the_time.split(':'))
    if x_hours == 00 and x_minutes < 20:
        return f"\033[31m{the_time}\033[0m"  # red
    else:
        return f"\033[32m{the_time}\033[0m"  # return in green

############### continue with the reset of report ##########################
"""
This function takes all tickets dictionary and output all tickets ((in order)) 
"""
def TTS_Report(d):
    count_dict = {}
    for val in d.values():
        key = val[1]
        type_val = val[2]
        if key in count_dict:
            if type_val in count_dict[key]:
                count_dict[key][type_val] += 1
            else:
                count_dict[key][type_val] = 1
        else:
            count_dict[key] = {type_val: 1}
    for key, nested_dict in count_dict.items():
        print(f"{key}:")
        for type_val, count in nested_dict.items():
            print(f"  {type_val}: {count}")

"""
This function used to check if there is a global (repeated exchange or not)
"""
def check_global(d):
    count_dict = {}
    for key in d:
        value = d[key]
        if value[4] in count_dict:
            count_dict[value[4]] += 1
        else:
            count_dict[value[4]] = 1
    for k, v in count_dict.items():
        if v >= 3:
            if v > 3:
                return f"There is a global at {k}"
            else:
                return f"There might be a global check {k}"
    return "No global found"
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/90.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/90.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
]
def TTS_Scraping():
    with open(r'D:\password_tts.txt', mode='r') as up:
        lu = up.readline()
        lp = up.readline()
        u = lu.replace('\n', '')
        p = lp.replace('\n', '')

    # initialize the Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    #options.add_argument(
     #   "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36")
    random_user_agent = random.choice(user_agents)
    options.add_argument(f'user-agent={random_user_agent}')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    # navigate to the website
    print("Opening TTS ...")
    driver.get("http://tts/")
    # time.sleep(10)
    wait = WebDriverWait(driver, 20)
    search_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "(//input[contains(@name, 'access_user_name')])")))
    search_input.send_keys(u)
    search_input1 = driver.find_element('xpath', "(//input[contains(@name, 'access_password')])")
    search_input1.send_keys(p)
    search_btn = driver.find_element('xpath', "(//input[contains(@name, 'Login')])")
    search_btn.click()
    time.sleep(2)
    print("Logged in!")
    time.sleep(2)
    # navigate to the page that contains the data
    driver.get(
        "http://tts/index.php?controller=app_oneorzeroreportmanager_main&subcontroller=app_oneorzeroreportmanager_manage&option=bulkUpdate&id=7")
    # extract the data
    tickets = driver.find_elements('xpath', "//tr[contains(@class,'trc')][contains(@style,'display:visible;')]")
    print("Getting all tickets and building the Report ... ")
    data = {}

    for items in tickets:
        Product = items.find_element('xpath', ".//td[8]").text # ADSL // VDSL // FTTH
        Category = items.find_element('xpath', ".//td[13]").text # Logical//Unable//Browsing//Speed
        GroupCount = items.find_element('xpath', ".//td[16]").text
        AccountNum = items.find_element('xpath', ".//td[1]").text
        TicketTitle = items.find_element('xpath', ".//td[4]").text # Logical//Unable//Browsing//Speed
        TransferDate = items.find_element('xpath', ".//td[5]").text.strip(".000000")
        TransferDate = TransferDate.split()
        Exchange = items.find_element('xpath', ".//td[6]").text
        Status = items.find_element('xpath', ".//td[7]").text  # Open//Automation//
        DSLAM_Num = items.find_element('xpath', ".//td[10]").text
        Card = items.find_element('xpath', ".//td[11]").text
        Port = items.find_element('xpath', ".//td[12]").text
        TicketNumber = items.find_element('xpath', ".//td[14]/a").text
        value = [calculate_times(TransferDate[1]),Category,Product,GroupCount,Exchange]
        data[AccountNum] = value
        #data.append([AccountNum, GroupCount, Status, Product, TicketTitle, TransferDate, Category])

    return data

# test from here and comment the rest
#all_tickets = arrange(TTS_Scraping())
#print(all_tickets)


parser = argparse.ArgumentParser(description='TTS Reporter by Abuelyouser')
parser.add_argument('-r', action='store_true', help='Display full report')
parser.add_argument('-n', type=int, help='number of tickets default is 3')
parser.add_argument('-G', action='store_true', help='Check global')


args = parser.parse_args()

all_tickets = arrange(TTS_Scraping())

print('\n' + "[!] collect time is : " + current_time + " [!]\n")

print('number of all tickets are  ' + str(len(all_tickets)))


if args.n:
    print_account_list(format_dic(all_tickets,args.n))
if args.r:
    TTS_Report(all_tickets)
if args.G:
    print(check_global(all_tickets))

if not args.n and not args.r and not args.G:
    print_account_list(format_dic(all_tickets,3))
