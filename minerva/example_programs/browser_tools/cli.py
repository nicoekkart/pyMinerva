from example_programs.browser_tools.app import App

class CLI():
    def __init__(self):
        self.commands = {
                "ls": self.parse_ls,
                "pwd": self.parse_pwd,
                "cd": self.parse_cd,
                "local": self.parse_local
                }
        self.app = App()
    def parse_ls(self, args):
        return self.app.ls()
    def parse_pwd(self, args):
        return self.app.pwd()
    def parse_cd(self, args):
        try:
            folder = int(args[0])
            return self.app.cd(folder)
        except ValueError:
            print("cd takes an integer")
        except IndexError:
            print("Please provide an argument to `cd`")
    def parse_local(self, args):
        return self.app.local()
    def parse_arg(self, arg):
        args = arg.split()
        cmd = args[0]
        if cmd in self.commands:
            return self.commands[cmd](args[1:])
        return error(args)
def error(args):
    return "Couldn't find command {0}".format(args[0])
