value_list = context.getPortalObject().portal_selections \
               .getSelectionCheckedValueList(context.REQUEST.selection_name)
if not value_list:
  raise ValueError('No Test Result selected')

if len(value_list) != 2:
  raise ValueError('Two Test Results should be selected')

a, b = value_list

from Products.ERP5Type.Document import newTempBase
import six

# make sure that a is the oldest result
if a.getIntIndex() > b.getIntIndex():
  a, b = b, a

# map titles to ids
b_title_dict = dict((line.getObject().getTitle(), line.id) for line \
  in b.searchFolder(portal_type='Test Result Line'))

object_list = []

compared_prop_list = ('all_tests', 'errors', 'failures', 'skips')


for a_line in a.searchFolder(portal_type='Test Result Line'):
  a_line = a_line.getObject()
  title = a_line.getTitle()
  if title in b_title_dict:
    # do some diffwork
    b_line = b[b_title_dict[title]]
    difference_dict = {}
    for prop in compared_prop_list:
      diff = b_line.getProperty(prop) - a_line.getProperty(prop)
      if diff != 0:
        difference_dict[prop] = diff
    if difference_dict:
      line = newTempBase(context, title,
                         status="changed",
                         before_url=a_line.absolute_url(),
                         after_url=b_line.absolute_url(),
                         **difference_dict)
      object_list.append(line)

    del b_title_dict[title]
  else:
    d = dict((prop, -a_line.getProperty(prop)) for prop in compared_prop_list)
    object_list.append(newTempBase(context, title,
                                   status="deleted",
                                   before_url=a_line.absolute_url(),
                                   **d))

for title, not_in_a in six.iteritems(b_title_dict):
  b_line = b[not_in_a]
  d = dict((prop, b_line.getProperty(prop)) for prop in compared_prop_list)
  object_list.append(newTempBase(context, title,
                                 status="added",
                                 after_url=b_line.absolute_url(),
                                 **d))

object_list.sort(key=lambda x:(x.status, x.id))
return object_list
