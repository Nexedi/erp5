params = context.portal_selections.getSelectionParamsFor('attachment_selection',
                                                    REQUEST=context.REQUEST)

if params.has_key('attachment_list'):
  return params['attachment_list']
return []
