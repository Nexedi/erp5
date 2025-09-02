"""
 This script allows to create a new Discussion Thread.
"""

portal = context.getPortalObject()
person = portal.portal_membership.getAuthenticatedMember().getUserValue()

version = '001'
language = portal.Localizer.get_selected_language()

# set predicate settings for current Discussion Forum
membership_criterion_category_list = context.getMembershipCriterionCategoryList()
multimembership_criterion_base_category_list = context.getMultimembershipCriterionBaseCategoryList()

reference = context.Base_generateReferenceFromString(title)
random_string_length = 10
while True:
  random_reference = "%s-%s" % (reference, context.Base_generateRandomString(string_length=random_string_length))
  if context.restrictedTraverse(random_reference, None) is None:
    # object does not already exist
    break
  random_string_length += 1

reference = random_reference

category_list = []
create_kw = dict(title = title,
                 source_value = person,
                 reference = reference,
                 version = version,
                 language = language,
                 description=description,
                 subject_list=subject_list,
                 classification=classification,
                 group_list=group_list,
                 site_list=site_list)

for base_category in multimembership_criterion_base_category_list:
  #create_kw['%s_list' %base_category] = [x for x in membership_criterion_category_list if x.startswith(base_category)]
  category_list.extend([x for x in membership_criterion_category_list if x.startswith(base_category)])

discussion_thread = portal.discussion_thread_module.newContent(
                      portal_type = "Discussion Thread",
                      **create_kw)
# as we create a thread under a "root" predicate discussion forum
# copy all categories from it to create a thread,
# this way thread will be part of discussion forum (through predicate's searchResults)
discussion_thread.setCategoryList(category_list)

redirect_url = None
# old forum backward compatibility redirect
if web_section:
  if predecessor is not None:
    predecessor_object = context.restrictedTraverse(predecessor)
    if predecessor_object.getPortalType() != 'Discussion Forum':
      redirect_url = predecessor_object.getAbsoluteUrl()
  if not redirect_url:
    web_section_object = context.restrictedTraverse(web_section)
    redirect_url = web_section_object.getAbsoluteUrl()

# predecessor
if predecessor is not None:
  predecessor_object = context.restrictedTraverse(predecessor)
  predecessor_portal_type = predecessor_object.getPortalType()

  # old forum backward compatibility predecessor
  # set predecessor on document
  if predecessor_portal_type == 'Web Section':
    predecessor_default_page = predecessor_object.getAggregate()
    if predecessor_default_page is not None:
      predecessor_document = context.restrictedTraverse(predecessor_default_page)
      discussion_thread.setPredecessorValueList([predecessor_document])
  if predecessor_portal_type == 'Web Page':
    discussion_thread.setPredecessorValueList([predecessor_object])

  if predecessor_portal_type == 'Discussion Forum':
    discussion_thread.setPredecessorValueList([predecessor_object])
    if not web_section:
      redirect_url = None

discussion_post = discussion_thread.newContent(
                      portal_type = "Discussion Post",
                      title = title,
                      text_content = text_content,
                      source_value = person,
                      version = version,
                      language = language)

# depending on security model Thread and Post can be directly published or shared
portal_status_message = "New discussion thread created."
discussion_thread.publish()

# handle attachments
if getattr(file, 'filename', '') != '':
  document = context.Base_contribute(
    batch_mode=True,
    redirect_to_document=False,
    synchronous_metadata_discovery=True,
    file=file,
  )

  # set relation between post and document
  discussion_post.setSuccessorValueList([document])

  # depending on security model this should be changed accordingly
  document.publish()

if send_notification_text not in ('', None):
  # we can send notifications
  person_list = []
  notification_list = send_notification_text.split('\n')
  for notification in notification_list:
    # we can assume user wanted to specify Person's title
    person_list.extend(portal.portal_catalog(portal_type='Person',
                                             title=notification,
                                             default_email_text='!='))
  if len(person_list):
    #Get message from catalog
    notification_reference = 'forum-new-thread'
    notification_message = context.NotificationTool_getDocumentValue(notification_reference, 'en')
    if notification_message is None:
      raise ValueError('Unable to found Notification Message with reference "%s".' % notification_reference)

    notification_mapping_dict = {'subject': discussion_thread.getTitle(),
                                 'url': discussion_thread.absolute_url(),
                                 'sender': portal.email_from_name }
    #Preserve HTML else convert to text
    if notification_message.getContentType() == "text/html":
      mail_text = notification_message.asEntireHTML(
        substitution_method_parameter_dict={'mapping_dict':notification_mapping_dict})
    else:
      mail_text = notification_message.asText(
        substitution_method_parameter_dict={'mapping_dict':notification_mapping_dict})
    sender = portal.portal_membership.getAuthenticatedMember().getUserValue()
    #Send email
    for recipient in person_list:
      portal.portal_notifications.sendMessage(
        sender=sender,
        recipient=recipient,
        subject=notification_message.getTitle(),
        message=mail_text,
        message_text_format=notification_message.getContentType(),
        store_as_event=False)

if redirect_url:
  return context.Base_redirect(redirect_url=redirect_url,
                               keep_items = dict(portal_status_message=context.Base_translateString(portal_status_message),
                                                 thread_relative_url=discussion_thread.getRelativeUrl()))
else:
  return discussion_post.Base_redirect(keep_items = dict(portal_status_message=context.Base_translateString(portal_status_message)))
