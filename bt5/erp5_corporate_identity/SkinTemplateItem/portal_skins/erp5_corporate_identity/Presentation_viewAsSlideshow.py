"""
================================================================================
Try to convert old OpenOffice presentations into slideshows
================================================================================
"""
# uses cloudooo to convert odp/sxi to html (quite buggy) and then salvages the
# result into a slideshow html, which is passed on as remote_content to the
# slideshow renderer

# kw-parameters   (* default)
# ------------------------------------------------------------------------------

import re

blank = ''
flags = re.MULTILINE|re.DOTALL|re.IGNORECASE

def getHeaderSlideTitle(my_doc):
  return '<h1>' + my_doc.getTitle() + '</h1>'

def getSlideList(content):
  return re.findall(r'<html>(.*?)</html>', content, flags=flags)

def getKey(item):
  return int(item[0])

# -------------------------------- Setup ---------------------------------------
if context.getPortalType() in ["Presentation"]:
  portal = context.getPortalObject()
  mimetype = 'text/html'
  content_type = context.getContentType()
  raw_data = portal.portal_transforms.convertToData(mimetype, bytes(context.getData() or b""), context=context, mimetype=content_type)
  if raw_data is None:
    raise ValueError("Failed to convert to %r" % mimetype)
  if context.REQUEST is not None:
    context.REQUEST.RESPONSE.setHeader("Content-Type", mimetype)

  # get a list of slides
  content = getSlideList(raw_data)

  # every slide is in the raw_data twice, once with the title and image as text,
  # once with the slidecontent without title. All slides are mixed randomly, so
  # we need to find out which slide contains what and then put them in their
  # correct order. We do this by extracting the links in the slides navigation
  # bar. This bar as a switch to change from image to text slides with the
  # current slide number so <a href="text3">Text</a> to switch from Graphic
  # slide 3 to Text slide 3. We use this to identify current slide
  if len(content) > 0:
    slideshow = []
    output = blank
    for slide in content:
      slide_nav =  re.search(r'<center>(.*?)</center>', slide, flags=flags).group()
      slide_nav_link_list = re.findall(r'<a(.*?)</a>', slide_nav, flags=flags)
      for link in slide_nav_link_list:

        # the header slide. Contains header and extracted text from image
        if re.search(r'>Graphic', link, flags=flags):
          pointer = re.search(r'(text|img)([0-9]*)\.', link, flags=flags)
          if pointer is not None:
            slide_header = re.search(r'<h1>(.*)?</h1>', slide, flags=flags).group()
            slideshow.append([str(pointer.group(2)), slide_header])

        # the content slide. Contains image and notes
        if re.search(r'>Text', link, flags=flags):
          pointer = re.search(r'(text|img)([0-9]*)\.', link, flags=flags)
          if pointer is not None:
            slideshow.append([str(pointer.group(2)), slide])

  # time to sort and add first slide header in case missing
  slideshow = sorted(slideshow, key=getKey)
  if '<h1' not in slideshow[0][1]:
    slideshow.insert(0, ["0", getHeaderSlideTitle(context)])

  output = ""
  section_start = '<section>'
  section_end = '</section>'

  # slideshow will contain <header>, <content>, <header>, <content>...
  # so we need to go through it two-slides at a time to assemble
  # slides
  for index in range(0, len(slideshow),2):
    slide_1st = slideshow[index]
    slide_2nd = slideshow[index+1]

    # we don't know whether header is on first or second position
    if '<h1' not in slide_1st[1]:
      go_1st = slide_2nd[1]
      go_2nd = slide_1st[1]
    else:
      go_1st = slide_1st[1]
      go_2nd = slide_2nd[1]

    go_2nd = go_2nd.replace(re.search(r'<head>.*?</center><br>', go_2nd, flags=flags).group(), blank)
    go_2nd = go_2nd.replace("<h3>Notes:</h3><br>", '<details open="open">')
    go_2nd = go_2nd.replace("</body>", "</details>")
    output = output + section_start + go_1st + go_2nd + section_end

  kw["remote_content"] = output
  return context.WebPage_viewAsSlideshow(*args, **kw)
