import re
from collections import UserDict
from datetime import datetime, timedelta
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, name):
        super().__init__(name)
        if not name:
            raise ValueError('Name is a required')     

class Phone(Field):
    def __init__(self, phone):
        super().__init__(phone)
        if not re.fullmatch(r"\d{10}", phone):
            raise ValueError('Number must have 10 digits')
        
class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        
    def __str__(self):
        return self.value.strftime("%d.%m.%Y")     

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, new_phone):
        self.phones.append(Phone(new_phone))

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                break

    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                break

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p.value
        return None
    
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        del self.data[name]

    def get_upcoming_birthdays(users):
        greetings_users = []
        today = datetime.today().date()
        for user in users:
            birthday = datetime.strptime(user["birthday"], "%Y.%m.%d").date()
            birthday_this_year = birthday.replace(year = today.year)

            if (birthday_this_year < today):
                birthday_this_year = birthday_this_year.replace(year = today.year + 1)

            days_before_birthday = (birthday_this_year - today).days

            if days_before_birthday <= 6:
                congratulation_date = birthday_this_year

                if congratulation_date.weekday() > 4:
                    congratulation_date += timedelta(days=(7 - congratulation_date.weekday()))
             
                greetings_users.append({
                    "name": user["name"],
                    "congratulation_date": congratulation_date.strftime('%Y.%m.%d'),
                })    
        return greetings_users
    

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()    

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, IndexError) as e:
            return str(e)
    return inner


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book):
    name, phone, *_ = args
    if phone:
        try:
            Phone(phone)
        except ValueError as e:
            return str(e)
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        return f"No contact found."
    record.edit_phone(old_phone, new_phone)
    return "Phone number updated."
    
@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if not record:
        return f"No contact found."
    return f"Phones for {name}: {', '.join(phone.value for phone in record.phones)}"

@input_error
def show_phones(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if not record:
        return f"No contact found."
    return f"Phones for {name}: {', '.join(phone.value for phone in record.phones)}"

def show_all(args, book: AddressBook):
    return "\n".join(str(record) for record in book.values())

@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if not record:
        return f"No contact found."
    record.add_birthday(birthday)
    return "Birthday added." 

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if not record:
        return f"Not found."
    if not record.birthday:
        return f"Any records found"
    return f"Birthday in record {record.birthday}."

@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No upcoming birthdays."
    return "\n".join(f"{user['name']} has a birthday on {user['congratulation_date']}" for user in upcoming_birthdays)


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == 'hello':
            print("How can I help you?")
        elif command == 'add':
            print(add_contact(args, book))
        elif command == 'change':
            print(change_contact(args, book))
        elif command == 'phone':
            print(show_phone(args, book))      
        elif command == 'all':
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print('Invalid command.')

if __name__ == "__main__":
    main()
