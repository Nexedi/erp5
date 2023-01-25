'''=============================================================================
   Adds <link rel="alternate" hreflang="[language] href="[href]"> for
   alternative language verions of web pages. SEO-relevant to avoid
                      duplicate page/content flags
============================================================================='''

portal_type = context.getPortalType()
website = context.getWebSiteValue()
website_url = website.getAbsoluteUrl()
default_language = website.getDefaultAvailableLanguage()
language_displayed_in_path = website.getStaticLanguageSelection()
available_language_list = website.getAvailableLanguageList()

def generateAlternativeTags(my_loop_language, my_visible_language, my_url=None):

  if my_url is None:
    my_url = website_url
    trailing_slash = ''
  else:
    trailing_slash = '/'

  if my_loop_language == default_language:
    visible_path_snippet = '/' + my_visible_language + '/'
    updated_path_snippet = '/'
  else:

    # no language indicator in path
    if my_visible_language == default_language:
      visible_path_snippet = website_url
      updated_path_snippet = website_url + '/' + my_loop_language
    else:
      visible_path_snippet = '/' + my_visible_language + trailing_slash
      updated_path_snippet = '/' + my_loop_language + trailing_slash

  return '<link rel="alternate" hreflang="%s" href="%s">' % (
    my_loop_language,
    my_url.replace(visible_path_snippet, updated_path_snippet)
  )

def generateAlternativeLanguageListForDocument(webpage):
  webpage_url = webpage.getAbsoluteUrl()
  reference = webpage.getProperty("reference")
  visible_language = webpage.getProperty("language")

  available_version_list = webpage.getDocumentValueList(
    reference=reference,
    all_languages=True,
    portal_type='Web Page',
    validation_state='published_alive'
  )

  if (reference is not None
    and visible_language is not None
    and language_displayed_in_path == 1
  ):
    result = []
    for loop_language in available_language_list:
      for document in available_version_list:
        document_language = document.getLanguage()

        if document_language == loop_language:
          if document_language != visible_language:
            result.append(
              generateAlternativeTags(
                document_language,
                visible_language,
                webpage_url
              )
            )

    return '\n'.join(result)

if portal_type == 'Web Page':
  return generateAlternativeLanguageListForDocument(context)

if portal_type == 'Web Section':
  websection = context
  websection_url = websection.getAbsoluteUrl()
  default_document = websection.getDefaultDocumentValue()

  if default_document is not None:
    return generateAlternativeLanguageListForDocument(default_document)
  else:
    result = []
    localizer_tool = context.Localizer
    visible_language = localizer_tool.get_selected_language()

    for loop_language in available_language_list:
      if loop_language != visible_language:
        result.append(
          generateAlternativeTags(
            loop_language,
            visible_language,
            websection_url
          )
        )

    return '\n'.join(result)

if portal_type == 'Web Site':
  default_document = website.getDefaultDocumentValue()

  if default_document is not None:
    return generateAlternativeLanguageListForDocument(default_document)
  else:
    result = []
    localizer_tool = context.Localizer
    visible_language = localizer_tool.get_selected_language()

    for loop_language in available_language_list:
      if loop_language != visible_language:
        result.append(generateAlternativeTags(loop_language, visible_language))

    return '\n'.join(result)

return ''
