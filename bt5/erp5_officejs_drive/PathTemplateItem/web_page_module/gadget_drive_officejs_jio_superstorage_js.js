<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="Web Script" module="erp5.portal_type"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_Access_contents_information_Permission</string> </key>
            <value>
              <tuple>
                <string>Anonymous</string>
                <string>Assignee</string>
                <string>Assignor</string>
                <string>Associate</string>
                <string>Auditor</string>
                <string>Manager</string>
                <string>Owner</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>_Add_portal_content_Permission</string> </key>
            <value>
              <tuple>
                <string>Assignor</string>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>_Change_local_roles_Permission</string> </key>
            <value>
              <tuple>
                <string>Assignor</string>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>_Modify_portal_content_Permission</string> </key>
            <value>
              <tuple>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>_View_Permission</string> </key>
            <value>
              <tuple>
                <string>Anonymous</string>
                <string>Assignee</string>
                <string>Assignor</string>
                <string>Associate</string>
                <string>Auditor</string>
                <string>Manager</string>
                <string>Owner</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>content_md5</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>default_reference</string> </key>
            <value> <string>gadget_officejs_drive_jio_superstorage.js</string> </value>
        </item>
        <item>
            <key> <string>description</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>gadget_drive_officejs_jio_superstorage_js</string> </value>
        </item>
        <item>
            <key> <string>language</string> </key>
            <value> <string>en</string> </value>
        </item>
        <item>
            <key> <string>portal_type</string> </key>
            <value> <string>Web Script</string> </value>
        </item>
        <item>
            <key> <string>short_title</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>text_content</string> </key>
            <value> <string>/*jslint indent: 2, maxerr: 3, nomen: true*/\n
/*global RSVP, Blob, jIO */\n
\n
(function (jIO) {\n
  "use strict";\n
\n
  /**\n
   * The jIO DavErp5Bridge extension\n
   *\n
   * @class DavErp5Bridge\n
   * @constructor\n
   */\n
  function DavErp5BridgeStorage(spec) {\n
    this._sub_storage = jIO.createJIO(spec.sub_storage);\n
    this._sub_type = spec.sub_storage.type;\n
  }\n
\n
  function addSlashes(s) {\n
    if (!s.startsWith(\'/\')) {\n
      s = \'/\' + s;\n
    }\n
    if (!s.endsWith(\'/\')) {\n
      s += \'/\';\n
    }\n
    return s;\n
  }\n
\n
  function removeSlashes(s) {\n
    while (s.startsWith(\'/\')) {\n
      s = s.substr(1);\n
    }\n
    while (s.endsWith(\'/\')) {\n
      s = s.substring(0, s.length - 1);\n
    }\n
    return s;\n
  }\n
\n
  function getResourceAndPosition(id) {\n
    var lastSlashIndex = id.lastIndexOf(\'/\'), //XXX what if the resource name contains \'/\' ?\n
      position = id.substring(0, lastSlashIndex),\n
      resource = id.substring(lastSlashIndex + 1);\n
    return {position:  addSlashes(position),\n
            resource: resource};\n
  }\n
\n
  DavErp5BridgeStorage.prototype.hasCapacity = function (capacity) {\n
    return (capacity === "list");\n
  };\n
\n
  // called by allDocs method\n
  DavErp5BridgeStorage.prototype.buildQuery = function (options) {\n
    if (this._sub_type === \'dav\') {\n
      return this._sub_storage.allAttachments(addSlashes(options.id))\n
        .push(function (all) {\n
          var dict = {},\n
            key;\n
          for (key in all) {\n
            if (all.hasOwnProperty(key)) {\n
              dict[key] = {\'value\': {\'id\': key, \'title\': key} };\n
            }\n
          }\n
          return dict;\n
        });\n
    }\n
    if (this._sub_type === \'erp5\') {\n
      return this._sub_storage.buildQuery({\n
        limit: [0, 100],\n
        select_list: [\'id\', \'title\'],\n
        query: \'relative_url: "\' + removeSlashes(options.id) + \'/%"\'\n
      });\n
    }\n
  };\n
\n
  DavErp5BridgeStorage.prototype.getAttachment = function (id, name) {\n
    var substorage = this._sub_storage,\n
      data;\n
    if (name === \'enclosure\') {\n
      if (this._sub_type === \'dav\') {\n
        data = getResourceAndPosition(id);\n
        return substorage.getAttachment(data.position, data.resource);\n
      }\n
      if (this._sub_type === \'erp5\') {\n
        id = removeSlashes(id);\n
        return substorage.getAttachment(id, \'links\', {format: \'json\'})\n
          .push(function (att) {\n
            return att._links.action_object_method;\n
          })\n
          .push(function (action_object_method) {\n
            if (action_object_method !== undefined) {\n
              return substorage.getAttachment(\n
                \'erp5\',\n
                action_object_method.href, // XXX action_object_method could be a list\n
                {\n
                  format: "blob"\n
                }\n
              )\n
                .push(function (attachmentContent) {\n
                  return attachmentContent;\n
                });\n
            }\n
            throw new jIO.util.jIOError("Cannot find \'action_object_method\' link on this document.", 500);\n
          });\n
      }\n
    } else {\n
      throw new jIO.util.jIOError("Only support \'enclosure\' attachment", 400);\n
    }\n
  };\n
\n
  DavErp5BridgeStorage.prototype.putAttachment = function (id, name, text) {\n
    var substorage = this._sub_storage,\n
      data;\n
    if (name === \'enclosure\') {\n
      if (this._sub_type === \'dav\') {\n
        data = getResourceAndPosition(id);\n
        return substorage.putAttachment(data.position, data.resource, text);\n
      }\n
      if (this._sub_type === \'erp5\') {\n
        data = new Blob([text], {"type" : "text/plain"});\n
        id = removeSlashes(id);\n
        return new RSVP.Queue()\n
          .push(function () {\n
            return jIO.util.readBlobAsDataURL(data);\n
          })\n
          .push(function (dataURI) {\n
            return substorage.put(id, {file: {url: dataURI.target.result}});\n
          });\n
      }\n
    }\n
    throw new jIO.util.jIOError("Only support \'enclosure\' attachment", 400);\n
  };\n
\n
  jIO.addStorage(\'daverp5mapping\', DavErp5BridgeStorage);\n
\n
}(jIO));</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>OfficeJS Drive Jio super-storage</string> </value>
        </item>
        <item>
            <key> <string>version</string> </key>
            <value> <string>001</string> </value>
        </item>
        <item>
            <key> <string>workflow_history</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAI=</string> </persistent>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="2" aka="AAAAAAAAAAI=">
    <pickle>
      <global name="PersistentMapping" module="Persistence.mapping"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value>
              <dictionary>
                <item>
                    <key> <string>document_publication_workflow</string> </key>
                    <value>
                      <persistent> <string encoding="base64">AAAAAAAAAAM=</string> </persistent>
                    </value>
                </item>
                <item>
                    <key> <string>edit_workflow</string> </key>
                    <value>
                      <persistent> <string encoding="base64">AAAAAAAAAAQ=</string> </persistent>
                    </value>
                </item>
                <item>
                    <key> <string>processing_status_workflow</string> </key>
                    <value>
                      <persistent> <string encoding="base64">AAAAAAAAAAU=</string> </persistent>
                    </value>
                </item>
              </dictionary>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="3" aka="AAAAAAAAAAM=">
    <pickle>
      <global name="WorkflowHistoryList" module="Products.ERP5Type.patches.WorkflowTool"/>
    </pickle>
    <pickle>
      <tuple>
        <none/>
        <list>
          <dictionary>
            <item>
                <key> <string>action</string> </key>
                <value> <string>publish</string> </value>
            </item>
            <item>
                <key> <string>actor</string> </key>
                <value> <string>zope</string> </value>
            </item>
            <item>
                <key> <string>comment</string> </key>
                <value> <string></string> </value>
            </item>
            <item>
                <key> <string>error_message</string> </key>
                <value> <string></string> </value>
            </item>
            <item>
                <key> <string>time</string> </key>
                <value>
                  <object>
                    <klass>
                      <global name="DateTime" module="DateTime.DateTime"/>
                    </klass>
                    <tuple>
                      <none/>
                    </tuple>
                    <state>
                      <tuple>
                        <float>1454938897.46</float>
                        <string>UTC</string>
                      </tuple>
                    </state>
                  </object>
                </value>
            </item>
            <item>
                <key> <string>validation_state</string> </key>
                <value> <string>published</string> </value>
            </item>
          </dictionary>
        </list>
      </tuple>
    </pickle>
  </record>
  <record id="4" aka="AAAAAAAAAAQ=">
    <pickle>
      <global name="WorkflowHistoryList" module="Products.ERP5Type.patches.WorkflowTool"/>
    </pickle>
    <pickle>
      <tuple>
        <none/>
        <list>
          <dictionary>
            <item>
                <key> <string>action</string> </key>
                <value> <string>edit</string> </value>
            </item>
            <item>
                <key> <string>actor</string> </key>
                <value> <string>zope</string> </value>
            </item>
            <item>
                <key> <string>comment</string> </key>
                <value>
                  <none/>
                </value>
            </item>
            <item>
                <key> <string>error_message</string> </key>
                <value> <string></string> </value>
            </item>
            <item>
                <key> <string>serial</string> </key>
                <value> <string>949.20767.26098.61730</string> </value>
            </item>
            <item>
                <key> <string>state</string> </key>
                <value> <string>current</string> </value>
            </item>
            <item>
                <key> <string>time</string> </key>
                <value>
                  <object>
                    <klass>
                      <global name="DateTime" module="DateTime.DateTime"/>
                    </klass>
                    <tuple>
                      <none/>
                    </tuple>
                    <state>
                      <tuple>
                        <float>1456139534.4</float>
                        <string>UTC</string>
                      </tuple>
                    </state>
                  </object>
                </value>
            </item>
          </dictionary>
        </list>
      </tuple>
    </pickle>
  </record>
  <record id="5" aka="AAAAAAAAAAU=">
    <pickle>
      <global name="WorkflowHistoryList" module="Products.ERP5Type.patches.WorkflowTool"/>
    </pickle>
    <pickle>
      <tuple>
        <none/>
        <list>
          <dictionary>
            <item>
                <key> <string>action</string> </key>
                <value> <string>detect_converted_file</string> </value>
            </item>
            <item>
                <key> <string>actor</string> </key>
                <value> <string>zope</string> </value>
            </item>
            <item>
                <key> <string>comment</string> </key>
                <value> <string></string> </value>
            </item>
            <item>
                <key> <string>error_message</string> </key>
                <value> <string></string> </value>
            </item>
            <item>
                <key> <string>external_processing_state</string> </key>
                <value> <string>converted</string> </value>
            </item>
            <item>
                <key> <string>serial</string> </key>
                <value> <string>0.0.0.0</string> </value>
            </item>
            <item>
                <key> <string>time</string> </key>
                <value>
                  <object>
                    <klass>
                      <global name="DateTime" module="DateTime.DateTime"/>
                    </klass>
                    <tuple>
                      <none/>
                    </tuple>
                    <state>
                      <tuple>
                        <float>1454937660.04</float>
                        <string>UTC</string>
                      </tuple>
                    </state>
                  </object>
                </value>
            </item>
          </dictionary>
        </list>
      </tuple>
    </pickle>
  </record>
</ZopeData>
