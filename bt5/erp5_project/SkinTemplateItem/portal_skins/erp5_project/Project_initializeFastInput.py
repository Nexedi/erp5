from Products.ERP5Type.Document import newTempBase

portal_object = context.getPortalObject()

if lines_num is None:
  lines_num = portal_object.portal_preferences.getPreferredListboxListModeLineCount() or 40

new_id = 0
l = []


# function to create a new fast input line
def createInputLine(new_id):
  int_len = 3
  o = newTempBase( portal_object,
                   str(new_id),
                   uid ='new_%s' % str(new_id).zfill(int_len)
                 )
  l.append(o)

# generate all lines for the fast input form
for new_id in range(lines_num):
  createInputLine(new_id + 1)

# return the list of fast input lines
return l
