"""Export the current selection in task report module in iCalendar format.
"""
from zExceptions import Unauthorized
# XXX bypass CookieCrumbler
if context.REQUEST.AUTHENTICATED_USER.getUserName() == 'Anonymous User':
  if context.REQUEST.get('disable_cookie_login__', 0) \
          or context.REQUEST.get('no_infinite_loop', 0)  :
    raise Unauthorized(context)
  return context.REQUEST.RESPONSE.redirect(script.id + "?disable_cookie_login__=1&no_infinite_loop=1")

def formatDate(date):
  d = "%04d%02d%02d" % (date.year(), date.month(), date.day())
  if date.hour() and date.minute():
    d += "T%02d%02d%02d" % (date.hour(), date.minute(), date.second())
  return d

def foldContent(s):
  """ fold a content line (cf RFC 2445) """
  s = s.replace(',', '\\,')
  s = s.replace('/', '\\/')
  s = s.replace('"', '\\"')
  s = s.replace('\n', '\\n')
  # FIXME: really fold, for now we return a big line, it works for most clients
  return s

def printTask(task) :
  print("""BEGIN:VTODO
DCREATED:%(creation_date)s
UID:%(uid)s
SEQUENCE:1
LAST-MODIFIED:%(modification_date)s
SUMMARY:%(title)s
STATUS:%(status)s
PRIORITY:%(priority)s""" % ( {
        'creation_date': formatDate(task.getCreationDate()),
        'uid': task.getPath(),
        'title': foldContent(task.getTitle()),
        'modification_date': formatDate(task.getModificationDate()),
        'status': task.getSimulationState() == 'delivered' and 'COMPLETED' or 'NEEDS_ACTION',
        'priority': task.getProperty('int_index', 3),
  } ))
  if task.hasComment():
    print("DESCRIPTION:" + foldContent(task.getComment()))
  if task.hasStartDate():
    print("DTSTART;VALUE=DATE:" + formatDate(task.getStartDate()))
  if task.hasStopDate():
    print("DUE;VALUE=DATE:" + formatDate(task.getStopDate()))
  organizer = task.getDestinationValue(portal_type='Person')
  if organizer:
    print("ORGANIZER;CN=%s:MAILTO:%s" % (organizer.getTitle(), organizer.getDefaultEmailText()))
    print("X-ORGANIZER:MAILTO:%s" % (organizer.getDefaultEmailText()))
  for attendee in task.getSourceValueList( portal_type = 'Person') :
    print("ATTENDEE;CN=%s:MAILTO:%s" % (attendee.getTitle(), attendee.getDefaultEmailText()))
  print("ATTACH;FMTTYPE=text/html:%s/%s/view" % (context.ERP5Site_getAbsoluteUrl(), task.getRelativeUrl()))

  print("END:VTODO")
  return printed

print("""BEGIN:VCALENDAR
PRODID:-//ERP5//NONSGML Task Report Module//EN
VERSION:2.0""")
obj_list = context.getPortalObject().portal_selections.callSelectionFor("task_report_module_selection")
for obj in obj_list :
  print(printTask(obj.getObject()))
print("END:VCALENDAR")

context.REQUEST.RESPONSE.setHeader('Content-Type', 'text/calendar')
context.REQUEST.RESPONSE.setHeader('Content-disposition',  'attachment; filename=ERP5.ics')
return printed
