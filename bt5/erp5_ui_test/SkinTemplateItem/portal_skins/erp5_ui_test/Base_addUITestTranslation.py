catalog = context.getPortalObject().Localizer[catalog_id]
catalog.gettext(message)
catalog.message_edit(message=message, language=language, translation=translation, note=None)
return "Translation of %s updated" % (message, )
