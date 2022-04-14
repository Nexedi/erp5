web_page_context = context.getPortalType() in ['Test Page', 'Web Page']

if web_page_context:
  no_web_page = False
  form_id = 'view'
else:
  no_web_page = not request.has_key('web_page') or request['web_page'] is None or not request['web_page']
  form_id = 'Zuite_viewRunZeleniumTestDialog'

no_reference = not request.has_key('web_page_reference') or request['web_page_reference'] is None or not request['web_page_reference']
no_url = not request.has_key('url') or request['url'] is None or not request['url']

if no_web_page and no_url and no_reference:
  if validator:
    return 0
  else:
    return dict(result = False, form_id = form_id, portal_status_message=context.Base_translateString("External Url (url), ERP5 Web Page Path (web_page) and ERP5 Web Page Reference (web_page_reference): were omitted, one of them must be set."))
elif not (no_url or no_web_page) or not (no_reference or no_web_page):
  if validator:
    return 0
  elif web_page_context:
    return dict(result=False, 
                form_id=form_id, 
                portal_status_message=context.Base_translateString("url, web_page and web_page_reference don't need to be set in Web Page context."))
  else:
    return dict(result=False, 
                form_id=form_id, 
                portal_status_message=context.Base_translateString("You have to choose between External Url (url), ERP5 Web Page Path (web_page) and ERP5 Web Page Reference (web_page_reference). Only ONE of them must be set."))

if validator:
  return 1
else:
  return dict(result = True)
