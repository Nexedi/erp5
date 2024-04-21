'''=============================================================================
              Adds open graph meta for Twitter and Facebook
        https://developers.facebook.com/docs/sharing/best-practices
        NOTE: add data-open-graph-image="true" to <img/> for OpenGraph
============================================================================='''

portal_type = context.getPortalType()
website = context.getWebSiteValue()
web_site_default_document = website.getDefaultDocumentValue()
website_url = website.getAbsoluteUrl()
website_name = website.getProperty('short_title')
website_fallback_image = website.getProperty('layout_seo_open_graph_image', '')

def generateImageUrl(my_url, my_image, my_size):
  return ''.join([my_url, '/', my_image, "?format=png&amp;display=", my_size])

def generateOpenGraphMeta(my_title, my_url, my_description, my_image):
  result = []

  result.append('<!-- OpenGraph -->')
  result.append('<meta property="og:type" content="website"/>')
  result.append('<meta property="og:site_name" content="%s"/>' % (website_name))
  result.append('<meta property="og:title" content="%s"/>' % (my_title))
  result.append('<meta property="og:url" content="%s"/>' % (my_url))
  result.append('<meta property="og:description" content="%s"/>' % (my_description))
  result.append('<meta property="og:image" content="%s"/>' % (my_image))

  result.append('<!-- Twitter Card -->')
  result.append('<meta name="twitter:card" content="summary"/>')
  result.append('<meta name="twitter:site" content="%s"/>' % (''.join(["@", website_name])))
  result.append('<meta name="twitter:title" content="%s"/>' % (my_title))
  result.append('<meta name="twitter:url" content="%s"/>' % (my_url))
  result.append('<meta name="twitter:description" content="%s"/>' % (my_description))
  result.append('<meta name="twitter:image" content="%s"/>' % (my_image))

  return '\n'.join(result)

def generateOpenGraphParamaters(my_context, has_text_content=None):
  document = my_context
  document_url = document.getAbsoluteUrl()
  document_title = document.getProperty("short_title") or document.getProperty("title")
  document_description = document.getProperty("description")

  # test if an image is labelled for open-graph in this documents textContent
  if has_text_content is not None:
    document_image = generateImageUrl(website_url, website_fallback_image, "xsmall")
    document_image_candidate = context.WebPage_getOpenGraphImage(document)
    if document_image_candidate:
      document_image = document_image.replace(website_fallback_image, document_image_candidate)
  else:
    document_background = document.getProperty('layout_content_background')

    if document_background is not None:
      document_image = generateImageUrl(document_url, document_background, "xlarge")
    else:
      document_image = generateImageUrl(document_url, website_fallback_image, "xsmall")

  return generateOpenGraphMeta(
    document_title,
    document_url,
    document_description,
    document_image
  )


if portal_type == 'Web Page':
  if context.getReference() !=  web_site_default_document.getReference():
    return generateOpenGraphParamaters(context, True)
  return generateOpenGraphParamaters(website)

if portal_type == 'Web Section':
  websection = context
  return generateOpenGraphParamaters(websection)

if portal_type == 'Web Site':
  return generateOpenGraphParamaters(website)

return ''
