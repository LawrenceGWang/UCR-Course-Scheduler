import json
import pickle
import sys
from tkinter import filedialog

import requests
from lxml import html

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('Usage:\tterm_plan.py [<schedule_path> / manual]'
                 '\n\t(Use generated schedule or manually input term and courses)')

    if 'manual' in sys.argv[1]:
        courselist = []
        term_txt = input('Enter course (e.g. Fall 2020): ').split()
        semester_dict = {'winter': '10', 'spring': '20', 'summer': '30', 'fall': '40'}
        term = term_txt[1] + semester_dict[term_txt[0].lower()]
        print('Type q to quit')
        while True:
            course_in = input('Enter a CRN: ')
            if 'q' in course_in:
                break
            elif course_in.isnumeric():
                courselist.append(course_in)
            else:
                print('Invalid CRN')
    else:
        try:
            courses = pickle.load(open(filedialog.askopenfilename(initialdir="./schedules/", title="Open schedule",
                                                                  filetypes=(("All Files", "*.*"),)), "rb"))
            term = courses.pop('Term')
            courselist = set([crn for key in courses for crn in courses[key]])
            print(courselist)
        except(FileNotFoundError, TypeError):
            sys.exit('Invalid schedule file! Run gui.py to create a schedule.')

    try:
        credentials = pickle.load(open("credentials.p", "rb"))
    except FileNotFoundError:
        credentials = [input('Enter RWeb Username: '), input('Enter RWeb Password: ')]
        if 'yes' in input('Do you want to save your credentials? (yes/no): ').lower():
            pickle.dump(credentials, open("credentials.p", "wb"))
        print('Credentials saved!')

    plan_name = 'Generated Plan'
    new_name = input('Set term plan name: ')
    if new_name:
        plan_name = new_name

    s = requests.Session()

    url = 'https://auth.ucr.edu/cas/login'
    tree = html.fromstring(s.get(url).content)
    auth = tree.xpath('//input[@name="execution"]/@value')
    login_data = {
        'username': credentials[0],
        'password': credentials[1],
        'execution': auth,
        '_eventId': 'submit',
        'geolocation': None
    }
    if 'have successfully logged' not in s.post(url, login_data).text:
        sys.exit('Login failed!')
    print('Login successful!')

    r = s.post(
        f'https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/term/search?mode=plan&dataType=json'
        f'&term={term}&studyPath=&studyPathText=&startDatepicker=&endDatepicker=')

    s.post('https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/plan/plan')

    models = []
    for crn in courselist:
        addData = {
            'dataType': 'json',
            'term': term,
            'courseReferenceNumber': crn,
            'section': 'section'
        }
        try:
            models.append(s.post('https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/plan/addPlanItem',
                                 data=addData).json()['model'])
        except:
            pass
    models.append({"headerDescription": plan_name, "headerComment": None})

    submitData = {
        "create": models,
        "update": [],
        "destroy": []
    }
    response = s.post('https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/plan/submitPlan/batch',
                      data=json.dumps(submitData))

    r = s.post('https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/plan/getPlanEvents')
    confirm = r.json()
    if not confirm:
        sys.exit('Error creating term plan! Check the number of plans you have on RWeb!')
    print('Term plan created successfully!')
    for crn, title in set([(class_dict["crn"], class_dict["title"]) for class_dict in confirm]):
        print(f'{crn}\t{title}')

    if 'yes' in input('Set plan as preferred term plan? (yes/no): ').lower():
        s.post('https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/plan/selectPlan')
        s.post("https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/plan/makePreferred"
               f"?dataType=json&preferred={response.json()['data']['planHeader']['sequenceNumber']}")
