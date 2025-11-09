
from collections import UserDict
from datetime import datetime, timedelta
import re

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty.")
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if not re.fullmatch(r"\d{10}", value):
            raise ValueError("Phone number must be exactly 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.date = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)

    def __str__(self):
        return self.value

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        self.phones.append(phone)

    def delete_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                self.phones.remove(phone)
                return True
        return False

    def edit_phone(self, old_number, new_number):
        for phone in self.phones:
            if phone.value == old_number:
                new_phone = Phone(new_number)
                idx = self.phones.index(phone)
                self.phones[idx] = new_phone
                return True
        return False

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def add_birthday(self, date_str):
        self.birthday = Birthday(date_str)

    def show_birthday(self):
        return str(self.birthday) if self.birthday else "Birthday not set."

    def days_until_birthday(self):
        if self.birthday:
            today = datetime.today()
            bd = self.birthday.date
            next_bd = bd.replace(year=today.year)
            if next_bd < today:
                next_bd = next_bd.replace(year=today.year + 1)
            return (next_bd - today).days
        return None

    def __str__(self):
        phones_str = '; '.join(str(p) for p in self.phones)
        bd_str = f", Birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{bd_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return True
        return False

    def get_upcoming_birthdays(self):
        today = datetime.today()
        upcoming = []
        for record in self.data.values():
            days_left = record.days_until_birthday()
            if days_left is not None and 0 <= days_left <= 7:
                upcoming.append((record.name.value, record.birthday))
        return upcoming
    
    #  Реалізація команд функції з декоратором 
    import re

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found."
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Insufficient arguments."
        except Exception as e:
            return f"Error: {str(e)}"
    return inner

@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if not record:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_phone(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        raise KeyError
    if not record.edit_phone(old_phone, new_phone):
        return "Old phone number not found."
    return "Phone updated."

@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        if record.phones:
            return f"{name}'s phones: " + ", ".join(str(phone) for phone in record.phones)
        else:
            return f"{name} has no phone numbers."
    else:
        raise KeyError