"""
================================================================================
Downgrade headers in passed content by 1 or number of levels specified
================================================================================
"""
import re

def pushDown(level):
  return ''.join(["h", str(level), ">"])

for header in re.findall("<h[1-6].*</h[1-6]>", content or ""):
  tag = re.findall("<(h[1-6]>)", header)[0] #h2>
  key = tag[1]
  content = content.replace(
    header,
    header.replace(tag, pushDown(int(key) + (downgrade or 1)))
  )

return content
