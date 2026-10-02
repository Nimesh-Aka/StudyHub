from datetime import datetime
class Item:
     def __init__(self, item_id, title):
          self.__item_id=item_id
          self.__date=datetime.now()
          self.set_title(title)

     def get_item_id(self):
          return self.__item_id

     def get_title(self):
          return self.__title

     def get_date(self):
          return self.__date

     def set_title(self, title):
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")
        self.__title = title