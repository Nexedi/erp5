source = context.getSource()
site = context.Baobab_getVaultSite(source)

if 'devise' in source:
  return  "%s/caveau/auxiliaire/encaisse_des_devises/%s" %(site.getRelativeUrl(), source.split("/")[-1])
else:
  return  "%s/caveau/auxiliaire/%s" %(site.getRelativeUrl(), source.split("/")[-1])
