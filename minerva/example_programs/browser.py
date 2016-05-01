from example_programs.browser_tools.cli import CLI

cli = CLI()
while True:
    inp = input('> ')
    cli.parse_arg(inp)
