"""Generate random password and return it.
Keyword argument:
min_len -- min length of password (default=6, int)
max_len -- min length of password (default=10, int)"""
from builtins import str
import string
import random


return str(DateTime().millis()) + '-' + ''.join(random.sample(string.letters+string.digits, random.randint(min_len,max_len)))
