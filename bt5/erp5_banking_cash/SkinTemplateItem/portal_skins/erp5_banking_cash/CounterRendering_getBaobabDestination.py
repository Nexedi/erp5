source = context.getSource()
if source is not None:
  if source.endswith('/entrante'):
    source = source[:-len('/entrante')]
  if source.endswith('/sortante'):
    source = source[:-len('/sortante')]
  site = context.Baobab_getVaultSite(source).getRelativeUrl()
  if 'devise' in source:
    return  "%s/surface/caisse_courante/%s" % (site, "/".join(source.split("/")[-2:]))
  else:
    return  "%s/surface/caisse_courante/encaisse_des_billets_et_monnaies" % site
return source
