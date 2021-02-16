im = context
pub = im.getSourceSectionValue()
pub_sub_list = pub.objectValues()
if not len(pub_sub_list):
  raise ValueError("%s sub in pub %s for im %s" %(len(pub_sub_list), pub.getPath(), im.getPath()))
else:
  pub_sub = pub_sub_list[0]
#pub_sub = im.getSourceSectionValue().objectValues()[0]

sub = im.getDestinationSectionValue()

pub_xml = []
sub_xml = []

for sign in sub.objectValues():
  pub_sign = pub_sub.get(sign.getId(), "No signature")
  pub_xml.append(pub_sign.getData(''))
  sub_xml.append(sign.getData(''))

pub_xml = '\n'.join(pub_xml)
sub_xml = '\n'.join(sub_xml)

return context.diffXML(sub_xml, pub_xml)
