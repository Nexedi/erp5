## Script (Python) "Base_doFavorite"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=favorite_select, form_id=''
##title=
##
import string

#Base_doAction = favorite_select.split() Previous implementation
if favorite_select.find('local_roles=') > 0:
  # Some local roles are defined
  url_items = favorite_select.split('&') # split parameters
  new_items = []
  for item in url_items:
    if item.find('local_roles=') >= 0:
      local_roles = item[item.find('local_roles='):].split(';')
      for role in local_roles:
        role = role.split('=')
        if len(role[len(role)-1]) > 0:
          new_items.append("local_roles:list=%s" % role[len(role)-1])
    else:
      new_items.append(item)
      
  favorite_select = '&'.join(new_items)

Base_doAction = (favorite_select,)
doAction0 = Base_doAction[0]
request = context.REQUEST

return request.RESPONSE.redirect(doAction0)
