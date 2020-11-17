from __future__ import print_function
# Monkey Patch the zope.contenttype to be able to detect svg image format.
try:
  import zope.contenttype

  original_text_type = zope.contenttype.text_type
  def svg_fix_text_type(s):
    s = s.strip()
    if '<html>' not in s and "<svg" in s:
      return 'image/svg+xml'

    # If it is not an svg, just try original behaviour.
    # This preserve the further improvements on zope.contenttype
    # and preserve the fix.
    return original_text_type(s)

  # Overwrite original method with the SVG detection fix.
  zope.contenttype.text_type = svg_fix_text_type

except ImportError:
  print("Skip to patch zope.contenttype, because it is not present.")
