"Modified version for ERP5 to append the default action (/view) in the URL."

from Products.CMFCore.utils import getToolByName
ptool = getToolByName(script, 'portal_properties')
utool = getToolByName(script, 'portal_url')
portal_url = utool()
result = []
param = int(context.REQUEST.get('ignore_layout', 0)) and '?ignore_layout:int=1' or ''
if include_root:
  result.append( { 'id'      : 'root'
                   , 'title'   : ptool.title()
                   , 'url'     : '%s/view%s' % (portal_url, param)
                   }
                 )

relative = utool.getRelativeContentPath(context)
portal = utool.getPortalObject()

obj = portal
now = []
for name in relative:
  obj = obj.restrictedTraverse(name)
  now.append(name)
  title = (
      getattr(obj, "getCompactTranslatedTitle", lambda: None)() or
      obj.getTitle() or obj.getId()
  )
  if not name == 'talkback':
    result.append( { 'id'      : name
                       , 'title'   : title
                       , 'url'     : '%s/%s/view%s' % (portal_url, '/'.join(now), param)
                       }
                    )

return result
