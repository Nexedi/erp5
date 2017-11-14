"""
================================================================================
Upgrade link for the specific type of display
================================================================================
"""
import re

link_href = re.findall("href=['\"](.*?)['\"]", link_string)[0]

# XXX flag if broken link
if link_href.find("http") == -1:
  link_obj = context.restrictedTraverse(link_href.split("?")[0])
  if link_obj:
    link_title = link_obj.getTitle()

if link_string.find("title=") == -1:
  link_title_href = ''.join(["title='", (link_title or link_href) + ",' href="])
  link_string = link_string.replace("href=", link_title_href)

if link_toc:
  link_text = re.findall('<a.*?>(.*)</a>', link)[0]
  link_string = link_string.replace(link_text, "AD")
  link_string = ''.join([" [", link_string, "]"])

return link_string
