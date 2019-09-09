"Modified version for ERP5 to append the default action (/view) in the URL."

portal = context.getPortalObject()

utool = portal.portal_url
portal_url = utool()
param = '?ignore_layout:int=1' if int(portal.REQUEST.get('ignore_layout', 0)) else ''
if include_root:
    result = [{
        'id'    : 'root',
        'title' : portal.portal_properties.title(),
        'url'   : '%s/view%s' % (portal_url, param),
    }]
else:
    result = []

obj = portal
now = []
for name in utool.getRelativeContentPath(context):
    obj = obj.restrictedTraverse(name)
    now.append(name)
    title = (
      getattr(obj, "getCompactTranslatedTitle", lambda: None)() or
      obj.getTitle() or obj.getId()
    )
    if name != 'talkback':
        result.append( { 'id'      : name
                       , 'title'   : title
                       , 'url'     : '%s/%s/view%s' % (portal_url, '/'.join(now), param)
                       }
                    )

return result
