from json import dumps

# sometime instead of real knowledge pad object we may get just its relative url
# and actually that's what we care for
if not isinstance(box, str):
  box_relative_url = box.getRelativeUrl()
else:
  box_relative_url = box

editable_mode = context.REQUEST.get('editable_mode', 0)
if editable_mode:
  editable_mode = 1
else:
  editable_mode = 0

js_update_code = """updater('%s', '%s', '%s', '%s', %s, field_prefix='%s');""" %(url, box_relative_url, dom_id,
                                                              editable_mode, dumps(params), field_prefix)
if box.getValidationState()=='invisible':
  # we can generate
  javascript_code = """invisible_gadgets["%s"]="%s";""" %(dom_id, js_update_code)
else:
  javascript_code = js_update_code

return javascript_code
