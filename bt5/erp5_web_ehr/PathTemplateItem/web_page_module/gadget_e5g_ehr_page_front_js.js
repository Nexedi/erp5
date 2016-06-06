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
            <value> <string>gadget_e5g_ehr_page_front.js</string> </value>
        </item>
        <item>
            <key> <string>description</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>gadget_e5g_ehr_page_front_js</string> </value>
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
            <value> <string encoding="cdata"><![CDATA[

/*global window, rJS, RSVP */\n
/*jslint nomen: true, indent: 2, maxerr: 3 */\n
(function (window, rJS, RSVP) {\n
  "use strict";\n
\n
  /////////////////////////////////////////////////////////////////\n
  // api\n
  /////////////////////////////////////////////////////////////////\n
\n
  // temporary options:\n
  //  gadget_href         [string]  url of gadget to load into a cell\n
  //  gadget_portal_link  [string]  portal type url (to avoid fetching)\n
  //  gadget_query        [object]  query parameters for data to display\n
  //  gadegt_title        [string]  title for listbox\n
  //  gadget_portal       [string]  portal type to link to\n
\n
  var HARDCODED_GRID_LIST = [\n
    [{\n
      "gadget_href": "gadget_e5g_ecrm_field_listbox_widget.html",\n
      "gadget_portal_link": "#jio_key=position_opportunity_module&view=view",\n
      "gadget_title": "Open Positions",\n
      "gadget_portal": "Position Opportunity",\n
      "gadget_query": {\n
        "query": \'portal_type: "Position Opportunity"\',\n
        "select_list": ["title"],\n
        "limit": [0, 5]\n
      }\n
    }, {\n
      "gadget_href": "gadget_e5g_ecrm_field_listbox_widget.html",\n
      "gadget_portal_link": "#jio_key=position_announcement_module&view=view",\n
      "gadget_title": "Position Announcements",\n
      "gadget_portal": "Position Announcement",\n
      "gadget_query": {\n
        "query": \'portal_type: "Position Announcement"\',\n
        "select_list": ["title"],\n
        "limit": [0, 5]\n
      }\n
    }, {\n
      "gadget_href": "gadget_e5g_ecrm_field_listbox_widget.html",\n
      "gadget_portal_link": "#jio_key=position_module&view=view",\n
      "gadget_title": "Positions",\n
      "gadget_portal": "Position",\n
      "gadget_query": {\n
        "query": \'portal_type: "Position"\',\n
        "select_list": ["title"],\n
        "limit": [0, 5]\n
      }\n
    }]\n
  ];\n
\n
  /////////////////////////////////////////////////////////////////\n
  // some methods\n
  /////////////////////////////////////////////////////////////////\n
\n
  /////////////////////////////////////////////////////////////////\n
  // RJS\n
  /////////////////////////////////////////////////////////////////\n
\n
  rJS(window)\n
\n
    /////////////////////////////////////////////////////////////////\n
    // ready\n
    /////////////////////////////////////////////////////////////////\n
    .ready(function (my_gadget) {\n
      my_gadget.property_dict = {};\n
    })\n
\n
    .ready(function (my_gadget) {\n
      return my_gadget.getElement()\n
        .push(function (my_element) {\n
          my_gadget.property_dict.element = my_element;\n
        });\n
    })\n
\n
    /////////////////////////////////////////////////////////////////\n
    // published methods\n
    /////////////////////////////////////////////////////////////////\n
\n
    /////////////////////////////////////////////////////////////////\n
    // acquired methods\n
    /////////////////////////////////////////////////////////////////\n
\n
    /////////////////////////////////////////////////////////////////\n
    // published methods\n
    /////////////////////////////////////////////////////////////////\n
\n
    /////////////////////////////////////////////////////////////////\n
    // declared methods\n
    /////////////////////////////////////////////////////////////////\n
\n
    /////////////////////////////////////////////////////////////////\n
    // declared service\n
    /////////////////////////////////////////////////////////////////\n
    .declareMethod("render", function () {\n
      var gadget = this;\n
      return new RSVP.Queue()\n
        .push(function () {\n
          return gadget.declareGadget("gadget_erp5_grid.html", {\n
            "scope": "grid"\n
          });\n
        })\n
        .push(function () {\n
          return gadget.getDeclaredGadget("grid");\n
        })\n
        .push(function (my_grid_gadget) {\n
          return my_grid_gadget.render({"layout": HARDCODED_GRID_LIST});\n
        })\n
        .push(function (my_content_gadget) {\n
          gadget.property_dict.element.appendChild(\n
            my_content_gadget.property_dict.element\n
          );\n
        });\n
    });\n
\n
}(window, rJS, RSVP));\n


]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Gadget E5G Ehr Frontpage JS</string> </value>
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
                <value> <string>sven</string> </value>
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
                        <float>1427380229.7</float>
                        <string>GMT</string>
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
                <value> <string>943.10739.23810.12168</string> </value>
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
                        <float>1432204059.88</float>
                        <string>GMT</string>
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
                <value> <string>sven</string> </value>
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
                        <float>1427380176.21</float>
                        <string>GMT</string>
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
