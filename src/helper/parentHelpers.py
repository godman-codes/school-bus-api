from random import randint

def create_username(last_name):
   """ creates a username from name and random integer"""
   return last_name + str(randint(0, 99))


def phoneNumberConverter(phone):
   """
   converts a normal phone number to +234
   """
   return f'+234{phone[1:]}'

def standard_query_helper(array, full_word):
   "a function to serach for a word in the joining of two class name properties"
   new_elements = []
   for element in array:
      if f'{element.first_name} {element.last_name}'.startswith(full_word):
         new_elements.append(element)
      if f'{element.last_name} {element.first_name}'.startswith(full_word):
         new_elements.append(element)
   print(new_elements)
   return new_elements
         
         
      

def standard_query(word, class__):
   "queries the database for columns of a class that start with word"
   class_title = class__.query.all()
   print(class_title)
   all_valid_elements = standard_query_helper(class_title, word)
   return all_valid_elements
   
   # first_name_row =  class__.query.filter(class__.first_name.startswith({word})).all()
   
   # last_name_row = class__.query.filter(class__.last_name.startswith({word})).all()
   
   # if first_name_row is None:
   #    last_name_row
   # elif last_name_row is None:
   #    return first_name_row
   # else:
   #    return first_name_row.extends(first_name_row)
      