"""
================================================================================
Looks for <img /> with data-open-graph-image="true" from content
================================================================================
"""
import re

if item and item.getPortalType() == "Web Page":
  content_image_list = re.findall("<img(.*?)/>", item.getTextContent() or "")

  for image_candidate in content_image_list:
    if "data-open-graph-image" in image_candidate:
      match = re.search('src="([^"]+)"', image_candidate)
      if match:
        return match.group(1).split("?")[0]
