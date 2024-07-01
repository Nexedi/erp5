# As a general rule, sending messages by MailHost should
# be done in an activity context that never retry.
# We do so because MailHost isn't transactional as the zodb.
# This script should then always be called in an activity
# spawned with parameters :
#     conflict_retry=False,
#     max_retry=0,
context.getPortalObject().MailHost.send(context.getData().decode())
