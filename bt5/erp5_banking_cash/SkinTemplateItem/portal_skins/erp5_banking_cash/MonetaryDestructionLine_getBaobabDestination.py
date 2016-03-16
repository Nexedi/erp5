# By default, the destination of a monetary destruction must
# be None in order to destroy ressources
destination = None

if context.getParentValue().isDematerialization() \
  and context.getSource() is not None \
  and context.getSourceSection() is not None:
  # We must in this case set the destination to a particular vault
  site = context.Baobab_getVaultSite(context.getSource())
  site_relative_url = site.getRelativeUrl()
  section_id = context.getSourceSectionId()
  destination = "%s/%s/%s" % (site_relative_url,
                              "caveau/serre/encaisse_des_billets_neufs_non_emis_en_transit_allant_a",
                              section_id)
return destination
