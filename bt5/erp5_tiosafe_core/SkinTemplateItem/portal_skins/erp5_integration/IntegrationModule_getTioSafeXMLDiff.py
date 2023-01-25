im = context
pub_source = im.getSourceSectionValue().getSourceValue()
pub_list = im.getSourceSectionValue().getListMethodId()
pub_xml_method = im.getSourceSectionValue().getXmlBindingGeneratorMethodId()
sub_source = im.getDestinationSectionValue().getSourceValue()
sub_list = im.getDestinationSectionValue().getListMethodId()
sub_xml_method = im.getDestinationSectionValue().getXmlBindingGeneratorMethodId()

pub_method = getattr(pub_source, pub_list, None)
sub_method = getattr(sub_source, sub_list, None)

pub_xml = []
sub_xml = []
def tiosafe_sort(a,b):
  if getattr(a, 'email', None):
    return cmp(a.email, b.email)
  elif getattr(a, 'getDefaultEmailText', None) and len(a.getDefaultEmailText("")):
    return cmp(a.getDefaultEmailText(), b.getDefaultEmailText())
  elif getattr(a, 'reference', None):
    return cmp(a.reference, b.reference)
  elif getattr(a, 'getReference', None) and len(a.getReference("")):
    return cmp(a.getReference(), b.getReference())
  elif getattr(a, 'title', None):
    return cmp(a.title, b.title)
  else:
    return cmp(a.id, b.id)


if pub_method is not None and sub_method is not None:
  pub_object = pub_method(context_document=im.getSourceSectionValue())
  pub_object.sort(cmp=tiosafe_sort)
  for ob in pub_object:
    try:
      pub_xml.append(getattr(ob, pub_xml_method)(context_document=im.getSourceSection()))
    except TypeError:
      pub_xml.append(getattr(ob, pub_xml_method)())

  sub_object = sub_method(context_document=im.getDestinationSectionValue())
  sub_object.sort(cmp=tiosafe_sort)
  for ob in sub_object:
    try:
      sub_xml.append(getattr(ob, sub_xml_method)(context_document=im.getDestinationSection()))
    except TypeError:
      sub_xml.append(getattr(ob, sub_xml_method)())

else:
  raise ValueError("Impossible to get method, pub_method = %s from %s, sub_method = %s from %s" %(pub_method, pub_list, sub_method, sub_list,))

pub_xml = '\n'.join(pub_xml)
sub_xml = '\n'.join(sub_xml)

return context.diffXML(xml_plugin=sub_xml, xml_erp5=pub_xml, html=html)
