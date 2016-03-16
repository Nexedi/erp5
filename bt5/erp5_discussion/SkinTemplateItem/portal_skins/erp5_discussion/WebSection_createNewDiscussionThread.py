"""
 This script allows to create a new Discussion Thread.
"""
from zExceptions import Unauthorized

MARKER = ['', None, []]

portal = context.getPortalObject()
person = portal.ERP5Site_getAuthenticatedMemberPersonValue()

version = '001'
language = portal.Localizer.get_selected_language()
has_website = context.getWebSiteValue() is not None

try:
  user_assignment_dict = portal.ERP5Site_getPersonAssignmentDict()
except Unauthorized:
  # not in all cases current logged in user may access its details
  user_assignment_dict = {'group_list': [], 'site_list':[]}

if group_list in MARKER:
  group_list = user_assignment_dict['group_list']
if site_list in MARKER:
  site_list = user_assignment_dict['site_list']

# set predicate settings for current Web Section
if has_website:
  membership_criterion_category_list = context.getMembershipCriterionCategoryList()
  multimembership_criterion_base_category_list = context.getMultimembershipCriterionBaseCategoryList()

reference = context.Base_generateReferenceFromString(title)

if has_website:
  existing_document = context.getDocumentValue(reference)
  existing_web_section_list = portal.portal_catalog(id=reference, portal_type=['Web Site', 'Web Section'])
  existing_module_list = portal.portal_catalog(id=reference, parent_uid=portal.getUid())
  if existing_document is not None \
    or len(existing_web_section_list) \
    or len(existing_module_list):
    # if there are other document or any tarversal objects (module, web section)
    # which ID or reference duplicates just add some random part
    # so we can distinguish)
    reference = '%s-%s' %(context.Base_generateRandomString(), reference)

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

if has_website:
  for base_category in multimembership_criterion_base_category_list:
    #create_kw['%s_list' %base_category] = [x for x in membership_criterion_category_list if x.startswith(base_category)]
    category_list.extend([x for x in membership_criterion_category_list if x.startswith(base_category)])

discussion_thread = portal.discussion_thread_module.newContent(
                      portal_type = "Discussion Thread",
                      **create_kw)
# as we create a thread under a "root" predicate web section copy
# all categories from it to create thread, this way thread will be part
# of web section (through getDocumentValue API)
discussion_thread.setCategoryList(category_list)

# predecessor
if predecessor is None:
  redirect_url = context.getAbsoluteUrl()
else:
  predecessor_object = context.restrictedTraverse(predecessor)
  predecessor_portal_type = predecessor_object.getPortalType()
  redirect_url = predecessor_object.getAbsoluteUrl()

  # predecessor will only be set on document = web section default page
  if predecessor_portal_type == 'Web Section':
    predecessor_default_page = predecessor_object.getAggregate()
    if predecessor_default_page is not None:
      predecessor_document = context.restrictedTraverse(predecessor_default_page)
      discussion_thread.setPredecessorValueList([predecessor_document])
  
  # set predecessor on document
  if predecessor_portal_type == 'Web Page':
    discussion_thread.setPredecessorValueList([predecessor_object])

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
  document_kw = {'batch_mode': True,
                 'redirect_to_document': False,
                 'file': file}
  document = context.Base_contribute(**document_kw)

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

return context.Base_redirect(redirect_url=redirect_url,
         keep_items = dict(portal_status_message=context.Base_translateString(portal_status_message),
                           thread_relative_url=discussion_thread.getRelativeUrl()))
