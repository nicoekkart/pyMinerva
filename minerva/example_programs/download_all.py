""" This program download all files off a minerva course in a given directory
    Usage:
        py -m example_programs.download_all <course_needle> (<folder>)
"""
from minerva_core import Minerva
import sys
import os
import secrets

# Search string for the course
needle_course = sys.argv[1]

if len(sys.argv) == 3:
    if not os.path.isdir(sys.argv[2]):
        os.makedirs(sys.argv[2])
    # Change directory
    os.chdir(sys.argv[2])

with Minerva(secrets.username, secrets.password) as minerva:
    # Course object
    course = minerva.find_first_course(needle_course)
    minerva.go_to_course_page(course)
    minerva.open_tool('docu')
    minerva.get_all_documents()
