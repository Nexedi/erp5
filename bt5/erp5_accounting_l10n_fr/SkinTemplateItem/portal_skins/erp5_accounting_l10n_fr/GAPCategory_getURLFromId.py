"""
  Translates a short account number (eg 280) to a full gap category url (eg gap/2/28/280).
"""

from builtins import range
number = gap_id.strip()

gap_url = gap_base
for i in range(len(number)):
  gap_url += number[:i+1] + '/'

return gap_url[:-1]
