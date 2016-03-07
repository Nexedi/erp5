# New mail must be received
if context.getValidationState() == 'draft':
  context.receive()

# We assign the mailbox
# (this should be moved to metadata discovery)
id = context.getId()
mailbox = id.split('-')[0]
subject_list = mailbox.split('.')
if not subject_list:
  subject_list = ['INBOX']
context.setSubjectList(subject_list)

# Let us check if this is Junk
bogosity = context.getContentInformation().get('X-Bogosity', 'No')
if bogosity.startswith('Yes') or bogosity.startswith('Spam') or 'Junk' in subject_list or 'Spam' in subject_list:
  context.spam()

# Let us check if this is sent by us
if context.getSender() and context.getSender().find('jp@nexedi.com') >= 0 and context.getValidationState() == 'new':
  if context.getRecipient() and context.getRecipient().find('jp@nexedi.com') >= 0:
    pass
  else:
    context.markAsSent()
if context.getSender() and context.getSender().find('jp@tiolive.com') >= 0 and context.getValidationState() == 'new':
  if context.getRecipient() and context.getRecipient().find('jp@tiolive.com') >= 0:
    pass
  else:
    context.markAsSent()
