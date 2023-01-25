portal = context.getPortalObject()
publication = portal.restrictedTraverse(publication_path)
subscription = portal.restrictedTraverse(subscription_path)


# First we must get list of gid from subscriptions objects
sub_xml_method_id = subscription.getXmlBindingGeneratorMethodId()
pub_xml_method_id = publication.getXmlBindingGeneratorMethodId()

diff_list = []
append = diff_list.append

# Browse objects from subscription
sub_object_list = list(subscription.getDocumentList(id_list=id_list))
for sub_object in sub_object_list:
  # Get their gid
  gid = subscription.getGidFromObject(sub_object)
  # Retrieve the corresponding document from the publication
  pub_object = publication.getDocumentFromGid(gid)
  # Compare their xml
  try:
    sub_xml = getattr(sub_object, sub_xml_method_id)(context_document=subscription)
  except TypeError:
    sub_xml = getattr(sub_object, sub_xml_method_id)()
  if pub_object:
    try:
      pub_xml = getattr(pub_object, pub_xml_method_id)(context_document=publication)
    except TypeError:
      pub_xml = getattr(pub_object, pub_xml_method_id)()
  else:
    pub_xml = ""
  diff = portal.diffXML(xml_plugin=sub_xml, xml_erp5=pub_xml, html=False)
  context.log("Got diff for GID %s" %(gid,))
  if diff != "No diff":
    append(diff)

if len(diff_list):
  severity = len(diff_list)
  from Products.CMFActivity.ActiveResult import ActiveResult
  active_result = ActiveResult()
  active_result.edit(summary='Failed',
                     severity=severity,
                     detail='\n'.join(diff_list))
  subscription.activate(active_process=active_process,
            activity='SQLQueue',
            priority=2,).ERP5Site_saveCheckCatalogTableResult(active_result)
