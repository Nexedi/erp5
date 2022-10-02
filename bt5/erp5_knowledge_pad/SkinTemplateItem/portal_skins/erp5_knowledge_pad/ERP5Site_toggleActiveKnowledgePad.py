from six import string_types as basestring
toggable_pad = None
all_knowledge_pads = context.ERP5Site_getKnowledgePadListForUser(mode=mode)
if isinstance(knowledge_pad_url, basestring):
  toggable_pad = context.restrictedTraverse(knowledge_pad_url)
else:
  # we pass object
  toggable_pad = knowledge_pad_url

if toggable_pad is not None:
  if toggable_pad.getValidationState() == 'invisible':
    toggable_pad.visible()
  for pad in all_knowledge_pads:
    if pad.getObject()!=toggable_pad and pad.getValidationState()=='visible':
      pad.invisible()
if redirect:
  context.Base_redirect(form_id="view")
