select_list = [l.strip() for l in kw.pop("select_columns", "").split(",")]

if select_list:
  kw["select_list"] = select_list

return context.searchFolder(**kw)
