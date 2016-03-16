"""
  Render an entire Pad and needed JavaScript code.
  Used to make instant Pad switching.
"""
from json import dumps

pad = context.restrictedTraverse(pad_relative_url)

# render Pad's html
body = pad.KnowledgePad_viewDashboardWidget(real_context=context,
                                            columns=1)


# 'keep_items' to be used as 'params' to 'updater' javascript method call
portal_type_list = ["Web Page", "Web Illustration", "Web Table"]
keep_items = dict(SearchableText='',
                  portal_type=portal_type_list)

# generate needed JavaScript code (even for 'public' boxes)
javascript_list = []
for box in pad.objectValues():
  gadget = box.getSpecialiseValue()
  gadget_type = gadget.getRenderType()
  if box.getValidationState() in ['visible', 'invisible', 'public'] \
        and gadget_type=='asynchronous' and gadget.getValidationState()!='invisible':
    edit_form_id=gadget.getEditFormId()
    view_form_id=gadget.getViewFormId()
    base_url = '%s/%s' %(context.absolute_url(), view_form_id) 
    box_dom_id = box.getRelativeUrl().replace('/', '_')
    view_form_dom_id = '%s_content' %box_dom_id;
    javascript_code = pad.KnowledgePad_generateAjaxCall(base_url, box, \
                            view_form_dom_id, params=keep_items, \
                            ignore_security_check=1)
    javascript_list.append(javascript_code)
javascript = ''.join(javascript_list)

result = {'body': body,
          'javascript':  javascript}

return dumps(result)
