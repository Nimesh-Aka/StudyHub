from item import Item
from datetime import datetime

class Task(Item):
    def __init__(self, task_id, title, due_date, task_status):
        super().__init__(task_id, title)
        self.set_due_date(due_date)
        self.set_task_status(task_status)

    def get_due_date(self):
             return self.__due_date

    def get_task_status(self):
            return self.__task_status

    def set_due_date(self, due_date):
         if due_date == "":
            raise ValueError("Due Date cannot be empty")
         else:
            self.__due_date=due_date

    def set_task_status(self, task_status):
        task=task_status
        match task:
            case "To-Do":
                self.__task_status="To-Do"
            case "In Progress":
                self.__task_status="In Progress"
            case "On Hold":
                self.__task_status="On Hold"
            case _:
                raise ValueError("Task Status Cannot be empty or have to above status")

    def summary(self):
        return f"Task: {self.get_title()} [{self.get_task_status()}] due {self.get_due_date()}"
            


         
