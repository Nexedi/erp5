portal = context.getPortalObject()
#default_time_zone = portal.portal_preferences.getPreferredTimeZone()
preferred_date_order = portal.portal_preferences.getPreferredDateOrder()

def format_date(date):
  # XXX modification date & creation date are still in server timezone.
  #   See merge request !17
  #
  # if default_time_zone:
  #   date = date.toZone(default_time_zone)
  if preferred_date_order == 'dmy':
    return "%s/%s/%s&nbsp;&nbsp;&nbsp;%s" % (date.dd(), date.mm(), date.year(), date.TimeMinutes())
  if preferred_date_order == 'mdy':
    return "%s/%s/%s&nbsp;&nbsp;&nbsp;%s" % (date.mm(), date.dd(), date.year(), date.TimeMinutes())
  # ymd
  return "%s/%s/%s&nbsp;&nbsp;&nbsp;%s" % (date.year(), date.mm(), date.dd(), date.TimeMinutes())

creation_date = format_date(context.getCreationDate())
modification_date = format_date(context.getModificationDate())
owner = context.Base_getOwnerTitle()
container.REQUEST.RESPONSE.setHeader('Content-Type', 'text/html')
return """
<html>
  <body>
    <div id="creation_date">{creation_date}</div>
    <div id="modification_date">{modification_date}</div>
    <div id="owner">{owner}</div>
  </body>
</html>
""".format(
  creation_date=creation_date,
  modification_date=modification_date,
  owner=owner)
