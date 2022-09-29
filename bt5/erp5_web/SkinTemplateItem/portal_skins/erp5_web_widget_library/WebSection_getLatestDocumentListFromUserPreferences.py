web_section = None
box_relative_url = context.REQUEST.get('box_relative_url', None)
if box_relative_url is not None:
  box = context.restrictedTraverse(box_relative_url)
  preferences = box.KnowledgeBox_getDefaultPreferencesDict()
  # check if in preferences we explicitly define the section we want
  if preferences.get('preferred_section_relative_url', None) is not None:
    web_section_relative_url = preferences['preferred_section_relative_url']
    web_section = context.restrictedTraverse(web_section_relative_url, None)
  elif context.REQUEST.get('current_web_section', None) is not None:
    web_section =  context.REQUEST['current_web_section']
  # if current context is a Web Section or Web Site ..
  if web_section is None and not getattr(context, 'isDocument', 1):
    web_section = context

# fall back to site
if web_section is None:
  web_section = context.getWebSiteValue()
return web_section.getDocumentValueList(**kw)
