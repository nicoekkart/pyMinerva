from clint.textui import puts, indent
from minerva_core import Minerva
import secrets
class App():
    def __init__(self):
        self.minerva = Minerva(secrets.username, secrets.password)
        self.cd_stack = []
    def ls(self):
        def ls_courses():
            puts("Courses main page")
            with indent(4):
                puts("\n".join(["({}) {}".format(i, x.title) for i, x in enumerate(self.minerva.find_all_courses())]))
        def ls_tools():
            puts("Course page")
            with indent(4):
                puts("\n".join(["({}) {} {}".format(i, x.name, '*' if x.is_new else '')
                    for i, x in enumerate(self.minerva.get_all_tools())
                    ]))
        if len(self.cd_stack) == 0:
            ls_courses()
        elif len(self.cd_stack) == 1:
            ls_tools()
    def pwd(self):
        puts(self.minerva.current_url)
    def cd(self, folder):
        def cd_courses():
            self.minerva.go_to_course_page(
                    self.minerva.find_all_courses()[folder]
                    )
        def cd_tools():
            self.minerva.open_tool(
                    self.minerva.get_all_tools()[folder].name
                    )
        if len(self.cd_stack) == 0:
            cd_courses()
        elif len(self.cd_stack) == 1:
            cd_tools()
        self.cd_stack.append(folder)
    def local(self):
        self.minerva.open_local_version()
