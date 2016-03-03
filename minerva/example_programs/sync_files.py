from minerva_core import Minerva
from example_programs.synced_map import m
import os
import secrets
import re

with Minerva(secrets.username, secrets.password) as minerva:
    for needle, folder in m.items():
        os.chdir(folder)
        course = minerva.find_first_course(needle)
        minerva.go_to_course_page(course)
        all_tools = minerva.get_all_tools()
        docu_regex = re.compile('docu', re.IGNORECASE)
        document_tool = next(
            filter(lambda x: docu_regex.search(x.name), all_tools),
            None
        )
        if document_tool.is_new:
            minerva.open_tool('docu')
            minerva.get_all_documents()
            print('Course updated: ' + course.title)
        minerva.to_main()
