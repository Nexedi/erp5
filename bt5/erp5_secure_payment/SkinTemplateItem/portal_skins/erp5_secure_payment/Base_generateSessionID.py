"""
  Generate random id which is generally used as a session ID.
"""
from random import choice
import string
return  ''.join([choice(string.ascii_letters) for _ in range(max_long)])
