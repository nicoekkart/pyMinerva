""" Holds the Course class, which represents a minerva course
"""
from datetime import date
import re


class Course():
    """ The course class
    """
    def __init__(self,
                 title='',
                 code='',
                 startingYear=date.today().year,
                 endingYear=date.today().year + 1,
                 professor='',
                 is_info=False,
                 url=None):
        """ Initializes the course with self-describing parameters
        """
        self.title = title
        self.code = code
        self.startingYear = startingYear
        self.endingYear = endingYear
        self.professor = professor
        self.is_info = is_info
        self.url = url

    def __str__(self):
        """ Create string representation of the course
        """
        ans = ''
        # If it is an info page
        if self.is_info:
            ans += 'Infosite: '
            ans += self.title
            ans += '==>' + self.url
        # If regular course
        else:
            ans += 'E' + str(self.code) + ' - '
            ans += self.title + ' '
            ans += "(%d, %d) - " % (self.startingYear, self.endingYear)
            ans += self.professor
            ans += ' ==> ' + self.url
        return ans

    def __repr__(self):
        """ Returns representation fo the course
            Necessary for some debugging
        """
        return self.__str__()

    def __hash__(self):
        return hash(self.__str__())

    def __eq__(self, other):
        return self.__str__() == other.__str__()


def course_from_div(div):
    """ Creates a course from a div containing all the course info
    """
    # Get the first anchor
    a = div.a
    title = a.string
    # Regex for the course code and starting year 
    # (which can be found in the div ID)
    courseRegex = re.compile(r'course_E(\d{6})0(\d{4})')
    m = courseRegex.search(str(div['id']))
    ms = None
    if m and len(m.groups()) == 2:
        # If we have caught both groups
        ms = m.groups()
    else:
        # Default values if not found (infopages)
        ms = ('', 0)
    # First part is the code, second the startingYear
    code = ms[0]
    startingYear = int(ms[1])
    # Assume this, until proven otherwise
    endingYear = startingYear + 1

    # Find all the strings in the div tag seperated by superTag
    all_strings = list(div.stripped_strings)

    # set is_info accordingly
    is_info = False
    if('Infosite' in all_strings):
        is_info = True
    professor = ''

    if(not is_info):
        # Captures the course code, startingYear, endingYear and Professor
        # These are all found in the subtitle on the minerva homepage
        # This is represented by all_strings[1]
        descRegex = re.compile(r'EX?(\d+).?\s\((\d+)\s-\s(\d+)\)\s-\s(.+)')
        found = descRegex.search(all_strings[1])
        if(found):
            professor = found.group(4)

    # Set the course url
    url = a['href']

    # Create the Course
    crs = Course(title, code, startingYear,
                 endingYear, professor, is_info, url)

    return crs
