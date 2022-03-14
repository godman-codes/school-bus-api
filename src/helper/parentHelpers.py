from random import randint

def create_parent_username(last_name):
   """ creates a username for registered parent"""
   return last_name + str(randint(0, 99))