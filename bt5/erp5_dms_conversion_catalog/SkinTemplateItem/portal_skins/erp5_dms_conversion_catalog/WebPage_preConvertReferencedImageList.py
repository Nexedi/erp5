"""
  Get all images inside a document and try to pre convert relative ones
"""
portal = context.getPortalObject()

MARKER = (None, '',)
API_ARGUMENT_LIST = ['format', 'display', 'display_list', 'quality', 'resolution']
validation_state = ('released', 'released_alive', 'published', 'published_alive',
                    'shared', 'shared_alive', 'public', 'validated')

def convertUrlArgumentsToDict(convert_string):
  convert_kw = {}
  # some editors when creating wbe page content do escape '&' properly
  convert_string = convert_string.replace('&amp;', '&')

  # convert from URL string to python arguments dict
  for pair in convert_string.split('&'):
    arg_list = pair.split('=')
    if len(arg_list)==2:
      convert_kw[arg_list[0]] = arg_list[1]
  return convert_kw

image_url_list = context.Base_extractImageUrlList()
for image_url in image_url_list:
  if not image_url.startswith('http://') and not image_url.startswith('https://'):
    # try to use only relative URLs
    part_list = image_url.split('?')
    if len(part_list)==2:
      # don't deal with bad URLs (having more than one '?') inside
      reference = part_list[0]
      convert_string = part_list[1]

      # check we have locally such a reference so we can convert it
      catalog_kw = {'portal_type': portal.getPortalDocumentTypeList() + portal.getPortalEmbeddedDocumentTypeList(),
                    'reference': reference,
                    'validation_state': validation_state}

      document = portal.portal_catalog.getResultValue(**catalog_kw)
      if document is not None:
        # try to pre convert it based on extracted URL's arguments
        convert_kw = convertUrlArgumentsToDict(convert_string)

        # XXX: we do check if "data" methods exists on pretending to be Document portal types
        # we need a way to do this by introspection
        if ((getattr(document, "getData", None) is not None and document.getData() not in MARKER) or \
           (getattr(document, "getBaseData", None) is not None and document.getBaseData() not in MARKER)):
          if 'display' in convert_kw.keys():
            # conversion script aggregate all possible display options into a list
            convert_kw['display_list'] = [convert_kw.pop('display')]

          # only certain arguments make sense due to API so leave only them
          for key in convert_kw.keys():
            if key not in API_ARGUMENT_LIST:
              convert_kw.pop(key)

          # due to API we need certain arguments
          if convert_kw.get('quality') is None:
            convert_kw['quality'] = kw.get('quality')

          # do real conversion
          format = convert_kw.get('format')
          quality = convert_kw.get('quality')
          if format not in MARKER and quality not in MARKER:
            # format is mandatory if it's missing then anyway URL request will fail so
            # don't bother create an activity
            document.activate(priority=4, tag="conversion", activity="SQLQueue").Base_callPreConvert(**convert_kw)
