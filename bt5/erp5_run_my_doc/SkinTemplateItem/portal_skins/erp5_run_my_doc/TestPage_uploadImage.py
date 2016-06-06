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
            <value> <string>"""\n
  Create an image object and upload the image if necessary\n
"""\n
\n
translateString = context.Base_translateString\n
\n
if image_caption in ["", None]:\n
  image_caption = chapter_title\n
\n
if edit_mode:\n
  msg = translateString(\'Slide updated.\')\n
else:\n
  msg = translateString(\'Slide created.\')\n
\n
def createImage(image_id):\n
  return context.newContent(portal_type = \'Embedded File\',\n
                                title=image_caption,\n
                                id=image_id)\n
\n
if slide_type in [\'Screenshot\', \'Illustration\'] and upload_image:\n
  if not(file is None or not file):\n
    if edit_mode:\n
      try:\n
        image = context.restrictedTraverse(context.getPath() + \'/\' + image_id)\n
      except:\n
        image = createImage(image_id)\n
        msg += \' Image %s created.\' % image_id\n
    else:\n
      image = createImage(image_id)\n
      msg += \' Image %s created.\' % image_id\n
\n
\n
  image.edit(file=file)\n
\n
  msg += \' Image content uploaded to %s.\' % image.getRelativeUrl()\n
\n
  if image_caption not in ["", None]:\n
    image.setTitle(image_caption)\n
\n
  if batch_mode:\n
    return image\n
\n
form_id = context.REQUEST.get(\'dialog_id\', None)\n
context.Base_redirect(form_id,\n
                      keep_items = dict(portal_status_message=translateString(msg)))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>image_id, file, edit_mode = 0, slide_type = \'Illustration\', chapter_title = \'\', batch_mode = False, image_caption = None, upload_image = 1, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TestPage_uploadImage</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
