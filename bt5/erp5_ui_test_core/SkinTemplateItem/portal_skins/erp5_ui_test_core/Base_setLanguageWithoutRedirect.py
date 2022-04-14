# pylint:disable=redefined-builtin
# select_language is a builtin because of a Localizer.itools.i18n.accept patch

context.Base_doLanguage(select_language)
# Don't redirect. Base_doLanguage tries to redirect to the same page
# and then selenium main page is loaded again in the bottom frame of
# the original selenium main page and one more selenium test starts
# running in another frame. This happens recursively.
context.REQUEST.RESPONSE.setStatus(200)
return 'done'
