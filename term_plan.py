from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support.expected_conditions import presence_of_element_located, \
    frame_to_be_available_and_switch_to_it, element_to_be_clickable
from tkinter import Tk, PhotoImage, Label, filedialog
import time
import pickle

root = Tk()
root.withdraw()

try:
    credentials = pickle.load(open("./credentials.p", "rb"))
except:
    credentials = [input('Enter RWeb Username: '), input('Enter RWeb Password: ')]
    if input('Do you want to save you credentials? (yes/no): ').lower == 'yes':
        pickle.dump(credentials, open("credentials.p", "wb"))

try:
    courses = pickle.load(open(filedialog.askopenfilename(initialdir="./schedules/", title="Open schedule",
                                                          filetypes=(("all files", "*.*"),)), "rb"))
    term = courses.pop('Term')
except:
    exit('Invalid schedule file! Run gui.py to create a schedule.')

url = 'https://auth.ucr.edu/cas/login'
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument(f'--window-size={root.winfo_screenwidth()},{root.winfo_screenheight()}')

driver = webdriver.Chrome('./chromedriver.exe', options=chrome_options)
wait = WebDriverWait(driver, 5)
driver.get(url)
print('ChromeDriver started')

""" Login """
WebDriverWait(driver, 3).until(presence_of_element_located((By.XPATH, '//input[@class="form-control required"]')))
login = driver.find_elements(By.XPATH, '//input[@class="form-control required"]')
login[0].send_keys(credentials[0])  # Username
login[1].send_keys(credentials[1])  # Password
driver.find_element(By.XPATH, '//button[@name="submit"]').click()  # Sign in
try:
    WebDriverWait(driver, 2).until(frame_to_be_available_and_switch_to_it((By.ID, "duo_iframe")))
    driver.find_element(By.XPATH, '//span[@class="label factor-label"]').click()
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
    time.sleep(2)
except Exception as e:
    pass
print(f'Login successful')

""" Term Plan """
""" Old code to select a term
url = 'https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/registration/registration'
driver.get(url)
wait.until(presence_of_element_located((By.XPATH, '//a[@id="planningLink"]')))
driver.find_element(By.XPATH, '//a[@id="planningLink"]').click()
driver.find_element(By.ID, 's2id_txt_term').click()
driver.find_element(By.XPATH, '//input[@id="s2id_autogen1_search"]').send_keys(term)
time.sleep(1)
driver.find_element(By.XPATH, '//input[@id="s2id_autogen1_search"]').send_keys(Keys.ENTER)
wait.until(presence_of_element_located((By.ID, 'term-go')))
driver.find_element(By.ID, 'term-go').click()
"""
driver.get(f'https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/term/search?mode=plan&dataType=json'
           f'&term={term}&studyPath=&studyPathText=&startDatepicker=&endDatepicker=')

""" Old code to create a new term plan
driver.get('https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/plan/selectPlan')
wait.until(presence_of_element_located((By.XPATH, '//button[@id="createPlan"]')))
driver.find_element(By.XPATH, '//button[@id="createPlan"]').click()
"""
driver.get('https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/plan/plan')

driver.find_element(By.ID, 'search-go').click()
for course in courses:
    print(f'Adding course {course} to term plan')
    wait.until(element_to_be_clickable((By.XPATH, '//button[@id="search-again-button"]')))
    time.sleep(1)
    driver.find_element(By.XPATH, '//button[@id="search-again-button"]').click()
    wait.until(element_to_be_clickable((By.XPATH, '//ul[@class="select2-choices"]')))
    # time.sleep(1)
    driver.find_element(By.XPATH, '//ul[@class="select2-choices"]').click()
    driver.find_element(By.ID, 's2id_autogen1').send_keys(Keys.BACKSPACE + Keys.BACKSPACE + course)
    time.sleep(1)
    driver.find_element(By.ID, 's2id_autogen1').send_keys(Keys.ENTER)
    wait.until(element_to_be_clickable((By.ID, 'search-go')))
    driver.find_element(By.ID, 'search-go').click()
    wait.until(element_to_be_clickable((By.XPATH, '//button[@class="form-button search-section-button"]')))
    # time.sleep(1)
    driver.save_screenshot("screenshot.png")
    driver.find_element(By.XPATH, '//button[@class="form-button search-section-button"]').click()
    wait.until(element_to_be_clickable((By.CLASS_NAME, 'page-size-select')))
    Select(driver.find_element(By.CLASS_NAME, 'page-size-select')).select_by_visible_text('50')
    for section in set(courses[course]):
        time.sleep(1)
        driver.find_element(By.XPATH, '//button[@id="' + f'addSection{term}{section}' + '"]').click()
    time.sleep(1)
    driver.find_element(By.XPATH, '//button[@id="saveButton"]').click()
    try:
        WebDriverWait(driver, 2).until(
            element_to_be_clickable((By.XPATH, '//div[@class="ui-dialog-buttonset"]/button[2]')))
        driver.find_element(By.XPATH, '//div[@class="ui-dialog-buttonset"]/button[2]').click()
    except:
        pass
    wait.until(element_to_be_clickable((By.XPATH, '//a[@class="form-button return-course-button"]')))
    driver.find_element(By.XPATH, '//a[@class="form-button return-course-button"]').click()
driver.find_element(By.XPATH, '//div[@class="btnToggleNorth ui-toggler-open ui-toggler"]').click()
driver.save_screenshot("./screenshot.png")
driver.close()

image = PhotoImage(file='./screenshot.png')
root.geometry(f'{root.winfo_screenwidth()}x{root.winfo_screenheight()}')
label = Label(root, compound="top", image=image)
label.pack()
root.deiconify()
root.mainloop()

sys.exit()
