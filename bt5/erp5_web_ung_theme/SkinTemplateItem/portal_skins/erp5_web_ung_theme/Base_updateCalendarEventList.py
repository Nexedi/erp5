<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="PythonScript" module="Products.PythonScripts.PythonScript"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>Script_magic</string> </key>
            <value> <int>3</int> </value>
        </item>
        <item>
            <key> <string>_bind_names</string> </key>
            <value>
              <object>
                <klass>
                  <global name="NameAssignments" module="Shared.DC.Scripts.Bindings"/>
                </klass>
                <tuple/>
                <state>
                  <dictionary>
                    <item>
                        <key> <string>_asgns</string> </key>
                        <value>
                          <dictionary>
                            <item>
                                <key> <string>name_container</string> </key>
                                <value> <string>container</string> </value>
                            </item>
                            <item>
                                <key> <string>name_context</string> </key>
                                <value> <string>context</string> </value>
                            </item>
                            <item>
                                <key> <string>name_m_self</string> </key>
                                <value> <string>script</string> </value>
                            </item>
                            <item>
                                <key> <string>name_subpath</string> </key>
                                <value> <string>traverse_subpath</string> </value>
                            </item>
                          </dictionary>
                        </value>
                    </item>
                  </dictionary>
                </state>
              </object>
            </value>
        </item>
        <item>
            <key> <string>_body</string> </key>
            <value> <string>"""\n
  Script to load all events and organize all data to be loaded on calendar.\n
  XXX - This script should be splitted, because have many different\n
  features(i.e add, remove and update events)\n
"""\n
from json import dumps\n
from DateTime import DateTime\n
import random\n
\n
def convertToERP5DateTime(date):\n
  if not date:\n
    return None\n
  date, hour = date.split()\n
  month, day, year = date.split("/")\n
  return DateTime("%s/%s/%s %s" % (month, day, year, hour))\n
\n
if context.portal_membership.isAnonymousUser():\n
  return dumps(dict(events=[]))\n
\n
portal = context.getPortalObject()\n
form = context.REQUEST.form\n
portal_type_list = ["Acknowledgement",\n
                    "Fax Message",\n
                    "Letter",\n
                    "Mail Message",\n
                    "Note",\n
                    "Phone Call",\n
                    "Short Message",\n
                    "Site Message",\n
                    "Visit",\n
                    "Web Message"]\n
\n
if request_type == "list":\n
  kw = {}\n
  if form.has_key("SearchableText"):\n
    kw["SearchableText"] = form.get("SearchableText")\n
    kw["sort_on"] = (("delivery.start_date", "ASC"))\n
    kw["delivery.start_date"] = {"range": "min", "query": DateTime()}\n
  event_list = portal.event_module.searchFolder(**kw)\n
  now = DateTime()\n
  event_dict = {}\n
  event_dict["events"] = []\n
  event_dict["issort"] = True\n
  event_dict["start"] = (now-30).strftime("%m/%d/%Y %H:%M")\n
  event_dict["end"] = (now+30).strftime("%m/%d/%Y %H:%M")\n
  event_dict["error"] = None\n
  for event in event_list:\n
    if event.getStartDate() is None or event.getStopDate() is None:\n
      continue\n
    start = event.getStartDate().strftime("%m/%d/%Y %H:%M")\n
    end = event.getStopDate().strftime("%m/%d/%Y %H:%M")\n
    if event.getStartDate().Date() == event.getStopDate().Date():\n
      display_minimized = 0\n
    else:\n
      display_minimized = 1\n
    event_dict["events"].append([random.randrange(10000, 99999),\n
                                 event.getTitle(),\n
                                 start,\n
                                 end,\n
                                 0, display_minimized, 0,\n
                                 random.randrange(-1,13), 1,\n
                                 event.getId(),\n
                                 event.getPortalType(),\n
                                 event.getDescription()])\n
  return dumps(event_dict)\n
\n
elif request_type == "remove":\n
  title = form.get("title")\n
  catalog_object = portal.portal_catalog.getResultValue(portal_type=portal_type_list,\n
                                                        title=title)\n
  event = context.restrictedTraverse(catalog_object.getPath())\n
  portal.event_module.deleteContent(event.getId())\n
  return dumps({"IsSuccess": True})\n
\n
elif request_type == "update":\n
  event_id = form.get("event_id")\n
  if not event_id:\n
    return dumps({"IsSuccess": False})\n
  title = form.get("title")\n
  text_content = form.get("event_text_content")\n
  end_date = convertToERP5DateTime(form.get("CalendarEndTime"))\n
  start_date = convertToERP5DateTime(form.get("CalendarStartTime"))\n
  catalog_object = portal.portal_catalog.getResultValue(portal_type=portal_type_list,\n
                                                        id=event_id)\n
  event = context.restrictedTraverse(catalog_object.getPath())\n
  event_portal_type = form.get(\'event_portal_type\')\n
  if event.getPortalType() != event_portal_type and event_portal_type in portal_type_list:\n
    new_event = portal.event_module.newContent(portal_type=event_portal_type)\n
    new_event.edit(start_date=start_date,\n
                   end_date=end_date,\n
                   title=title,\n
                   description=text_content)\n
    portal.event_module.deleteContent(event.getId())\n
  else:\n
    kw = {}\n
    if title and event.getTitle() != title:\n
      kw["title"] = title\n
    if text_content and event.getDescription() != text_content:\n
      kw["description"] = text_content\n
    if start_date is not None:\n
      kw["start_date"] = start_date\n
    if end_date is not None:\n
      kw["stop_date"] = end_date\n
    event.edit(**kw)\n
  return dumps({"IsSuccess": True})\n
\n
elif request_type == "add":\n
  portal_type = form.get("portal_type")\n
  if not portal_type:\n
    return dumps({"IsSuccess": False})\n
  end_date = convertToERP5DateTime(form.get("CalendarEndTime"))\n
  start_date = convertToERP5DateTime(form.get("CalendarStartTime"))\n
  event_title = form.get("CalendarTitle")\n
  event = portal.event_module.newContent(portal_type=portal_type, title=event_title)\n
  event.setStartDate(start_date)\n
  event.setStopDate(end_date)\n
  return dumps({"IsSuccess": True, "Data": {"title": event_title}})\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>request_type</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_updateCalendarEventList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
