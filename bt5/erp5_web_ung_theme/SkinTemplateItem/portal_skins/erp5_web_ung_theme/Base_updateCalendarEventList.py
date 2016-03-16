"""
  Script to load all events and organize all data to be loaded on calendar.
  XXX - This script should be splitted, because have many different
  features(i.e add, remove and update events)
"""
from json import dumps
from DateTime import DateTime
import random

def convertToERP5DateTime(date):
  if not date:
    return None
  date, hour = date.split()
  month, day, year = date.split("/")
  return DateTime("%s/%s/%s %s" % (month, day, year, hour))

if context.portal_membership.isAnonymousUser():
  return dumps(dict(events=[]))

portal = context.getPortalObject()
form = context.REQUEST.form
portal_type_list = ["Acknowledgement",
                    "Fax Message",
                    "Letter",
                    "Mail Message",
                    "Note",
                    "Phone Call",
                    "Short Message",
                    "Site Message",
                    "Visit",
                    "Web Message"]

if request_type == "list":
  kw = {}
  if form.has_key("SearchableText"):
    kw["SearchableText"] = form.get("SearchableText")
    kw["sort_on"] = (("delivery.start_date", "ASC"))
    kw["delivery.start_date"] = {"range": "min", "query": DateTime()}
  event_list = portal.event_module.searchFolder(**kw)
  now = DateTime()
  event_dict = {}
  event_dict["events"] = []
  event_dict["issort"] = True
  event_dict["start"] = (now-30).strftime("%m/%d/%Y %H:%M")
  event_dict["end"] = (now+30).strftime("%m/%d/%Y %H:%M")
  event_dict["error"] = None
  for event in event_list:
    if event.getStartDate() is None or event.getStopDate() is None:
      continue
    start = event.getStartDate().strftime("%m/%d/%Y %H:%M")
    end = event.getStopDate().strftime("%m/%d/%Y %H:%M")
    if event.getStartDate().Date() == event.getStopDate().Date():
      display_minimized = 0
    else:
      display_minimized = 1
    event_dict["events"].append([random.randrange(10000, 99999),
                                 event.getTitle(),
                                 start,
                                 end,
                                 0, display_minimized, 0,
                                 random.randrange(-1,13), 1,
                                 event.getId(),
                                 event.getPortalType(),
                                 event.getDescription()])
  return dumps(event_dict)

elif request_type == "remove":
  title = form.get("title")
  catalog_object = portal.portal_catalog.getResultValue(portal_type=portal_type_list,
                                                        title=title)
  event = context.restrictedTraverse(catalog_object.getPath())
  portal.event_module.deleteContent(event.getId())
  return dumps({"IsSuccess": True})

elif request_type == "update":
  event_id = form.get("event_id")
  if not event_id:
    return dumps({"IsSuccess": False})
  title = form.get("title")
  text_content = form.get("event_text_content")
  end_date = convertToERP5DateTime(form.get("CalendarEndTime"))
  start_date = convertToERP5DateTime(form.get("CalendarStartTime"))
  catalog_object = portal.portal_catalog.getResultValue(portal_type=portal_type_list,
                                                        id=event_id)
  event = context.restrictedTraverse(catalog_object.getPath())
  event_portal_type = form.get('event_portal_type')
  if event.getPortalType() != event_portal_type and event_portal_type in portal_type_list:
    new_event = portal.event_module.newContent(portal_type=event_portal_type)
    new_event.edit(start_date=start_date,
                   end_date=end_date,
                   title=title,
                   description=text_content)
    portal.event_module.deleteContent(event.getId())
  else:
    kw = {}
    if title and event.getTitle() != title:
      kw["title"] = title
    if text_content and event.getDescription() != text_content:
      kw["description"] = text_content
    if start_date is not None:
      kw["start_date"] = start_date
    if end_date is not None:
      kw["stop_date"] = end_date
    event.edit(**kw)
  return dumps({"IsSuccess": True})

elif request_type == "add":
  portal_type = form.get("portal_type")
  if not portal_type:
    return dumps({"IsSuccess": False})
  end_date = convertToERP5DateTime(form.get("CalendarEndTime"))
  start_date = convertToERP5DateTime(form.get("CalendarStartTime"))
  event_title = form.get("CalendarTitle")
  event = portal.event_module.newContent(portal_type=portal_type, title=event_title)
  event.setStartDate(start_date)
  event.setStopDate(end_date)
  return dumps({"IsSuccess": True, "Data": {"title": event_title}})
