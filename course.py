from datetime import date
import re


class Course():

    def __init__(self,
                 title='',
                 code='',
                 startingYear=date.today().year,
                 endingYear=date.today().year + 1,
                 professor='',
                 is_info=False,
                 url=None):
        self.title = title
        self.code = code
        self.startingYear = startingYear
        self.endingYear = endingYear
        self.professor = professor
        self.is_info = is_info
        self.url = url

    def __str__(self):
        ans = ''
        if self.is_info:
            ans += 'Infosite: '
            ans += self.title
            ans += '==>' + self.url
        else:
            ans += 'E' + str(self.code) + ' - '
            ans += self.title + ' '
            ans += "(%d, %d) - " % (self.startingYear, self.endingYear)
            ans += self.professor
            ans += ' ==> ' + self.url
        return ans

    def __repr__(self):
        return self.__str__()


def course_from_div(div):
    a = div.a
    title = a.string
    courseRegex = re.compile(r'course_E(\d{6})0(\d{4})')
    m = courseRegex.search(str(div['id']))
    ms = None
    if m and len(m.groups()) == 2:
        ms = m.groups()
    else:
        ms = ('', 0)
    code = ms[0]
    startingYear = int(ms[1])
    endingYear = startingYear + 1

    all_strings = list(div.stripped_strings)

    is_info = False
    if('Infosite' in all_strings):
        is_info = True
    professor = ''

    if(not is_info):
        descRegex = re.compile(r'EX?(\d+).?\s\((\d+)\s-\s(\d+)\)\s-\s(.+)')
        found = descRegex.search(all_strings[1])
        if(found):
            professor = found.group(4)

    url = a['href']

    crs = Course(title, code, startingYear,
                 endingYear, professor, is_info, url)

    return crs
