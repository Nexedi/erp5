"""
  This function transform a string to a safe id.
  It is used here to create a safe category id from a string.
"""

translation_map = { "a": ['\xe0']
                  , "e": ['\xe9', '\xe8']
                  }

clean_id = ''
if s is None:
  return None
s = s.lower()
s = s.strip()
# oocalc inserts some strange chars when you press - key in a text cell.
# Following line is a workaround for this, because \u2013 does not exist in latin1
s = s.replace(u'\u2013', '-')
for char in s.encode('iso8859_1'):
  if char == '_' or char.isalnum():
    clean_id += char
  elif char.isspace() or char in ('+', '-'):
    clean_id += '_'
  else:
    for (safe_char, char_list) in translation_map.items():
      if char in char_list:
        clean_id += safe_char
        break
return clean_id
