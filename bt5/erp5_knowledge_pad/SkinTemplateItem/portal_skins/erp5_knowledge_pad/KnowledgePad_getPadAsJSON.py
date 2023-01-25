"""
  Render an entire Pad and needed JavaScript code.
  Used to make instant Pad switching.
"""
from json import dumps

pad = context.restrictedTraverse(pad_relative_url)

# render Pad's html
body = pad.KnowledgePad_viewDashboardWidget(real_context=context)

# toggle new active pad
context.ERP5Site_toggleActiveKnowledgePad(pad_relative_url, mode, redirect=False)

# generate needed JavaScript code
javascript_list = []
for box in pad.searchFolder(portal_type='Knowledge Box',
                            validation_state=['visible', 'invisible']):
  box = box.getObject()
  gadget = box.getSpecialiseValue()
  gadget_type = gadget.getRenderType()
  if gadget_type=='asynchronous' and gadget.getValidationState()!='invisible':
    edit_form_id=gadget.getEditFormId()
    view_form_id=gadget.getViewFormId()
    base_url = '%s/%s' %(context.absolute_url(), view_form_id)
    box_dom_id = box.getRelativeUrl().replace('/', '_')
    view_form_dom_id = '%s_content' %box_dom_id;
    javascript_code = pad.KnowledgePad_generateAjaxCall(base_url, box, \
                            view_form_dom_id, ignore_security_check=1)
    javascript_list.append(javascript_code)
javascript = ''.join(javascript_list)
# return JSON
result = {'body': body,
          'javascript':  javascript}
return dumps(result)
