import re

class User:
    def __init__(self, name, email, password, notes):
        self.__name=name ## private property
        self.set_email(email)
        self.__password=password ## private property
        self.__notes=notes ## Instance property 

    def get_name(self):
        return self.__name
        
    def get_email(self):
        return self.__email

    def get_notes(self):
        return self.__notes
    
    def set_name(self, name):
        self.__name=name
        print("Name is changed!")

    ## For changing the email
    def set_email(self, email):
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, email):
            raise ValueError("Invalid Email Adress!")
        else:
            self.__email=email
            print("Email Set")
            

    ## For changeing the passwrod
    def set_password(self, password):
        self.__password=password
        print("Passwrod was changed!")


