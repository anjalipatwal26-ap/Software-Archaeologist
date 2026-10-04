import math
from datetime import datetime


class Calculator:
    def add(self, a, b):
        return a + b

    def multiply(self, a, b):
        return a * b


def calculate_square(number):
    return math.pow(number, 2)


def get_current_time():
    return datetime.now()