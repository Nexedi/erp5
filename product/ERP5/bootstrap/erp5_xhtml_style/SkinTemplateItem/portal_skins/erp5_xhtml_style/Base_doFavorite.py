if select_favorite is None:
  select_favorite = context.REQUEST.form["Base_doFavorite"]
if select_favorite == '':
  return
# XXX more encode should be implemented in ERP5Site_redirect.
select_favorite = select_favorite.replace(' ', '+')
return context.ERP5Site_redirect(select_favorite, **kw)
