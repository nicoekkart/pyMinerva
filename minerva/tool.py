""" Class for a Tool
"""


class Tool():

    def __init__(self, name, url, is_new):
        self.name = name
        self.url = url
        self.is_new = is_new

    def __str__(self):
        return "%s: %s (%s)" % (
            self.name,
            self.url,
            'New item' if self.is_new else 'Old item'
        )

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.__str__() == other.__str__()