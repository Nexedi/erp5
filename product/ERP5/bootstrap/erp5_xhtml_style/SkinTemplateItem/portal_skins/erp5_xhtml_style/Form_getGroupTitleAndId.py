"""
  This script splits a form group id in two part:
    * a group id,
    * a group title.

  The group should be named based on the following pattern: "group id (Group Title)"

  This script is a hack to let us merge two informations (id and title) into one (id) to get
    over Formulator limitations. This script should disappear with Formulator's refactoring.

  Features:
    * Multiple parenthesis allowed;
    * Group id can continue after the title definition.

  Example:
    A string like
      "left webcontent (The Fantastic Group (and (funky) lisp-like parenthesis)) extra",
    will return the following tuple:
      ( 'left webcontent extra'
      , 'The Fantastic Group (and (funky) lisp-like parenthesis)'
      , 'left webcontent (The Fantastic Group (and (funky) lisp-like parenthesis)) extra'
      )
"""
form=context

def getFormGroupTitleAndId():
  res = []
  append = res.append
  for original_group_id in form.get_groups(include_empty=0):
    group_id = original_group_id
    try:
      group_id_head, group_id_rest = group_id.split('(', 1)
      group_title, group_id_tail = group_id_rest.rsplit(')', 1)
      group_id = group_id_head + group_id_tail
      if not group_title:
        group_title = None
    except ValueError:
      # When group_id does not have parentheses.
      group_title = None
    group_id = ' '.join((w for w in group_id.split(' ') if w))
    append({'gid': group_id, 'gtitle': group_title, 'goid': original_group_id})
  return res

return getFormGroupTitleAndId()
