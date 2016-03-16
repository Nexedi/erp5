from DateTime import DateTime

form = context.REQUEST.form
portal_type = form.get("portal_type")
event_title = form.get("title")
text_content = form.get("event_text_content")
start_date = DateTime("%(start_date_year)s/%(start_date_month)s/%(start_date_day)s %(start_date_hour)s:%(start_date_minute)s" % form)
stop_date = DateTime("%(stop_date_year)s/%(stop_date_month)s/%(stop_date_day)s %(stop_date_hour)s:%(stop_date_minute)s" % form)
portal = context.getPortalObject()
event = portal.event_module.newContent(portal_type=portal_type, title=event_title)
event.setStartDate(start_date)
event.setStopDate(stop_date)
event.setDescription(text_content)
