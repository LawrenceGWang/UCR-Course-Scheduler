from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support.expected_conditions import presence_of_element_located, frame_to_be_available_and_switch_to_it
import time
import pickle
import sys

try:
    credentials = pickle.load(open("./credentials.p", "rb"))
    courses = pickle.load(open("./pickles/final.p", "rb"))
    term = courses.pop('Term')
except:
    credentials = [input('Enter RWeb Username: '), input('Enter RWeb Password: ')]
    pickle.dump(credentials, open("credentials.p", "wb"))

url = 'https://rweb.ucr.edu'
chrome_options = Options()
# chrome_options.add_argument('--headless')

driver = webdriver.Chrome('./chromedriver.exe', options=chrome_options)
wait = WebDriverWait(driver, 10)
driver.get(url)
print('ChromeDriver started')

""" Login """
try:
    wait.until(presence_of_element_located((By.XPATH, '//input[@class="form-control required"]')))
except:
    print('Too long')
login = driver.find_elements(By.XPATH, '//input[@class="form-control required"]')
login[0].send_keys(credentials[0])  # Username
login[1].send_keys(credentials[1])  # Password
driver.find_element(By.XPATH, '//button[@name="submit"]').click()  # Sign in
wait.until(frame_to_be_available_and_switch_to_it((By.ID, "duo_iframe")))
try:
    driver.find_element(By.XPATH, '//span[@class="label factor-label"]').click()
except:
    pass
select_device = driver.find_elements(By.XPATH, '//select[@name="device"]/option')
devices = [device.text for device in select_device]
print(f'Select a device (0 - {len(devices)}):')
for i, device in enumerate(devices):
    print(f'{i}) {device}')
driver.find_element(By.XPATH, '//select[@name="device"]/option[text()="' + devices[int(input())] + '"]').click()
time.sleep(1)
driver.find_element(By.XPATH, '//button[@id="message"]').click()  # Text me new codes
driver.find_element(By.XPATH, '//input[@name="passcode"]').send_keys(input('Enter 2FA code: '))
driver.find_element(By.XPATH, '//button[@id="passcode"]').click()
driver.switch_to.default_content()

time.sleep(3)

""" Term Plan """
url = 'https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/registration/registration'
driver.get(url)
try:
    wait.until(presence_of_element_located((By.XPATH, '//a[@id="planningLink"]')))
except:
    print('Too long')
driver.find_element(By.XPATH, '//a[@id="planningLink"]').click()
driver.find_element(By.ID, 's2id_txt_term').click()
driver.find_element(By.XPATH, '//input[@id="s2id_autogen1_search"]').send_keys(term)
time.sleep(1)
driver.find_element(By.XPATH, '//input[@id="s2id_autogen1_search"]').send_keys(Keys.ENTER)
wait.until(presence_of_element_located((By.ID, 'term-go')))
driver.find_element(By.ID, 'term-go').click()
wait.until(presence_of_element_located((By.XPATH, '//button[@id="createPlan"]')))
driver.find_element(By.XPATH, '//button[@id="createPlan"]').click()
driver.find_element(By.ID, 'search-go').click()

for course in courses:
    driver.find_element(By.XPATH, '//button[@id="search-again-button"]').click()
    driver.find_element(By.XPATH, '//div[@id="s2id_txt_subjectcoursecombo"]').click()
    courseelem = driver.find_element(By.ID, 's2id_autogen1').send_keys(course)
    time.sleep(1)
    courseelem = driver.find_element(By.ID, 's2id_autogen1').send_keys(Keys.ENTER)
    time.sleep(1)
    driver.find_element(By.ID, 'search-go').click()
    driver.find_element(By.XPATH, '//button[@class="form-button search-section-button"]').click()
    Select(driver.find_element(By.CLASS_NAME, 'page-size-select')).select_by_visible_text('50')

    for i, row in enumerate(driver.find_elements(By.XPATH, '//table[@id="table1"]/tbody/tr')):
        print(row.find_element(By.XPATH, 'td[@data-property="courseReferenceNumber"]').text)



sys.exit()

driver.find_element(By.ID, 's2id_txt_term').click()
time.sleep(1)
termslist = driver.find_element(By.ID, 'select2-results-1').find_elements(By.TAG_NAME, 'li');
if userterm == '':
    termslist[0].click()
else:
    for termoption in termslist:
        if userterm in termoption.text:
            termoption.click()
            break
time.sleep(1)
try:
    driver.find_element(By.ID, 'term-go').click()
except:
    sys.exit('Invalid term!')
time.sleep(2)
print('Term selected')

""" BROWSE CLASSES """
driver.find_element(By.ID, 's2id_txt_subjectcoursecombo').click()
courseelem = driver.find_element(By.ID, 's2id_autogen1')
time.sleep(1)
courseelem.send_keys(course)
time.sleep(1)
courseelem.send_keys(Keys.RETURN)
time.sleep(1)
try:
    driver.find_element(By.ID, 'search-go').click()
except:
    print('Course not found')
    raise Exception(f'Course {course} not found!')
print(f'Course {course} selected')

time.sleep(2)

Select(driver.find_element(By.CLASS_NAME, 'page-size-select')).select_by_visible_text('50')
time.sleep(2)
table = driver.find_element(By.ID, 'table1')
for i, row in enumerate(table.find_elements(By.TAG_NAME, 'tr')):
    l1 = list()
    for td in row.find_elements(By.TAG_NAME, 'td'):
        if td.text == '':
            l1.append(td.get_attribute('innerHTML'))
        else:
            l1.append(td.text)
    if not l1 or 'FULL' in l1[9].split()[0]:
        continue
    days = []
    for day in row.find_elements(By.XPATH,
                                 './td[@data-property="meetingTime"]/div/div/ul/li[@class="ui-state-default ui-state-highlight"]'):
        days.append(day.get_attribute('data-name'))
    ctime = row.find_element(By.XPATH, './td[@data-property="meetingTime"]/div/span').text
    # print(f'{l1}\n\n')
    all.append((days, ctime, l1))
    sys.stdout.write("\r")
    sys.stdout.write(f"Scraped {i} sections")
    sys.stdout.flush()
print('\nSection scraping finished')
driver.close()