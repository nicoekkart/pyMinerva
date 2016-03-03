""" This program download all files off a minerva course in a given directory
    Usage:
        py -m example_programs.download_all <course_needle> (<folder>)

        with <course_needle> being the search string for your course, and (<folder>) being the path on your computer
        where you want the files to be downloaded.
"""
from minerva_core import Minerva
import sys
import os
import secrets


def download_course(needle_course):
    # Search string for the course

    with Minerva(secrets.username, secrets.password) as minerva:
        # Course object
        course = minerva.find_first_course(needle_course)
        minerva.go_to_course_page(course)
        minerva.open_tool('docu')
        minerva.get_all_documents()


def get_input():
    needle_course = ""
    while needle_course is "":
        needle_course = input(
            "type a keyword for the course you want to download: ")
        if needle_course == "":
            needle_course = None

        directory = input(
            "Select a directory where to download the course "
            "(Leave blank for current directory): ")
        if directory is not "":
            if not os.path.isdir(directory):
                os.makedirs(directory)
            # Change directory
            os.chdir(directory)
    return needle_course

if __name__ == '__main__':
    download_course(get_input())
