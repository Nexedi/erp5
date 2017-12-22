"""
================================================================================
Add image size conversion only if image is not the default image
================================================================================
"""

# parameters:
# ------------------------------------------------------------------------------
# path                        Image path to embed

# XXX replace this with clear defintion of possible values for dialog params
# XXX Note, this is necessary, because it seems images scored in skin folders
# cannot convert (neither format nor size) and in wkhtmltopdf fail if a
# conversion parameter is provided.
if path.find("common") > -1:
  return path
else:
  return path + "&display=%s" % (display or "thumbnail")
