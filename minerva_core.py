import requests
from bs4 import BeautifulSoup
import course
import re
import webbrowser
import os
import secrets
from urllib.parse import urljoin 


MINERVA_POST_URL = (
    'https://login.ugent.be/login'
    '?service=https%3A%2F%2Fminerva.ugent.be'
    '%2Fplugin%2Fcas%2Flogincas.php'
)

BASE_URL = 'http://minerva.ugent.be/index.php'


class Minerva():

    def __init__(self, username, password):
        payload = {
            'action': 'login',
            'username': username,
            'password': password
        }

        c = requests.session()
        c.post(MINERVA_POST_URL, payload)
        response = c.get(BASE_URL)

        self.req_session = c
        self.resp = response
        self.current_url = BASE_URL
        self.soup = (None, None)
        self.all_courses = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        self.req_session.close()

    def to_main(self):
        self.to_url(BASE_URL)

    def to_url(self, url):
        if(self.current_url == url):
            return
        self.resp = self.req_session.get(url)
        self.current_url = url

    def open_tool(self, tool_name):
        soup = self.getSoup()
        all_tools = map(
            lambda x: (x.a['href'], x.img['title']), soup.select("div.tool.pointer"))
        tools_regex = re.compile(tool_name, re.IGNORECASE)
        answer = next(
            filter(lambda x: tools_regex.search(x[1]), all_tools),
            None
        )
        self.to_url(answer[0])
        return answer

    def get_all_documents(self):
        soup = self.getSoup()
        all_divs = soup.select("div[id^=document]")
        for div in all_divs:
            span = div.span
            if(not span):
                 continue
            a = span.a
            if(not a):
                continue
            link = a['href']
            title = a.string
            if(link.startswith('http')):
                self.download_file(link)
            elif(link.startswith('document.php')):
                old_url = self.current_url
                new_url = urljoin(old_url, link)
                self.to_url(new_url)
                os.makedirs(title)
                os.chdir(title)
                self.get_all_documents()
                os.chdir("..")
                self.to_url(old_url)



    def get_html(self):
        return self.resp.text

    def getSoup(self):
        soup_url, soup = self.soup
        if(soup_url == self.current_url and soup):
            return soup
        soup = BeautifulSoup(self.get_html(), 'html.parser')
        self.soup = (self.current_url, soup)
        return soup

    def find_all_courses(self):
        if(self.all_courses):
            return self.all_courses
        assert self.current_url == BASE_URL, (
            "Courses can only be found at the homepage"
        )
        soup = self.getSoup()
        courses_bs = soup.find_all(class_="course")
        courses = map(course.course_from_div, courses_bs)
        self.all_courses = list(courses)
        return self.all_courses

    def go_to_course_page(self, course):
        self.to_url(course.url)

    def find_first_course(self, search_string):
        results = self.find_courses(search_string)
        return results[0] if results else None

    def find_courses(self, search_string):
        assert self.current_url == BASE_URL, (
            "Courses can only be found at the homepage"
        )
        all_courses = self.find_all_courses()
        is_correct = re.compile(search_string, re.IGNORECASE)
        results = filter(lambda x: is_correct.search(str(x)), all_courses)
        return list(results)

    def open_local_version(self):
        file = open("minerva_tmp.html", "w")
        file.write(self.get_html())
        file.close()
        webbrowser.open("minerva_tmp.html")

    def download_file(self, url):
        r = self.req_session.get(url, stream=True)
        with open(self.basename(url), 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    # f.flush() commented by recommendation from J.F.Sebastian

    def basename(self, url):
        url = os.path.basename(url)
        found = re.search(r"(.*)\?(.*)", url)
        return found.group(1)


if __name__ == '__main__':
    with Minerva(secrets.username, secrets.password) as minerva:
        analyse = minerva.find_first_course("analyse II")
        minerva.go_to_course_page(analyse)
        minerva.open_tool("document")
        minerva.get_all_documents()