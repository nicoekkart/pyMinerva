from requests import session
from bs4 import BeautifulSoup
import pickle
from collections import defaultdict
import os.path
import balloonTip
import secrets
import time


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

payload = {
    'action': 'login',
    'username': secrets.USERNAME,
    'password': secrets.PASSWORD
}


def crawl_url(url, c, d):
    response = c.get(url)
    html_course = response.text
    soup = BeautifulSoup(html_course, 'html.parser')
    content = soup.find(id="content")
    titel = content.find('h1').string
    all_announcements = content.find_all(class_='new_item')

    for item in all_announcements:
        a_item = item.find(class_='link2follow')
        if(a_item):
            item_text = a_item.string
            d[str(titel)].append(str(item_text))
    return d


with session() as c:
    URL = (
        'https://login.ugent.be/login'
        '?service=https%3A%2F%2Fminerva.ugent.be'
        '%2Fplugin%2Fcas%2Flogincas.php'
    )
    c.post(URL, data=payload)
    response = c.get('http://minerva.ugent.be/index.php')
    list_new_notifs = defaultdict(list)
    html_minerva = response.text
    soup = BeautifulSoup(html_minerva, 'html.parser')
    courses = soup.find_all(class_="course")
    for course in courses:
        course_link = course.find('a')
        course_url = course_link.get('href')
        list_new_notifs = crawl_url(course_url, c, list_new_notifs)


def get_difference(d1, d2):
    d3 = defaultdict(list)
    for key, val in d1.items():
        d3[key] = list(set(d1[key]) - set(d2[key]))
    return d3

FILENAME = "log_data.p"

if(os.path.isfile(FILENAME)):
    list_old_notifs = pickle.load(open("log_data.p", "rb"))
else:
    list_old_notifs = defaultdict(list)

newest_notifs = get_difference(list_new_notifs, list_old_notifs)

print("Alles ingelezen, dit zijn de verschillen:")
print("===================================\n\n")
full_string = ""
for key, val in newest_notifs.items():
    if(val):
        print(key)
        print("--------------------------")
        print("\n".join(val))
        print()
        balloonTip.balloon_tip("Minerva: " + key, "\n".join(val) + "\n")
        
print(full_string)


# We have the list of anouncements, now pickle them
pickle.dump(list_new_notifs, open("log_data.p", "wb"))
