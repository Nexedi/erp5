code = site.getCodification()

if code[-1] != "0":
  main_code = "%s0" %code[:-1]
  main_site = context.Baobab_getSiteFromCodification(main_code)
else:
  main_site = site

return main_site
