from Products.ERP5Type.Log import log
from DateTime import DateTime

portal = context.getPortalObject()
document_type_list = portal.getPortalDocumentTypeList()
comment_list = []
followup_thread = 'follow_up/' + context.getRelativeUrl()

catalog_kw = {'portal_type': '%Post',
              'query': portal.portal_catalog.getCategoryParameterDict(
                category_list=[followup_thread]),
              'validation_state': "published"}
for post in portal.portal_catalog(**catalog_kw):
  # hardcoded content until data structure (and portal_type/module) for Post are defined
  comment_list.append((dict(
      user="hardcoded user",#event.getSourceTitle(),
      date=DateTime().ISO8601(),#"TODO: get date",#event.getStartDate().ISO8601(),
      text=post.getData(),#event.asStrippedHTML(),
      attachment_link=None,#attachment_link,
      attachment_name=None,#attachment_name,
      message_id="hardcoded message_id",#event.getSourceReference(),
  )))

return comment_list
