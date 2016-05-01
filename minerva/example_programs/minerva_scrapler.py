""" This program checks minerva for new activity
    and returns them as windows notifications.
"""

import os
import pickle
import sys
import platform

from minerva_core import Minerva

import secrets


def get_items_diff(old, new):
    """ Finds difference between old and new pickle
    """
    changed = {}
    # Loop trough the new one
    for course, new_items in new.items():
        # These are the old items for the current course
        old_items = old[course] if course in old else []
        # Get the difference
        cur_changed = [i for i in new_items if not i in old_items]
        if cur_changed:
            # Set the difference
            changed[course] = cur_changed
    return changed


def is_windows():
    return os.name == 'nt'


def windows_print(key, val):
    from example_programs import balloonTip

    balloonTip.balloon_tip(
        "Minerva: " + key.title, "\n".join(val) + "\n"
    )

with Minerva(secrets.username, secrets.password) as minerva:
    # Get all the courses
    courses = minerva.find_all_courses()
    # Remove infopages
    courses = list(
        filter(lambda x: not x.is_info, courses)
    )
    # Empty dictionary for course -> new items
    course_new_items = {}

    for course in courses:
        # Go to the course page of the current course
        minerva.go_to_course_page(course)
        # Get all the tools (Tool) of the current course
        all_tools = minerva.get_all_tools()
        # Filter on new items
        new_items = list(
            filter(lambda x: x.is_new, all_tools)
        )
        # Store the new items in the map
        course_new_items[course] = list(
            map(
                lambda x: x.name,  # Only need name of tool
                new_items
            )
        )

    # Choose arbitrary filename
    FILENAME = "log_data.p"

    if(os.path.isfile(FILENAME)):
        # File exists => We can depickle
        course_old_items = pickle.load(open(FILENAME, "rb"))
    else:
        # File doesn't exist => empty map
        course_old_items = {}

    # Get the changed items
    course_changed = get_items_diff(course_old_items, course_new_items)

    for key, val in course_changed.items():
        # Windows notification with changes

        # TODO: Check if it works in windows?
        if is_windows():
            windows_print(key, val)

        print("Minerva: " + key.title + "\n", "\n".join(val) + "\n")
    # necessary for pickle
    sys.setrecursionlimit(10000)
    # pickle the new items again
    pickle.dump(course_new_items, open(FILENAME, "wb"))
