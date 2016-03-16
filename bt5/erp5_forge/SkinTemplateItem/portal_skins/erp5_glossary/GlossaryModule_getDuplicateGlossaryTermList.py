kw['language_title'] = kw.get('language_title', '') or '%'
kw['business_field_title'] = kw.get('business_field_title', '') or '%'
return context.getPortalObject().GlossaryModule_zGetDuplicateGlossaryTermList(selection_params=kw)
