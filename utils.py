import datetime
import random

def greet(name):
    return f"Hello, {name}!"

def current_time():
    now = datetime.datetime.now()
    return now.strftime("%H:%M:%S")

def random_choice(options):
    return random.choice(options)