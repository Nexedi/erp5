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

"Jump to gitlab or gitweb web interface to view commit"\n
\n
portal = context.getPortalObject()\n
test_suite_list = portal.portal_catalog(\n
  portal_type=\'Test Suite\',\n
  validation_state=(\'validated\', \'invalidated\'),\n
  title={\'query\': context.getTitle(), \'key\': \'ExactMatch\'})\n
\n
if not test_suite_list:\n
  return []\n
\n
test_suite = sorted(\n
  [test_suite.getObject() for test_suite in test_suite_list],\n
  key=lambda test_suite: test_suite.getValidationState() == \'validated\')[0]\n
\n
# TODO: make this jump test suite\n
\n
# decode the reference ( ${buildout_section_id}=${number of commits}-${hash},${buildout_section_id}=${number of commits}-${hash}, ... ) \n
repository_dict = {}\n
for repository_string in context.getReference().split(\',\'):\n
  repository_code, revision = repository_string.split(\'-\')\n
  repository_dict[repository_code.split(\'=\')[0]] = revision\n
\n
\n
result_list = []\n
from Products.PythonScripts.standard import Object\n
\n
def makeVCSLink(repository_url, revision):\n
  # https://user:pass@lab.nexedi.cn/user/repo.git -> https://user:pass@lab.nexedi.cn/user/repo/commit/hash\n
  if \'lab.nexedi.cn\' in repository_url and repository_url.endswith(\'.git\'):\n
    repository_url = repository_url[:-len(\'.git\')]\n
  if \'@\' in repository_url: # remove credentials\n
    scheme = repository_url.split(\':\')[0] \n
    url = \'%s://%s/commit/%s\' % (scheme, repository_url.split(\'@\')[1], revision )\n
  else:\n
    url = \'%s/commit/%s\' % (repository_url, revision )\n
  # gitweb for git.erp5.org\n
  if \'/repos/\' in url:\n
    url = url.replace(\'/repos/\', \'/gitweb/\')\n
    url = url.replace(\'/commit/\', \'/commitdiff/\')\n
\n
  def getListItemUrl(*args, **kw):\n
    return url\n
  \n
  return Object(\n
    uid=\'new_\',\n
    getUid=lambda: \'new_\',\n
    getListItemUrl=getListItemUrl,\n
    repository=repository_url,\n
    revision=revision)\n
  \n
for repository in test_suite.contentValues(portal_type=\'Test Suite Repository\'):\n
  result_list.append(\n
    makeVCSLink(\n
      repository.getProperty(\'git_url\'),\n
      repository_dict[repository.getProperty(\'buildout_section_id\')]))\n
\n
if len(result_list) == 1:\n
  from zExceptions import Redirect\n
  raise Redirect(result_list[0].getListItemUrl())\n
\n
return result_list\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>*args, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TestResult_getJumpVCSResultList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
