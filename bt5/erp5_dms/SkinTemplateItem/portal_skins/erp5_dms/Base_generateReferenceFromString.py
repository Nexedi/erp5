"""
  Generate reference from a string by escaping all non ascii characters.
  XXX: add support for non-ascii characters using unidecode python library
"""
transliterate_list = ['?', ':', ';', '/', '&', '=', '^', '@', '>', '<', ']', '[', '^', '\\']

def removeNonAscii(s):
  return "".join(i for i in s if ord(i)>44 and ord(i)<123)

# reference can be used for permanent URL so be friendly to spaces (SEO)
s = s.strip()
s =s.replace(' ', '-')

s = removeNonAscii(s)
for item in transliterate_list:
  s = s.replace(item, '-')

return s.strip('-')
