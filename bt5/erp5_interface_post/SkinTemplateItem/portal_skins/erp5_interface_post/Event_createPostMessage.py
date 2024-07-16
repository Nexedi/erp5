import six
portal = context.getPortalObject()

post_message_post_module = portal.getDefaultModuleValue(post_portal_type, None)

if isinstance(post_message_data, six.text_type):
  post_message_data = post_message_data.encode()

message_post = post_message_post_module.newContent(
  portal_type=post_portal_type,
  title="Post Message for %s" % context.getTitle(),
  data=post_message_data,
  **kw
)

message_post.prepareExport()

event_aggregate_list = context.getAggregateList()
event_aggregate_list.append(message_post.getRelativeUrl())
context.setAggregateList(event_aggregate_list)
