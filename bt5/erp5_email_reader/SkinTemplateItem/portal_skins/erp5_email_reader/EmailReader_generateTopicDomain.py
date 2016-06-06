<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="PythonScript" module="Products.PythonScripts.PythonScript"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>Script_magic</string> </key>
            <value> <int>3</int> </value>
        </item>
        <item>
            <key> <string>_bind_names</string> </key>
            <value>
              <object>
                <klass>
                  <global name="NameAssignments" module="Shared.DC.Scripts.Bindings"/>
                </klass>
                <tuple/>
                <state>
                  <dictionary>
                    <item>
                        <key> <string>_asgns</string> </key>
                        <value>
                          <dictionary>
                            <item>
                                <key> <string>name_container</string> </key>
                                <value> <string>container</string> </value>
                            </item>
                            <item>
                                <key> <string>name_context</string> </key>
                                <value> <string>context</string> </value>
                            </item>
                            <item>
                                <key> <string>name_m_self</string> </key>
                                <value> <string>script</string> </value>
                            </item>
                            <item>
                                <key> <string>name_subpath</string> </key>
                                <value> <string>traverse_subpath</string> </value>
                            </item>
                          </dictionary>
                        </value>
                    </item>
                  </dictionary>
                </state>
              </object>
            </value>
        </item>
        <item>
            <key> <string>_body</string> </key>
            <value> <string encoding="cdata"><![CDATA[

"""\n
  Generate a tree of \n
  depth, parent, **kw\n
"""\n
\n
from Products.ERP5Type.Cache import CachingMethod\n
from Products.ERP5Type.Log import log\n
#log("depth: %s parent: %s kw: %s" % (depth, repr(parent), repr(kw)))\n
#log("selection: %s" % repr(context.portal_selections.getSelectionParamsFor(\'crawled_content_selection\')))\n
\n
\n
\n
def getAvailableSubjectList(subject_list=(), container_uid=None):\n
  """\n
    Returns the list of available subjects for all documents\n
    located in the current container (if defined) and which\n
    already match all subjects of subject_list\n
\n
    NOTE: for now only 3 levels of subject are available\n
  """\n
  #log("In getAvailableSubjectList with container: %s subject_list: %s" % (container_uid, subject_list))\n
  kw = dict(subject="!=", \n
            select_expression="subject.subject", \n
            group_by_expression="subject.subject",\n
            #src__=1\n
            )\n
  if container_uid: kw[\'parent_uid\'] = container_uid\n
  subject_len = len(subject_list)\n
  for i in range(0,3):\n
    if subject_len > i:\n
      kw[\'subject_filter_%s\' % i] = subject_list[i]    \n
  result_list = context.portal_catalog(**kw)\n
  #return result_list\n
  result = filter(lambda x: x not in subject_list,\n
                map(lambda r: r.subject, result_list))\n
  result.sort()\n
  return result\n
\n
#return repr(getAvailableSubjectList(subject_list=["toto"], container=context))\n
#return getAvailableSubjectList(container=context)\n
\n
request = context.REQUEST\n
domain_list = []\n
\n
selection = context.portal_selections.getSelectionParamsFor(\'crawled_content_selection\')\n
object_path = selection.get(\'object_path\')\n
portal = context.getPortalObject()\n
external_source = portal.restrictedTraverse(object_path)\n
external_source_uid = external_source.getUid()\n
\n
getAvailableSubjectList = CachingMethod(getAvailableSubjectList, \n
      id=(\'%s_%s\' % (script.id, \'\'), \n
          \'\'),\n
      cache_factory=\'erp5_ui_short\')\n
\n
if depth == 0:\n
  domain_subject_list = getAvailableSubjectList(container_uid=external_source_uid)\n
  subject_list = ()\n
elif depth == 1:\n
  subject_list = [parent.getCriterionList()[0].identity]\n
  #log("subject_list: %s " % subject_list)\n
  domain_subject_list = getAvailableSubjectList(container_uid=external_source_uid,\n
                                         subject_list=subject_list)\n
elif depth == 2:\n
  subject_list = [parent.getCriterionList()[0].identity]\n
  subject_list += [parent.getParentValue().getCriterionList()[0].identity]\n
  #log("subject_list: %s " % subject_list)\n
  domain_subject_list = getAvailableSubjectList(container_uid=external_source_uid,\n
                                         subject_list=subject_list)\n
elif depth == 3:\n
  subject_list = [parent.getCriterionList()[0].identity]\n
  subject_list += [parent.getParentValue().getCriterionList()[0].identity]\n
  subject_list += [parent.getParentValue().getParentValue().getCriterionList()[0].identity]\n
  #log("subject_list: %s " % subject_list)\n
  domain_subject_list = getAvailableSubjectList(container_uid=external_source_uid,\n
                                         subject_list=subject_list)\n
else:\n
  domain_subject_list = ()\n
  subject_list = ()\n
\n
for subject in domain_subject_list:\n
  if subject:\n
    criterion_property_list = [\'subject\']\n
    for i in range(0,min(depth,3)):\n
      criterion_property_list.append(\'subject_filter_%s\' % i)\n
    domain = parent.generateTempDomain(id=\'sub\' + subject)\n
    domain.edit(title = subject,\n
                domain_generator_method_id=script.id,\n
                criterion_property_list=criterion_property_list)\n
    domain.setCriterion(\'subject\', identity=subject)\n
    for i in range(0, min(depth,3)):\n
      domain.setCriterion(\'subject_filter_%s\' % i, identity=subject_list[i])\n
    domain_list.append(domain)\n
\n
return domain_list\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>depth, parent, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>EmailReader_generateTopicDomain</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
