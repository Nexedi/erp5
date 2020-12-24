#pylint:disable=redefined-builtin
"""
  Create an image object and upload the image if necessary
"""

translateString = context.Base_translateString

if image_caption in ["", None]:
  image_caption = chapter_title

if edit_mode:
  msg = translateString('Slide updated.')
else:
  msg = translateString('Slide created.')

def createImage(image_id):
  return context.newContent(portal_type = 'Embedded File',
                                title=image_caption,
                                id=image_id)

if slide_type in ['Screenshot', 'Illustration'] and upload_image:
  if not(file is None or not file):
    if edit_mode:
      image = context.restrictedTraverse(context.getPath() + '/' + image_id, None)
      if image is None:
        image = createImage(image_id)
        msg += ' Image %s created.' % image_id
    else:
      image = createImage(image_id)
      msg += ' Image %s created.' % image_id


  image.edit(file=file)

  msg += ' Image content uploaded to %s.' % image.getRelativeUrl()

  if image_caption not in ["", None]:
    image.setTitle(image_caption)

  if batch_mode:
    return image

form_id = context.REQUEST.get('dialog_id', None)
context.Base_redirect(form_id,
                      keep_items = dict(portal_status_message=translateString(msg)))
