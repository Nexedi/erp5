portal = context.getPortalObject()
event_module = portal.getDefaultModule(event_type)
event_module.newContent(
  start_date=start_date,
  text_content=text_content,
  title=title,
  description=description,
  portal_type=event_type)
