"""
  Generic random string generator.

"""
from random import choice
from string import ascii_letters, digits

character_set = ''
if include_letters:
  character_set = '%s%s' %(character_set, ascii_letters)
if include_digits:
  character_set = '%s%s' %(character_set, digits)
return ''.join([choice(character_set) for _ in range(int(string_length))])
