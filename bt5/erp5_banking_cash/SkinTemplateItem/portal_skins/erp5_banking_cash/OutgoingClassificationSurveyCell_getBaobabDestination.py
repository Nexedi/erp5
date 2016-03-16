document_site = context.getRootDeliveryValue().getBaobabSourceValue()
site_url = context.Baobab_getVaultSite(document_site).getRelativeUrl()
if context.getEmissionLetter() in context.Baobab_getEmissionLetterList(site_list=[site_url, ]):
  return '%s/caveau/serre/encaisse_des_billets_retires_de_la_circulation' % site_url
else:
  return '%s/caveau/auxiliaire/encaisse_des_externes' % site_url
