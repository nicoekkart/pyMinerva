""" Holds the core class of the pyMinerva project
"""

import requests
from bs4 import BeautifulSoup
import course
import re
import webbrowser
import os
import secrets
from urllib.parse import urljoin

# URL to send POST request to
MINERVA_POST_URL = (
    'https://login.ugent.be/login'
    '?service=https%3A%2F%2Fminerva.ugent.be'
    '%2Fplugin%2Fcas%2Flogincas.php'
)

# Minerva home page
BASE_URL = 'http://minerva.ugent.be/index.php'


class Minerva():

    """ This class represants a minerva session.
        Possible things to do:
            - use as context manager
            - Go to (secured) minerva url
            - List all the courses
            - Find a specific course
            - Go to course page
            - Use course tools:
                - Documents:
                    - Download all documents with same directory names
                    - Download single document
            - TODO
    """

    def __init__(self, username, password):
        """ Initializes the minerva request session
            username is the minerva username
            password is the minerva password
        """
        # POST request parameters
        payload = {
            'action': 'login',
            'username': username,
            'password': password
        }
        # Create session and POST
        c = requests.session()
        c.post(MINERVA_POST_URL, payload)

        # Set default page to BASE_URL
        response = c.get(BASE_URL)

        # Save request session
        self.req_session = c
        # Save the response
        self.resp = response
        # Save the current url where we're at
        self.current_url = BASE_URL

        # Initialize empty members
        self.soup = (None, None)
        self.all_courses = None

    def __enter__(self):
        """ Gets ran when used as context manager
        """
        return self

    def __exit__(self, *args):
        """ Gets ran when exiting context manager
        """
        self.close()

    def close(self):
        """ Close the current session
        """
        self.req_session.close()

    def to_main(self):
        """ Go to the minerva homepage
        """
        self.to_url(BASE_URL)

    def to_url(self, url):
        """ Changes the current page to the given url
            TODO: is valid?
        """
        if(self.current_url == url):
            # Already there
            return

        # Update session response
        self.resp = self.req_session.get(url)
        # Update current url
        self.current_url = url

    def get_all_tools(self):
        """ Returns a list of tools (name, url, is_new) of the current course
        """
        # Get the Beautiful Soup
        soup = self.getSoup()
        # Get all the tool divs
        tool_divs = soup.select('div.tool.pointer')
        # Get the info required from the div
        tool_info = map(
            lambda x: (x.img['title'], x.a['href'], 'new_item' in x['class']),
            tool_divs)
        return list(tool_info)

    def open_tool(self, tool_name):
        """ Opens a tool on a course page.
            Returns a tuple (url, name)
            TODO: make safer
        """
        # Get the Beautiful Soup
        soup = self.getSoup()

        # Get all the tools on the course page
        all_tools = self.get_all_tools() 

        # Create regex to find the tool
        tools_regex = re.compile(tool_name, re.IGNORECASE)

        # Find first satisfying tool, otherwise returns None
        answer = next(
            filter(lambda x: tools_regex.search(x[0]), all_tools),
            None
        )
        # Go to the tool url
        self.to_url(answer[1])
        return answer

    def get_all_documents(self):
        """ Specific for 'documents' tool.
            Downloads all documents recursively, keeps minerva folder structure.
            TODO: make safer, on documents page?, possible errors, make more pythonesque
        """
        # Get the Beautiful Soup
        soup = self.getSoup()
        # Select all divs whose id's start with 'document'
        all_divs = soup.select("div[id^=document]")

        for div in all_divs:
            # Check if the div contains a span
            span = div.span
            if(not span):
                continue
            # Check if the span contains an anchor
            a = span.a
            if(not a):
                continue
            # Get url and title from the anchor
            link = a['href']
            title = a.string
            # If this is a document (might FAIL)
            if(link.startswith('http')):
                # Download this file in the current folder
                self.download_file(link)
            # If this is a folder (might FAIL)
            elif(link.startswith('document.php')):
                # Save old url as tmp var
                old_url = self.current_url
                # Create a new url, where the folder is on minerva
                new_url = urljoin(old_url, link)
                # Go to url
                self.to_url(new_url)
                # Create a folder with same name as on minerva
                os.makedirs(title)
                # Change current directory to this folder
                os.chdir(title)
                # Get all documents (recursive) of this folder
                self.get_all_documents()
                # Go back to original folder
                os.chdir("..")
                # Go back to original url
                self.to_url(old_url)

    def get_html(self):
        """ Returns html representation (txt) of the current page
        """
        return self.resp.text

    def getSoup(self):
        """ Returns the Beautiful Soup of the current page
        """
        # Does it already exist for this page?
        soup_url, soup = self.soup
        if(soup_url == self.current_url and soup):
            return soup
        # Create new soup and return
        soup = BeautifulSoup(self.get_html(), 'html.parser')
        self.soup = (self.current_url, soup)
        return soup

    def find_all_courses(self):
        """ Returns a list of all the courses (Course) on your minerva
        """
        # Don't redo your work
        if(self.all_courses):
            return self.all_courses
        # Just to be sure
        assert self.current_url == BASE_URL, (
            "Courses can only be found at the homepage"
        )
        # Get the Beautiful Soup
        soup = self.getSoup()

        # Find all the elements with the .course class
        courses_bs = soup.find_all(class_="course")
        # Create Course objects for all of them
        courses = map(course.course_from_div, courses_bs)
        # map -> list
        self.all_courses = list(courses)
        return self.all_courses

    def go_to_course_page(self, course):
        """ Goes to the url of a course
        """
        self.to_url(course.url)

    def find_first_course(self, search_string):
        """ Returns the first course that contains search_string
            TODO: better with iterator
        """
        # Find all the courses satisfying this
        results = self.find_courses(search_string)
        # Take the first one
        return results[0] if results else None

    def find_courses(self, search_string):
        """ Find all courses that contain search_string
        """
        assert self.current_url == BASE_URL, (
            "Courses can only be found at the homepage"
        )
        # Find all the courses
        all_courses = self.find_all_courses()
        # Regex to check if course contains
        is_correct = re.compile(search_string, re.IGNORECASE)
        # Filter on the course __str__, which holds all info
        results = filter(lambda x: is_correct.search(str(x)), all_courses)
        return list(results)

    def open_local_version(self):
        """ Opens a local (html) version of the current page
        """
        # Open a writer
        file = open("minerva_tmp.html", "w")
        # Write the html to the file
        file.write(self.get_html())
        file.close()
        # Open the file in the browser
        webbrowser.open("minerva_tmp.html")

    def download_file(self, url):
        """ Downloads a file (minerva or not) on the current url
            TODO: make safer
        """
        # get the response of GET url
        r = self.req_session.get(url, stream=True)
        # write this response in chuncks of 1024 bytes
        with open(self.basename(url), 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)

    def basename(self, url):
        """ Returns the basename (only filename without query parameters)
            TODO: can the regex fail?
        """
        # Get the basename (file name)
        url = os.path.basename(url)
        # Strip query parameters
        found = re.search(r"(.*)\?(.*)", url)
        return found.group(1)


if __name__ == '__main__':
    """ Example program for the Minerva class
    """
    with Minerva(secrets.username, secrets.password) as minerva:
        analyse = minerva.find_first_course("wiskundige basis")
        minerva.go_to_course_page(analyse)
        minerva.open_tool("forum")
        minerva.open_local_version()
