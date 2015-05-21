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
            <value> <string>gadget_e5g_ecrm_field_listbox_widget.js</string> </value>
        </item>
        <item>
            <key> <string>description</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>gadget_e5g_ecrm_field_listbox_widget_js</string> </value>
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

/*global window, rJS, RSVP, Handlebars */\n
/*jslint nomen: true, indent: 2 */\n
(function (window, rJS, RSVP, Handlebars) {\n
  "use strict";\n
\n
  /////////////////////////////////////////////////////////////////\n
  // api handlebars\n
  /////////////////////////////////////////////////////////////////\n
\n
  // listbox_widget_header = {\n
  //   "left_link_list": [\n
  //     {"link_title": [string], "link_href": [string]}\n
  //   ],\n
  //   "listbox_title": [string],\n
  //   "right_link_list": [\n
  //     {"link_title": [string], "link_href": [string]}\n
  //   ]\n
  // }\n
  // listbox_widget_search = {\n
  //   "search_title": [string]\n
  // }\n
  // listbox_widget_table = {\n
  //   "column_list": [\n
  //     {"column_title": [string]}\n
  //   ]\n
  // }\n
  // listbox_widget_table_partial = {\n
  //   "table_row_list": [{\n
  //     "table_cell_list": [\n
  //       {{"cell_title": [string], "cell_href": [string]}\n
  //     ]\n
  //   }]\n
  // }\n
\n
  /////////////////////////////////////////////////////////////////\n
  // templates\n
  /////////////////////////////////////////////////////////////////\n
  var gadget_klass = rJS(window),\n
    templater = gadget_klass.__template_element,\n
\n
    listbox_widget_header = Handlebars.compile(\n
      templater.getElementById("listbox-widget-header").innerHTML\n
    ),\n
    listbox_widget_table = Handlebars.compile(\n
      templater.getElementById("listbox-widget-table").innerHTML\n
    ),\n
    listbox_widget_table_partial = Handlebars.registerPartial(\n
      "listbox-widget-table-partial",\n
      templater.getElementById("listbox-widget-table-partial").innerHTML\n
    );\n
\n
  /////////////////////////////////////////////////////////////////\n
  // some methods\n
  /////////////////////////////////////////////////////////////////\n
\n
  gadget_klass\n
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
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")\n
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")\n
    .declareAcquiredMethod("whoWantToDisplayThis", "whoWantToDisplayThis")\n
    .declareAcquiredMethod("translateHtml", "translateHtml")\n
\n
    /////////////////////////////////////////////////////////////////\n
    // declared methods\n
    /////////////////////////////////////////////////////////////////\n
    .declareMethod(\'render\', function (my_option_dict) {\n
      var gadget = this,\n
        content = \'\',\n
        result;\n
\n
      // store initial configuration and query\n
      gadget.property_dict.initial_query\n
        = gadget.property_dict.initial_query || my_option_dict.gadget_query;\n
      gadget.property_dict.option_dict =\n
        gadget.property_dict.option_dict || my_option_dict;\n
\n
      return new RSVP.Queue()\n
        .push(function () {\n
          return gadget.jio_allDocs(my_option_dict.gadget_query);\n
        })\n
        .push(function (my_result) {\n
          var link_list = [],\n
            i_len,\n
            i;\n
\n
          result = my_result;\n
\n
          for (i = 0, i_len = result.data.total_rows; i < i_len; i += 1) {\n
            link_list.push(gadget.whoWantToDisplayThis(result.data.rows[i].id));\n
          }\n
\n
          return RSVP.all(link_list);\n
        })\n
        .push(function (my_link_list) {\n
          var query = gadget.property_dict.option_dict.gadget_query,\n
            column_list = [],\n
            table_row_list = [],\n
            table_cell_list,\n
            i_len,\n
            i,\n
            j_len,\n
            j;\n
\n
          // build handlebars object\n
\n
          // loop select_list to build columns\n
          for (i = 0, i_len = query.select_list.length; i < i_len; i += 1) {\n
            column_list.push({"column_title": query.select_list[i]});\n
          }\n
\n
          for (j = 0, j_len = result.data.total_rows; j < j_len; j += 1) {\n
            table_cell_list = [];\n
            for (i = 0, i_len = query.select_list.length; i < i_len; i += 1) {\n
              table_cell_list.push({\n
                "cell_href": my_link_list[j],\n
                "cell_title": result.data.rows[j].value[query.select_list[i]]\n
              });\n
            }\n
            table_row_list.push({"table_cell_list": table_cell_list});\n
          }\n
          content += listbox_widget_header({\n
            "listbox_title": my_option_dict.gadget_title,\n
            "right_link_list": [{\n
              "link_title": "All",\n
              "link_href": gadget.property_dict.option_dict.gadget_portal_link\n
            }]\n
          });\n
          content += listbox_widget_table({\n
            "column_list": column_list,\n
            "table_row_list": table_row_list\n
          });\n
\n
          return gadget.translateHtml(content);\n
        })\n
        .push(function (my_translated_html) {\n
          gadget.property_dict.element.querySelector(".custom-grid .ui-body-c")\n
            .innerHTML = my_translated_html;\n
          return gadget;\n
        });\n
    });\n
\n
    /////////////////////////////////////////////////////////////////\n
    // declared service\n
    /////////////////////////////////////////////////////////////////\n
\n
}(window, rJS, RSVP, Handlebars));\n


]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Gadget E5G Ecrm Field Listbox Widget JS</string> </value>
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
                        <float>1427813550.21</float>
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
                <value> <string>943.9410.37394.25582</string> </value>
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
                        <float>1432202379.05</float>
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
                        <float>1427813514.41</float>
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
