import string

def fixMissingCategoryTitles(self, dry_run=0):
  """
    Recursively sets a default title when it's empty or equal to id
    Must be called on CategoryTool
  """
  msg = ''
  for base in self.portal_categories.getChildNodes():
    object_list = base.getCategoryChildValueList()
    for object in object_list :
      title = object.getTitle()
      id = object.getId()
      if not title:
        new_title = string.capwords(id.replace('_', ' '))
        if not dry_run:
          object.setTitle(new_title)
        msg += 'The title of %s was set to %s\n' % (object.getRelativeUrl(), new_title)
  return msg
