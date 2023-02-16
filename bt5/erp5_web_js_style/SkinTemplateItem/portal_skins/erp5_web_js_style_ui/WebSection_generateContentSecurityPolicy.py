content_security_policy = "default-src 'self'; img-src 'self' data:"

if no_style_gadget_url:
  web_section = context
  iframe_url_list = [x.strip() for x in web_section.getLayoutProperty('configuration_iframe_url_text', default='').split('\n') if x.strip()]
  if iframe_url_list:
    content_security_policy = "%s; frame-src 'self' %s" % (content_security_policy, ' '.join(iframe_url_list))
else:
  # If not rendering gadget, fully disable javascript
  # as nothing is expected
  content_security_policy += "; script-src 'none'"

return content_security_policy
