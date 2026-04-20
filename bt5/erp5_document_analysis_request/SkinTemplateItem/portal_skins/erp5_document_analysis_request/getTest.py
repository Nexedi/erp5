# Example code:
import numpy as np
import StringIO
import matplotlib.image as mpimg

# Return a string identifying this script.
print "This is the", script.meta_type, '"%s"' % script.getId(),
if script.title:
    print "(%s)" % html_quote(script.title),
print "in", container.absolute_url()
print "test"
title = 15
# Get original image
portal = context.getPortalObject()
obj = portal.portal_catalog(follow_up_title=title, portal_type="Image")

for item in obj:
  print item.getTitle()

print "------------------"
return printed
