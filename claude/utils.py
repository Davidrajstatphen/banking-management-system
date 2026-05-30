import re
import json
import logging
import functools
import random
from datetime import datetime
import os 


# load config json file

with open("config.json","r") as f:
    CONFIRG=json.load(f)

logging.basicConfig(
     filename="transaction.log",
     level=logging.INFO,
     format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_transaction(func):
  """decorator to log transactions"""
  @functools.wraps(func)
  def wrapper(*args, **kwargs):
     logging.info(f"Called;{func.__name__} with args: {args[1:]}")
     try:
        result=func(*args, **kwargs)
        logging.info(f"Success : {func.__name__}")
        return result
     except Exception as e:
        logging.error(f"Error in {func.__name__}:{str(e)}")
        raise
     return wrapper
  
def validate_input(func):
   """decorator to validate inputs"""
   @functools.wraps(func)
   def wrapper(*args,**kwargs):
      for arg in args[1:]:
         if arg is None or arg == "":
            raise ValueError("input cannot be empty")
         return func(*args,**kwargs)
      return wrapper
                  
# regex for validation

def validate_pan(pan):
   pattern=r'^[A-Z]{5}[0-9]{4}[A-Z]$'
   return bool(re.match(pattern,pan.upper()))

def validate_phone(phone):
   pattern =r'^[6-9]\d{9}$'
   return bool(re.match(pattern,str(phone)))

def validate_email(email):
   pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
   return bool(re.match(pattern,email))

def validate_account_number(acc_num):
    pattern = r'^\d{10}$'
    return bool(re.match(pattern,str(acc_num)))


# generator for transaction history

def transaction_generator(transaction,batch_size=10):
   for i  in range(0,len(transaction),batch_size):
      yield transaction[i:i+batch_size]
   
def generate_account_number():
  #generate 10 unique number
  import random
  return str(random.randint(1000000000,999999999))


def generate_otp():
   import random
   return str(random.randint(100000,999999))

def format_currency(amount):
   return f"Rs {amount:,.2f}"

def get_timestamp():
   return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#File I/O

def write_to_log(message):
   """write message to log file"""
   timestamp=get_timestamp()
   log_entry=f"[{timestamp}] {message}\n"
   with open('transaction.log','a') as f:
      f.write(log_entry)


def read_log_file():
   
   if not os.path.exists('transactions.log'):
      return[]
   
   with open('transaction.log','r') as f:
      return f.readlines()
   

              

             

   
                 

