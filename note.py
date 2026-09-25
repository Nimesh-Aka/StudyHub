
from datetime import datetime

class Note:
    def __init__(self, note_id, title, description):
        self.__note_id=note_id
        self.__date=datetime.now()
        self.set_title(title)
        self.set_description(description)

    def get_note_id(self):
        return self.__note_id

    def get_date(self):
        return self.__date

    def get_title(self):
        return self.__title

    def set_title(self, title):
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")
        self.__title = title

    def get_description(self):
        return self.__description

    def set_description(self, description):
        if not description or not description.strip():
            raise ValueError("Description cannot be empty")
        self.__description = description