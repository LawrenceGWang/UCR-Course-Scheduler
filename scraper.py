import json

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support.expected_conditions import presence_of_element_located
import time
import sys

chrome_options = Options()
chrome_options.add_argument('--headless')


""" Pure Selenium solution 
    No reason to use this if requests solution works
    Runtime: ~25 seconds
"""
def getCourseDataSelenium(userterm, course):
    url = 'https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/term/termSelection?mode=search'
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
        for day in row.find_elements(By.XPATH,
                                     './td[@data-property="meetingTime"]/div/div/ul/li[@class="ui-state-default ui-state-highlight"]'):
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


""" Hybrid Selenium/Requests solution 
    Use if pure requests version breaks
    Runtime: ~8 seconds
"""
def getCourseDataHybrid(userterm, course):
    url = 'https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/term/termSelection?mode=search'
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
    seasons = {'Winter': 10, 'Spring': 20, 'Summer': 30, 'Fall': 40}
    jsonurl = f'https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/searchResults/searchResults?txt_subjectcoursecombo={course}&txt_term={term[1]}{seasons[term[0]]}&startDatepicker=&endDatepicker=&pageOffset=0&pageMaxSize=999&sortColumn=subjectDescription&sortDirection=asc&[object%20Object]'
    driver.get(jsonurl)
    content = driver.page_source
    content = driver.find_element_by_tag_name('pre').text
    parsed_json = json.loads(content)
    list1 = [f for f in parsed_json['data'] if f['seatsAvailable']]
    for l in list1:
        print(l['courseReferenceNumber'], l['openSection'])


class rweb_session():
    def __init__(self):
        terms_url = 'https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/classSearch/getTerms?dataType=json&searchTerm=&offset=1&max=9999'
        self.term_codes = requests.get(terms_url).json()

    def init_term(self, _term):
        if not _term:
            self.term_code = self.term_codes[0]['code']
        for t in self.term_codes:
            if _term in t['description']:
                self.term_code = t['code']
                class_url = f'https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/courseSearch/get_subjectcoursecombo?dataType=json&searchTerm=&term={self.term_code}&offset=1&max=9999'
                self.course_codes = [c['code'] for c in requests.get(class_url).json()]
                return True
                break
        else:
            return False

    def is_valid_course(self, course):
        return course.upper() in self.course_codes

    """ Pure Requests solution 
        Try this first
        Runtime: ~0.5 seconds
    """
    def get_course_data(self, course):
        s = requests.Session()
        s.get(
            'https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/term/search?mode=search&dataType=json&term=202040&studyPath=&studyPathText=&startDatepicker=&endDatepicker=')
        jsonurl = f'https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/searchResults/searchResults?txt_subjectcoursecombo={course}&txt_term={self.term_code}&startDatepicker=&endDatepicker=&pageOffset=0&pageMaxSize=999&sortColumn=subjectDescription&sortDirection=asc&[object%20Object]'
        parsed_json = s.get(jsonurl).json()
        class_data = [row for row in parsed_json['data'] if row['seatsAvailable']]
        return class_data


""" For testing """
if __name__ == '__main__':
    session = rweb_session()


    # for t in session.term_codes:
    #     print(t)

    # if not session.init_term('Fall 2020'):
    #     print('Invalid term!')
    # if session.is_valid_course('PHYS040A'):
    #     for a in session.get_course_data('PHYS040A'):
    #         print(a)
    # term_text_to_code('Fall 2020')
    # getCourseData('Fall 2020', 'PHYS040A')
