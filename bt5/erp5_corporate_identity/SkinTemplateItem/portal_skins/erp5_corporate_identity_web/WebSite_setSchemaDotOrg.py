'''=============================================================================
                 Adds schemaDotOrg discoverable descriptions
        https://schema.org/ | https://developers.google.com/schemas/
        https://schema.org/docs/full.html
        NOTE: Schema defines categories applied to web sites/sections/pages
        NOTE: Organizations cannot be declared currently hardcoded
============================================================================='''

'''
portal_type = context.getPortalType()
website = context.getWebSiteValue()
website_url = website.getAbsoluteUrl()
website_name = website.getProperty('title')
website_fallback_image = website.getProperty('layout_seo_open_graph_image', '')

#hardcoded (can't store on organization)
facebook_handle = 'https://www.facebook.com/pages/Nexedi/168462169880320'
twitter_handle = 'https://twitter.com/nexedi'
google_handle = ''

# always add website information, no matter displayed
result = []
result.append('<script type="application/ld+json">')
result.append('{')
result.append('"@context": "http://schema.org",')
result.append('"@type": "WebSite",')
result.append(''.join(['"@url": "', website_url, '",']))
result.append('"potentialAction": {')
result.append('"@type": "InteractAction",')
result.append(''.join(['"target": "', website_url, '/contact"']))
result.append('}')
result.append('</script>')

# on a website, we add above and hardcoded organization info
if portal_type == 'Web Site':
  result.append('<script type="application/ld+json">')
  result.append('{')
  result.append('"@context": "http://schema.org",')
  result.append('"@type": "Organization",')
  result.append(''.join(['"name": "', website_name, '",']))
  result.append(''.join(['"url": "', website_url, '",']))
  result.append(''.join(['"logo": "', website_fallback_image, '?format=png&amp;display=xsmall",']))
  result.append(''.join(['"sameAs":["', facebook_handle, '", "', twitter_handle,'", "', google_handle, '"]']))

  # once organizations are retrieveable, could we add contact numbers
  result.append('"contactPoint": [')
  result.append('{')
  result.append('"@type" : "ContactPoint",')
  result.append('"telephone": "+33-6-62-05-76-14",')
  result.append('"contactType": "Enquiries",')
  result.append('"availableLanguage": ["French", "English", "Japanese"]')
  result.append('}, {')
  result.append('"@type" : "ContactPoint",')
  result.append('"telephone": "+49-176-9639-9023",')
  result.append('"contactType": "Enquiries",')
  result.append('"availableLanguage": ["German", "English", "French"]')
  result.append('}, {')
  result.append('"@type" : "ContactPoint",')
  result.append('"telephone": "+33-6-77-73-59-28",')
  result.append('"contactType": "Enquiries",')
  result.append('"availableLanguage": ["Chinese", "English", "French"]')
  result.append('}, {')
  result.append('"@type" : "ContactPoint",')
  result.append('"telephone": "+55-21-999-09-58-70",')
  result.append('"contactType": "Enquiries",')
  result.append('"availableLanguage": ["Portuguese", "English", "French"]')
  result.append('}')
  result.append('</script>')

# a web section should ideally be a webpage in schema.org
if portal_type == 'Web Section':
  result.append('<script type="application/ld+json">')
  result.append('{')
  result.append('"@context": "http://schema.org",')
  result.append('"@type": "Organization",')

  result.append('}')
  result.append('</script>')

return '\n'.join(result)



"""
I could use categories, if we would have
schema/WebSite
schema/WebPage
schema/AboutPage
schema/ProfilePage
schema/CheckoutPage
schema/CollectionPage
schema/ContactPage
schema/ItemPage


about = AboutPage
value = ProfilePage
success = ~ CheckoutPage
innovation = ~ CheckoutPage
free software = CollectionPage & Item = Product/Software
jobs = ~ CheckoutPage
contact = ContactPage
Solution = CollectionPage & Item = Product/Software
Service = CollectionPage & Item = Service
Press = CollectionPage
Blog = CollectionPage
Team = CheckoutPage



#import re

#portal_type = context.getPortalType()
#website = context.getWebSiteValue()
#website_url = website.getAbsoluteUrl()
#website_name = website.getProperty('title')
#website_fallback_image = website.getProperty('layout_seo_open_graph_image', '')

#def generateImageUrl(my_url, my_image, my_size):
#  return ''.join([my_url, '/', my_image, "?format=png&amp;display=", my_size])

#def generateOpenGraphMeta(my_title, my_url, my_description, my_image):
#  result = []

#  result.append('<!-- OpenGraph -->')
#  result.append('<meta property="og:type" content="website"/>')
#  result.append('<meta property="og:site_name" content="%s"/>' % (website_name))
#  result.append('<meta property="og:title" content="%s"/>' % (my_title))
#  result.append('<meta property="og:url" content="%s"/>' % (my_url))
#  result.append('<meta property="og:description" content="%s"/>' % (my_description))
#  result.append('<meta property="og:image" content="%s"/>' % (my_image))

#  result.append('<!-- Twitter Card -->')
#  result.append('<meta name="twitter:card" content="summary"/>')
#  result.append('<meta name="twitter:site" content="%s"/>' % (''.join(["@", website_name])))
#  result.append('<meta name="twitter:title" content="%s"/>' % (my_title))
#  result.append('<meta name="twitter:url" content="%s"/>' % (my_url))
#  result.append('<meta name="twitter:description" content="%s"/>' % (my_description))
#  result.append('<meta name="twitter:image" content="%s"/>' % (my_image))

#  return '\n'.join(result)

#def generateOpenGraphParamaters(my_context, has_text_content=None):
#  document = my_context
#  document_url = document.getAbsoluteUrl()
#  document_title = document.getProperty("short_title")
#  document_description = document.getProperty("description")

#  # test if an image is labelled for open-graph in this documents textContent
#  if has_text_content is not None:
#    document_content = document.getProperty("text_content")
#    document_image_list = re.findall("<img(.*?)/>", document_content)
#    document_image = generateImageUrl(website_url, website_fallback_image, "xsmall")

#    for image_candidate in document_image_list:
#      if "data-open-graph-image" in image_candidate:
#        match = re.search('src="([^"]+)"', image_candidate)
#        if match:
#          document_image = match.group(1).split("?")[0]
#  else:
#    document_background = document.getProperty('layout_content_background')

#    if document_background is not None:
#      document_image = generateImageUrl(document_url, document_background, "xlarge")
#    else:
#      document_image = generateImageUrl(document_url, website_fallback_image, "xsmall")

#  return generateOpenGraphMeta(
#    document_title,
#    document_url,
#    document_description,
#    document_image
#  )

#if portal_type == 'Web Page':
#  return generateOpenGraphParamaters(context, True)

#if portal_type == 'Web Section':
#  websection = context
#  default_document = websection.getDefaultDocumentValue()

#  if default_document is not None:
#    return generateOpenGraphParamaters(default_document, True)
#  else:
#    return generateOpenGraphParamaters(websection)

#if portal_type == 'Web Site':
#  default_document = website.getDefaultDocumentValue()

#  if default_document is not None:
#    return generateOpenGraphParamaters(default_document, True)
#  else:
#    return generateOpenGraphParamaters(website)

#return ''



'''
