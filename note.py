from item import Item
from datetime import datetime

class Note(Item):
    def __init__(self, note_id, title, description):
        super().__init__(note_id, title)
        self.set_description(description)


    def get_description(self):
        return self.__description

    def set_description(self, description):
        if not description or not description.strip():
            raise ValueError("Description cannot be empty")
        self.__description = description

    def summary(self):
        return f"Note: {self.get_title()} - {self.get_description()}"


