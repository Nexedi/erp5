pad_relative_url = context.getRelativeUrl()
edit_form_id = context.getSpecialiseValue().getEditFormId()

return '''onkeypress="submitGadgetPreferenceFormOnEnter(event, '%s','%s', '%s');"''' \
         %('gadget_preference_%s_field' %pad_relative_url.replace('/', '_'), pad_relative_url, edit_form_id)
