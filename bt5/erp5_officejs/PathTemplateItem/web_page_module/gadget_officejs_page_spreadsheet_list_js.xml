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
                <string>Assignee</string>
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
                <string>Assignee</string>
                <string>Assignor</string>
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
            <key> <string>categories</string> </key>
            <value>
              <tuple>
                <string>contributor/person_module/1</string>
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
            <value> <string>gadget_officejs_page_spreadsheet_list.js</string> </value>
        </item>
        <item>
            <key> <string>description</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>gadget_officejs_page_spreadsheet_list_js</string> </value>
        </item>
        <item>
            <key> <string>language</string> </key>
            <value>
              <none/>
            </value>
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
            <value> <string encoding="cdata"><![CDATA[

/*globals window, RSVP, rJS*/\n
/*jslint indent: 2, nomen: true, maxlen: 80*/\n
(function (window, RSVP, rJS) {\n
  "use strict";\n
\n
  rJS(window)\n
    .ready(function (g) {\n
      g.props = {};\n
      return g.getElement()\n
        .push(function (element) {\n
          g.props.element = element;\n
        });\n
    })\n
    .ready(function (g) {\n
      return new RSVP.Queue()\n
        .push(function () {\n
          return RSVP.all([\n
            g.translate("validated"),\n
            g.translate("invalidated"),\n
            g.translate("Not synced!"),\n
            g.translate("Waiting for approval")\n
          ]);\n
        })\n
        .push(function (result_list) {\n
          g.props.translation_dict = {\n
            "validated": result_list[0],\n
            "invalidated": result_list[1],\n
            "Not synced!": result_list[2],\n
            "Waiting for approval": result_list[3]\n
          };\n
        });\n
    })\n
    .declareAcquiredMethod("translate", "translate")\n
    .declareAcquiredMethod("getUrlFor", "getUrlFor")\n
    .declareAcquiredMethod("updateHeader", "updateHeader")\n
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")\n
    .allowPublicAcquisition("jio_allDocs", function (param_list) {\n
      var gadget = this;\n
      return this.jio_allDocs.apply(this, param_list)\n
        .push(function (result) {\n
          var i,\n
            len;\n
          for (i = 0, len = result.data.total_rows; i < len; i += 1) {\n
            // XXX jIO does not create UUID with module inside\n
            if (result.data.rows[i].id.indexOf("module") === -1) {\n
              result.data.rows[i].value.state =\n
                gadget.props.translation_dict["Not synced!"];\n
            } else {\n
              result.data.rows[i].value.state =\n
                gadget.props.translation_dict[\n
                  result.data.rows[i].value.local_state ||\n
                    "Waiting for approval"\n
                ];\n
            }\n
          }\n
          return result;\n
        });\n
    })\n
    .declareMethod("render", function (options) {\n
      var gadget = this;\n
      return new RSVP.Queue()\n
        .push(function () {\n
          return gadget.getUrlFor({page: "add_spreadsheet"});\n
        })\n
        .push(function (url) {\n
          return gadget.updateHeader({\n
            title: "Spreadsheets",\n
            add_url: url\n
          });\n
        })\n
        .push(function () {\n
          return gadget.getDeclaredGadget("listbox");\n
        })\n
        .push(function (listbox) {\n
          return listbox.render({\n
            search_page: \'text_editor_list\',\n
            search: options.search,\n
            column_list: [{\n
              select: \'title\',\n
              title: \'Title\'\n
            }, {\n
              select: \'reference\',\n
              title: \'Reference\'\n
            }, {\n
              select: \'language\',\n
              title: \'Language\'\n
            }, {\n
              select: \'description\',\n
              title: \'Description\'\n
            }, {\n
              select: \'version\',\n
              title: \'version\'\n
            }, {\n
              select: \'modification_date\',\n
              title: \'Modification Date\'\n
            }],\n
            query: {\n
              query: \'portal_type:("Spreadsheet",)\',\n
              select_list: [\'title\', \'reference\', \'language\',\n
                            \'description\', \'version\', \'modification_date\'],\n
              limit: [0, 30]\n
              //sort_on: [["date", "descending"]]\n
            }\n
          });\n
        });\n
    });\n
\n
}(window, RSVP, rJS));

]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>OfficeJS Text Editor List JS</string> </value>
        </item>
        <item>
            <key> <string>version</string> </key>
            <value>
              <none/>
            </value>
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
                <value> <string>publish_alive</string> </value>
            </item>
            <item>
                <key> <string>actor</string> </key>
                <value> <string>bk</string> </value>
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
                        <float>1444151703.24</float>
                        <string>UTC</string>
                      </tuple>
                    </state>
                  </object>
                </value>
            </item>
            <item>
                <key> <string>validation_state</string> </key>
                <value> <string>published_alive</string> </value>
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
                <value> <string>cedric.le.ninivin</string> </value>
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
                <value> <string>947.15135.4474.14216</string> </value>
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
                        <float>1448023655.58</float>
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
                <value> <string>bk</string> </value>
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
                        <float>1444148156.24</float>
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
