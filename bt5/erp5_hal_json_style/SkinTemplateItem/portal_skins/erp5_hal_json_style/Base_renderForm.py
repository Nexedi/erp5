form = getattr(context, form_id)
return context.ERP5Document_getHateoas(form=form, mode='form')
