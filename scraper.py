import requests
import time
import sys


class rweb_session:
    def __init__(self):
        terms_url = 'https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/classSearch/getTerms?dataType=json&searchTerm=&offset=1&max=5'
        self.term_codes = requests.get(terms_url).json()
        self.rev_dict = {d['description']: d['code'] for d in self.term_codes}
        print(self.rev_dict)

    def init_term(self, _term):
        self.term_code = self.rev_dict[_term]
        class_url = f'https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/courseSearch/get_subjectcoursecombo?dataType=json&searchTerm=&term={self.term_code}&offset=1&max=9999'
        self.course_codes = [c['code'] for c in requests.get(class_url).json()]

    def is_valid_course(self, course):
        return course.upper() in self.course_codes

    def get_course_data(self, course):
        s = requests.Session()
        s.get(
            f'https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/term/search?mode=search&dataType=json&term={self.term_code}&studyPath=&studyPathText=&startDatepicker=&endDatepicker=')
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
