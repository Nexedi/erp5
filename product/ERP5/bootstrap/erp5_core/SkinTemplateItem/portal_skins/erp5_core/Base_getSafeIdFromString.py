"""
  This function transform a string to a safe id.
  It is used here to create a safe category id from a string.
"""
if s is None:
  return None
clean_id = ''
translation_map = { 'a'  : [u'\xe0', u'\xe3']
                  , 'e'  : [u'\xe9', u'\xe8']
                  , 'i'  : [u'\xed']
                  , 'u'  : [u'\xf9']
                  , '_'  : [' ', '+']
                  , '-'  : ['-', u'\u2013']
                  , 'and': ['&']
                  }
# Replace odd chars by safe ascii
s = s.lower()
s = s.strip()
for (safe_char, char_list) in translation_map.items():
  for char in char_list:
    s = s.replace(char, safe_char)
# Exclude all non alphanumeric chars
for char in s:
  if char.isalnum() or char in translation_map.keys():
    clean_id += char
# Delete leading and trailing char which are not alpha-numerics
# This prevent having IDs with starting underscores
while len(clean_id) > 0 and not clean_id[0].isalnum():
  clean_id = clean_id[1:]
while len(clean_id) > 0 and not clean_id[-1].isalnum():
  clean_id = clean_id[:-1]

return clean_id
