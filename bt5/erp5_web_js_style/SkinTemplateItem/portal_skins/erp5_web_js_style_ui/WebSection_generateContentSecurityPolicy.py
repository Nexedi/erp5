content_security_policy = "default-src 'self'; img-src 'self' data:"

if no_style_gadget_url:
  content_security_policy += "; frame-src 'self' https://www.youtube-nocookie.com/embed/"
else:
  # If not rendering gadget, fully disable javascript
  # as nothing is expected
  content_security_policy += "; script-src 'none'"

return content_security_policy
