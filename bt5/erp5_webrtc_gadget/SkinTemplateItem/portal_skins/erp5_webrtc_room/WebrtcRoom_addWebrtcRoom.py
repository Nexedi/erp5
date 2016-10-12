translateString = context.Base_translateString

room = context.newContent(
          title = title,
          portal_type = "Webrtc Room"
)

if batch_mode:
  return room

room.publish()
portal_status_message = translateString(
  "New room created"
)

return room.Base_redirect('view', 
  keep_items = dict(portal_status_message=portal_status_message), **kw)
