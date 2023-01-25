"""
  This script returns the list of category (or tags) which are available in the current web section.
  It returns a python list of Category object. A Category object is really simple, as it has just
  one property with a getter and a setter : title.

  TODO: XXX-JPS
  - this is way too slow - it will collapse the system
  - have a look at mailreader code - there is something doing the same
  - consider using virtual domains possibly - again look in email reader code
"""


## First step : retrieve the raw list
current_section = context.getWebSectionValue()
subject_list = []

for item in current_section.WebSection_getDocumentValueList(): # XXX-JPS - this will fail for performance reasons
  subject_list.extend([x for x in item.getSubjectList() if not x in subject_list])

## Now, build the object list so that a Listbox can be used to display the results of this script.
result = []

class Category:
  def setTitle(self, title):
    self.title = title
  def getTitle(self):
    return self.title

for item in subject_list:
  obj = Category()
  obj.setTitle(item)
  result.append(obj)

return result
