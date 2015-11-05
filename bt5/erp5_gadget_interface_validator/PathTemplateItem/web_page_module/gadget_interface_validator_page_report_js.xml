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
            <value> <string>gadget_interface_validator_page_report.js</string> </value>
        </item>
        <item>
            <key> <string>description</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>gadget_interface_validator_page_report_js</string> </value>
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
/*jslint nomen: true, indent: 2, maxerr: 3 */\n
(function (window, rJS, RSVP, Handlebars) {\n
  "use strict";\n
\n
  var INTERFACE_GADGET_SCOPE = "interface_gadget";\n
\n
  function renderInitialReport(gadget, gadget_list) {\n
    var gadget_info_list = [],\n
      row_list = [],\n
      column_list = [\'Gadget Name\', \'Declared Interfaces\', \'Validation Status\'],\n
      cell_list,\n
      default_status = "In Progress",\n
      content = \'\',\n
      item;\n
    for(item in gadget_list) {\n
      cell_list = [];\n
      cell_list.push({\n
        default_class: "gadget_name",\n
        value: gadget_list[item]\n
      });\n
      cell_list.push({\n
        default_class: "interface_list",\n
        value: default_status\n
      });\n
      cell_list.push({\n
        default_class: "validation_status",\n
        value: default_status\n
      });\n
      row_list.push({\n
        "cell_list": cell_list,\n
        "default_id": gadget_list[item].substr(0, gadget_list[item].indexOf(\'.\'))\n
        });\n
    }\n
    content += report_widget_table({\n
      column_list: column_list,\n
      row_list: row_list\n
    });\n
    gadget.props.content_element.innerHTML = content;\n
    $(gadget.props.element).trigger("create");\n
  }\n
\n
  function validateAppGadgetList(gadget, gadget_list){\n
    var item;\n
    for(item in gadget_list) {\n
      updateGadgetData(gadget, gadget_list[item]);\n
    }\n
  }\n
\n
  function updateGadgetData(gadget, verify_gadget_url) {\n
    return RSVP.Queue()\n
      .push(function() {\n
        return verifyGadgetImplementation(gadget, verify_gadget_url);\n
      })\n
      .push(function(verify_result) {\n
        var result_dict = {\n
          id: verify_gadget_url.substr(0, verify_gadget_url.indexOf(\'.\')),\n
          gadget_name: verify_gadget_url,\n
          interface_list: verify_result[0],\n
          validation_status: verify_result[1].result,\n
          validation_message: verify_result[1].result_message,\n
          error_detail: verify_result[1].details\n
        };\n
        return updateReportData(gadget, result_dict);\n
      });\n
  }\n
\n
  function verifyGadgetImplementation(gadget, verify_gadget_url) {\n
    var interface_gadget,\n
      interface_list = [],\n
      default_validation_status = {result:"N/A"};\n
    return new RSVP.Queue()\n
      .push(function() {\n
        return gadget.getDeclaredGadget(INTERFACE_GADGET_SCOPE);\n
      })\n
      .push(function(i_gadget) {\n
        interface_gadget = i_gadget;\n
        return interface_gadget.getDeclaredGadgetInterfaceList(verify_gadget_url);\n
      })\n
      .push(function(temp_interface_list) {\n
        interface_list = temp_interface_list;\n
        if(interface_list.length > 0) {\n
          return interface_gadget.verifyGadgetInterfaceImplementation(verify_gadget_url);\n
        }\n
        else {\n
          return default_validation_status;\n
        }\n
      })\n
      .push(function(validation_status) {\n
        return [interface_list, validation_status];\n
      }, function(error) {\n
        default_validation_status.result = false;\n
        default_validation_status.result_message = "Error with gadget loading";\n
        default_validation_status.details = error.message;\n
        return [interface_list, default_validation_status];\n
      });\n
  }\n
\n
  function updateReportData(gadget, report_data) {\n
    var id = "#" + report_data.id.replace(\'/\',\'\\\\/\'),\n
      update_element = gadget.props.content_element.querySelector(id),\n
      interface_data = \'\',\n
      validation_status = report_data.validation_status,\n
      validation_message = report_data.validation_message;\n
    if (report_data.interface_list.length) {\n
      var item,\n
        interface_name;\n
      for (item in report_data.interface_list) {\n
        interface_name = report_data.interface_list[item].substr(report_data.interface_list[item].lastIndexOf(\'/\') + 1);\n
        interface_data += (interface_name + \'<br />\');\n
      }\n
    } else {\n
      interface_data = \'None\';\n
    }\n
    if(report_data.validation_status === true) {\n
      validation_status = "Success";\n
      update_element.setAttribute(\'style\', \'color: green\');\n
    }\n
    if(report_data.validation_status === false) {\n
      validation_status = (validation_message !== undefined? validation_message : "Failure");\n
      update_element.setAttribute(\'style\', \'cursor: pointer; color: red\');\n
      update_element.className += "error expand";\n
    }\n
    gadget.props.error_data[report_data.id] = report_data.error_detail;\n
    update_element.querySelector(".validation_status").innerHTML = validation_status;\n
    update_element.querySelector(".validation_status").className += " final";\n
    update_element.querySelector(".interface_list").innerHTML = interface_data;\n
  }\n
\n
  function toggleErrorRow(gadget, source_element) {\n
    if(source_element.className.indexOf("expand") > -1) {\n
      var error_tr = document.createElement(\'tr\'),\n
        error_td = error_tr.insertCell(0);\n
      error_tr.id = source_element.id + \'_errordata\';\n
      error_td.className = \'errordata\';\n
      error_td.colSpan = "3";\n
      error_td.innerText = gadget.props.error_data[source_element.id];\n
      source_element.parentNode.insertBefore(error_tr, source_element.nextSibling);\n
      source_element.className = source_element.className.replace("expand","shrink");\n
    } else if(source_element.className.indexOf("shrink") > -1) {\n
      source_element.parentNode.removeChild(source_element.nextSibling);\n
      source_element.className = source_element.className.replace("shrink","expand");\n
    }\n
    return;\n
  }\n
\n
  /////////////////////////////////////////////////////////////////\n
  // Handlebars\n
  /////////////////////////////////////////////////////////////////\n
  // Precompile the templates while loading the first gadget instance\n
  var gadget_klass = rJS(window),\n
    templater = gadget_klass.__template_element,\n
    report_widget_table = Handlebars.compile(\n
      templater.getElementById("report-widget-table").innerHTML\n
    );\n
  Handlebars.registerPartial(\n
    "report-widget-table-partial",\n
    templater.getElementById("report-widget-table-partial").innerHTML\n
  );\n
\n
  gadget_klass\n
    /////////////////////////////////////////////////////////////////\n
    // ready\n
    /////////////////////////////////////////////////////////////////\n
    // Init local properties\n
    .ready(function (g) {\n
      g.props = {};\n
      g.props.error_data = {};\n
    })\n
\n
    // Assign the element to a variable\n
    .ready(function (g) {\n
      return g.getElement()\n
        .push(function (element) {\n
          g.props.element = element,\n
          g.props.content_element = element.querySelector(\'.validation_report\');\n
        });\n
    })\n
\n
    .declareMethod("render", function (options) {\n
      var gadget = this,\n
        appcache_url = options.appcache_url,\n
        gadget_list;\n
      return new RSVP.Queue()\n
        .push(function() {\n
          return gadget.getDeclaredGadget(INTERFACE_GADGET_SCOPE);\n
        })\n
        .push(function(interface_gadget) {\n
          return interface_gadget.getGadgetListFromAppcache(appcache_url);\n
        })\n
        .push(function(filtered_gadget_list) {\n
          gadget_list = filtered_gadget_list;\n
          return renderInitialReport(gadget, gadget_list);\n
        })\n
        .push(function() {\n
          return validateAppGadgetList(gadget, gadget_list);\n
        }, function(error) {\n
          return gadget.redirect({\n
            found: false\n
          });\n
        });\n
    })\n
\n
    .declareMethod("reportPageDummyMethod1", function(param1) {\n
      // A dummy method to fulfil the interface implementation requirement.\n
      return;\n
    })\n
    /////////////////////////////////////////////////////////////////\n
    // Acquired methods\n
    /////////////////////////////////////////////////////////////////\n
\n
    .declareAcquiredMethod("redirect", "redirect")\n
\n
    /////////////////////////////////////////////////////////////////\n
    // declared services\n
    /////////////////////////////////////////////////////////////////\n
    .declareService(function () {\n
      var gadget = this;\n
\n
      function rowSubmit(submit_data) {\n
        var parent_element = submit_data.target.parentElement;\n
        if(parent_element.className.indexOf("error") > -1) {\n
          return toggleErrorRow(gadget, parent_element);\n
        }\n
      }\n
\n
      return loopEventListener(\n
        gadget.props.content_element,\n
        \'click\',\n
        false,\n
        rowSubmit\n
      );\n
    });\n
\n
}(window, rJS, RSVP, Handlebars));

]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Gadget Interface Validator Reportpage JS</string> </value>
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
                        <float>1444138717.03</float>
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
                <value> <string>946.54878.32293.23654</string> </value>
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
                        <float>1446717974.43</float>
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
                        <float>1444138661.94</float>
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
