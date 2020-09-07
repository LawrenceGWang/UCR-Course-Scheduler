import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support.expected_conditions import presence_of_element_located
import time
import sys


url = 'https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/term/termSelection?mode=search'

chrome_options = Options()
chrome_options.add_argument('--headless')
    
def getCourseData(userterm, course):
    start_time = time.perf_counter()
    driver = webdriver.Chrome('./chromedriver.exe', options=chrome_options)
    wait = WebDriverWait(driver, 10)
    driver.get(url)
    print('ChromeDriver started')
    
    """ CHOOSE TERM """
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
    term = driver.find_element(By.XPATH, '//label[@for="txt_term"]').text.split(': ')[1].split()
    driver.find_element(By.ID, 's2id_txt_subjectcoursecombo').click()
    courseelem = driver.find_element(By.ID, 's2id_autogen1')
    time.sleep(1)
    courseelem.send_keys(course)
    time.sleep(1)
    courseelem.send_keys(Keys.RETURN)
    try:
        driver.find_element(By.ID, 'search-go').click()
    except:
        print('Course not found')
        raise Exception(f'Course {course} not found!')
    print(f'Course {course} selected')
    
    time.sleep(2)

    
    Select(driver.find_element(By.CLASS_NAME, 'page-size-select')).select_by_visible_text('50')
    time.sleep(2)
    all = []
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
        for day in row.find_elements(By.XPATH, './td[@data-property="meetingTime"]/div/div/ul/li[@class="ui-state-default ui-state-highlight"]'):
            days.append(day.get_attribute('data-name'))
        ctime = row.find_element(By.XPATH, './td[@data-property="meetingTime"]/div/span').text
        # print(f'{l1}\n\n')
        all.append((days, ctime, l1, term))
        sys.stdout.write("\r")
        sys.stdout.write(f"Scraped {i} sections")
        sys.stdout.flush()
    print('\nSection scraping finished')
    driver.close()
    print(time.perf_counter() - start_time)
    return all

if __name__ == '__main__':
    getCourseData('Fall 2020', 'PHYS040A')