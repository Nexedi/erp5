"""
 Old forum backward compatibility script
 This script allows to create a new Discussion Thread
"""

portal = context.getPortalObject()
person = portal.ERP5Site_getAuthenticatedMemberPersonValue()

version = '001'
language = portal.Localizer.get_selected_language()

# get the related forum using follow_up
result = context.getFollowUpRelatedValueList(portal_type = "Discussion Forum")
valid_states = ('published', 'published_alive', 'released', 'released_alive', 'shared', 'shared_alive')
result = [forum for forum in result if forum.getValidationState() in valid_states]
if result:
  forum = result[0]
else:
  raise ValueError, 'Unable to found a valid Discussion Forum for the current web site/section'

# set predicate settings for current Discussion Forum
membership_criterion_category_list = forum.getMembershipCriterionCategoryList()
multimembership_criterion_base_category_list = forum.getMultimembershipCriterionBaseCategoryList()

reference = forum.Base_generateReferenceFromString(title)
random_string_length = 10
while True:
  random_reference = "%s-%s" % (reference, forum.Base_generateRandomString(string_length=random_string_length))
  if forum.restrictedTraverse(random_reference, None) is None:
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
contributor_list = discussion_thread.getContributorValueList()
discussion_thread.setCategoryList(category_list)

discussion_post = discussion_thread.newContent(
                      portal_type = "Discussion Post",
                      title = title,
                      text_content = text_content,
                      source_value = person,
                      version = version,
                      language = language)

# depending on security model Thread and Post can be directly published or shared
portal_status_message = "New discussion created."
# examine category_list and if follow_up is used consider private
has_classification = len([x for x in category_list if x.startswith("classification/")])
has_group = len([x for x in category_list if x.startswith("group/")])
has_classification_and_group = has_classification and has_group
is_private_project = len([x for x in category_list if x.startswith('follow_up') and not x.startswith('follow_up/product_module/')])  # XXX please see DiscussionThread_createNewDiscussionPost

if has_classification_and_group:
  # private forum based on classification & group security
  discussion_thread.share()
elif is_private_project:
  # private forum based on project security
  discussion_thread.setClassification('collaborative/project')
  discussion_thread.share()
else:
  # public forum
  discussion_thread.publish()
#Set contributor back on thread as it has been removed
#when category list was set above.
discussion_thread.setContributorValueList(contributor_list)
# handle attachments
if getattr(file, 'filename', '') != '':
  if person:
    document_kw = {'batch_mode': True,
                   'synchronous_metadata_discovery': True,
                   'redirect_to_document': False,
                   'file': file}
    document = forum.Base_contribute(**document_kw)
  else:
    document_kw = {'batch_mode': True,
                   'discover_metadata': 1,
                   'redirect_to_document': False,
                   'file': file}

    document = portal.portal_contributions.newContent(**document_kw)

  # set relation between post and document
  discussion_post.setSuccessorValueList([document])

  # depending on security model this should be changed accordingly
  if has_classification_and_group:
    # private forum based on classification & group security
    document.setCategoryList(category_list)
    document.share()
  elif is_private_project:
    # private forum based on project security
    document.setCategoryList(category_list)
    document.setClassification('collaborative/project')
    document.share()
  else:
    # public forum
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
    notification_message = forum.NotificationTool_getDocumentValue(notification_reference, 'en')
    if notification_message is None:
      raise ValueError, 'Unable to found Notification Message with reference "%s".' % notification_reference

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
    sender = portal.ERP5Site_getAuthenticatedMemberPersonValue()
    #Send email
    for recipient in person_list:
      portal.portal_notifications.sendMessage(
        sender=sender,
        recipient=recipient,
        subject=notification_message.getTitle(),
        message=mail_text,
        message_text_format=notification_message.getContentType(),
        store_as_event=False)

return context.Base_redirect(redirect_url=context.getAbsoluteUrl(),
                             keep_items = dict(portal_status_message=context.Base_translateString(portal_status_message),
                                               thread_relative_url=discussion_thread.getRelativeUrl()))
