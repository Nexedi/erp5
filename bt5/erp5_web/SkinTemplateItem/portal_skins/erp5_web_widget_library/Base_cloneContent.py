"""
  Create new Content by cloning an existing document
  or by creating a new document.

  This script is called by the admin toolbox.

  Cloning or creation is prevented if document already exists
  with same reference, version, language. Pretty messages
  are provided to the user.
"""
context.Base_createCloneDocument(web_mode=1,
                                                                    clone=clone,
                                                                    form_id=form_id,
                                                                    editable_mode=editable_mode)
