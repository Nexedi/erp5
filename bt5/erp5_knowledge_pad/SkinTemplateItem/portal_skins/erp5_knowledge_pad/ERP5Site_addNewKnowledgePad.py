from Products.ERP5Type.ImmediateReindexContextManager import ImmediateReindexContextManager
with ImmediateReindexContextManager() as immediate_reindex_context_manager:
  pad = context.knowledge_pad_module.newContent(portal_type='Knowledge Pad',
                                                immediate_reindex=immediate_reindex_context_manager,
                                                title = pad_title)
  # for web mode
  if mode in ('web_front', 'web_section',):
    # in Web Mode we can have a temporary Web Site objects created based on current language
    real_context = context.Base_getRealContext()
    pad.setPublicationSectionValue(real_context)

  # set it as active
  context.ERP5Site_toggleActiveKnowledgePad(pad, mode=mode, redirect=False)

if redirect_url:
  return context.REQUEST.RESPONSE.redirect(redirect_url)
else:
  # adding is done though either AJAX call or programatically
  return pad.getRelativeUrl()
