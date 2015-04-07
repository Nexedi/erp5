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
            <key> <string>content_md5</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>default_reference</string> </key>
            <value> <string>gadget_erp5_grid.js</string> </value>
        </item>
        <item>
            <key> <string>description</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>rjs_gadget_erp5_grid_js</string> </value>
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

/*global window, rJS, RSVP, document */\n
/*jslint nomen: true, indent: 2, maxerr: 3 */\n
(function (window, document, rJS, RSVP) {\n
  "use strict";\n
\n
  /////////////////////////////////////////////////////////////////\n
  // some methods\n
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
    .declareMethod(\'render\', function (my_option_dict) {\n
      var gadget = this,\n
        props = gadget.property_dict,\n
        content_container;\n
\n
      // declare or load a cell gadget\n
      function fetchAndRenderGadget(my_config_dict) {\n
        return new RSVP.Queue()\n
          .push(function () {\n
            return gadget.declareGadget(\n
              my_config_dict.gadget_href,\n
              {"scope": "grid_" + my_config_dict.grid_location}\n
            );\n
          })\n
          .push(function (my_gadget_instance) {\n
            return my_gadget_instance.render(my_config_dict);\n
          });\n
      }\n
\n
      // generate requests to load data. On first call, also create html\n
      function setFragment() {\n
        var row_dict,\n
          row_container,\n
          cell_dict,\n
          i_len,\n
          i,\n
          j_len,\n
          j;\n
\n
        content_container = document.createDocumentFragment();\n
\n
        for (i = 0, i_len = props.layout.length; i < i_len; i += 1) {\n
          row_dict = props.layout[i];\n
          row_container = document.createElement("ul");\n
          row_container.className = \'grid-items line-\' + row_dict.length;\n
\n
          for (j = 0, j_len = row_dict.length; j < j_len; j += 1) {\n
            cell_dict = row_dict[j];\n
            row_container.appendChild(document.createElement("li"));\n
            cell_dict.grid_location = String(i) + String(j);\n
          }\n
          content_container.appendChild(row_container);\n
        }\n
      }\n
\n
      // START:\n
      props.layout = props.layout || my_option_dict.layout || [];\n
      my_option_dict.parameter_dict = my_option_dict.parameter_dict || {};\n
\n
      // set HTML frame\n
      setFragment();\n
\n
      // build HTML and assemble cell content once returned\n
      return new RSVP.Queue()\n
        .push(function () {\n
          var render_list = [],\n
            cell_dict,\n
            row,\n
            i_len,\n
            i,\n
            j_len,\n
            j;\n
\n
          for (i = 0, i_len = props.layout.length; i < i_len; i += 1) {\n
            row = props.layout[i];\n
            for (j = 0, j_len = row.length; j < j_len; j += 1) {\n
              cell_dict = row[j];\n
              cell_dict.grid_location = String(i) + String(j);\n
              render_list.push(fetchAndRenderGadget(cell_dict));\n
            }\n
          }\n
          return RSVP.all(render_list);\n
        })\n
        .push(function (my_content_list) {\n
          return new RSVP.Queue()\n
            .push(function () {\n
              var element_list = [],\n
                i_len,\n
                i;\n
\n
              for (i = 0, i_len = my_content_list.length; i < i_len; i += 1) {\n
                element_list.push(my_content_list[i].getElement());\n
              }\n
              return RSVP.all(element_list);\n
            })\n
            .push(function (my_element_list) {\n
              var grid_container,\n
                i,\n
                i_len;\n
\n
              for (i = 0, i_len = my_element_list.length; i < i_len; i += 1) {\n
                content_container.querySelectorAll(".grid-items > li")[i]\n
                  .appendChild(my_element_list[i]);\n
              }\n
\n
              grid_container = document.createElement("div");\n
              grid_container.className = "ui-grid-container ui-responsive";\n
              grid_container.appendChild(content_container);\n
              props.element.appendChild(grid_container);\n
              return gadget;\n
            });\n
        });\n
    });\n
\n
    /////////////////////////////////////////////////////////////////\n
    // declared service\n
    /////////////////////////////////////////////////////////////////\n
\n
}(window, document, rJS, RSVP));\n


]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Gadget ERP5 Grid JS</string> </value>
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
                <value> <string>publish_alive</string> </value>
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
                        <float>1427876852.94</float>
                        <string>GMT</string>
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
                <value> <string>sven</string> </value>
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
                <value> <string>942.11692.12685.57821</string> </value>
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
                        <float>1428415571.73</float>
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
                        <float>1427876819.35</float>
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
