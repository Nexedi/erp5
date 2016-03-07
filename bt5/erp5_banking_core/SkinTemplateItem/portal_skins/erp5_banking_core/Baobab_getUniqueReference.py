# first try to get the reference
try:
  reference = context.getSourceReference()
except AttributeError:
  return ''

application_id = 'BA'

N_ = context.Base_translateString

# if it's not defined, try to generate it
if reference in (None, '') or not str(reference).startswith(application_id):
  date = context.getCreationDate()
  if date in (None, ''):
    message = N_("No date defined")
    return message
  year = date.strftime('%Y')

  # codification
  source = context.getSourceValue()
  if source not in (None, ''):
    codification = source.getCodification()
    if codification in (None, ''):
      return ''
  else:
    # get from document site
    site = context.getSiteValue()
    if site not in (None, ''):
      codification = site.getCodification()
      if codification in (None, ''):
        return ''
    else:
      # get source from user site
      site_list = context.Baobab_getUserAssignedSiteList()
      if len(site_list) == 0:
        return ''
      else:
        site = site_list[0]
        site_value = context.restrictedTraverse('portal_categories/%s' %(site,))
        codification = site_value.getCodification()
        if codification in (None, ''):
          return ''

  # actual generation
  #if reference in (None, ''): 
  #XXX is it necessary to concatenate to an old reference ?
  # this make reference look strange when using different script to
  # generate reference based on criteria the user can play with
  baobab_id_group = (application_id, codification, year)
  new_id = context.portal_ids.generateNewLengthId(id_group = baobab_id_group,  default=1)

  # affectation
  reference = "%s-%s-%s-%s" % (application_id, codification, year, new_id)
  context.setSourceReference(reference)

# finally, return it
return reference
