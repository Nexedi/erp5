from builtins import str
from builtins import range
from Products.ERP5Type.Document import newTempBase

portal_object = context.getPortalObject()

if lines_num is None:
  lines_num = portal_object.portal_preferences.getPreferredListboxListModeLineCount() or 40

new_id = 0
l = []


# function to create a new fast input line
def createInputLine(new_id):
  int_len = 3
  new_id_str = str(new_id)
  o = newTempBase( portal_object,
                   new_id_str,
                   uid ='new_' + new_id_str.zfill(int_len)
                 )
  l.append(o)

# generate all lines for the fast input form
for new_id in range(lines_num):
  createInputLine(new_id + 1)

# return the list of fast input lines
return l
