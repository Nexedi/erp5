"""Generate random password and return it.
Keyword argument:
min_len -- min length of password (default=6, int)
max_len -- min length of password (default=10, int)"""
import string
import random


return str(DateTime().millis()) + '-' + ''.join(random.sample(string.ascii_letters+string.digits, random.randint(min_len,max_len)))
