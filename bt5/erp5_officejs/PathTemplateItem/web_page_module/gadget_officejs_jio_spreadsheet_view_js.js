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
            <value> <string>gadget_officejs_jio_spreadsheet_view.js</string> </value>
        </item>
        <item>
            <key> <string>description</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>gadget_officejs_jio_spreadsheet_view_js</string> </value>
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

/*globals window, rJS, Handlebars, RSVP, loopEventListener, console*/\n
/*jslint indent: 2, nomen: true, maxlen: 80*/\n
(function (window, RSVP, rJS, Handlebars, loopEventListener) {\n
  "use strict";\n
\n
  function saveContent(gadget, submit_event) {\n
    var i,\n
      doc = gadget.options.doc,\n
      today = new Date();\n
    doc.parent_relative_url = "document_module";\n
    doc.portal_type = "Spreadsheet";\n
    doc.modification_date = today.getDate()\n
      + \'/\' + (today.getMonth() + 1)\n
      + \'/\' + today.getFullYear();\n
    for (i = 0; i < submit_event.target.length; i += 1) {\n
      // XXX Should check input type instead\n
      if (submit_event.target[i].name) {\n
        doc[submit_event.target[i].name] = submit_event.target[i].value;\n
      }\n
    }\n
    return new RSVP.Queue()\n
      .push(function () {\n
        return gadget.getDeclaredGadget("my_text_content");\n
      })\n
      .push(function (text_content_gadget) {\n
        return text_content_gadget.getContent();\n
      })\n
      .push(function (data) {\n
        doc.data = data.text_content;\n
        doc.content_type = "application/yformat.xlsy"\n
        doc.filename = doc.title + ".xlsy"\n
        return gadget.put(gadget.options.jio_key, doc);\n
      });\n
  }\n
\n
  function maximize(gadget) {\n
    var iframe = gadget.props.element.querySelector(\'iframe\'),\n
      iframe_class_string = iframe.getAttribute(\'class\') || "",\n
      class_name = "ui-content-maximize",\n
      class_index = iframe_class_string.indexOf(class_name);\n
    if (class_index === -1) {\n
      iframe_class_string += \' \' + class_name;\n
      iframe.setAttribute(\'style\', \'\');\n
      iframe.setAttribute(\'class\', iframe_class_string);\n
      return;\n
    }\n
    iframe_class_string = iframe_class_string.substring(0, class_index)\n
      + iframe_class_string.substring(class_index + class_name.length);\n
    iframe.setAttribute(\'style\', \'width:100%; border: 0 none; height: 600px\');\n
    iframe.setAttribute(\'class\', iframe_class_string);\n
    return;\n
  }\n
\n
  var gadget_klass = rJS(window),\n
    source = gadget_klass.__template_element\n
      .querySelector(".view-web-page-template")\n
      .innerHTML,\n
    template = Handlebars.compile(source);\n
\n
\n
  gadget_klass\n
    .ready(function (g) {\n
      g.props = {};\n
      g.options = null;\n
      return g.getElement()\n
        .push(function (element) {\n
          g.props.element = element;\n
          g.props.deferred = RSVP.defer();\n
        });\n
    })\n
\n
    .declareAcquiredMethod("updateHeader", "updateHeader")\n
    .declareAcquiredMethod("get", "jio_get")\n
    .declareAcquiredMethod("translateHtml", "translateHtml")\n
    .declareAcquiredMethod("put", "jio_put")\n
    .declareAcquiredMethod(\'allDocs\', \'jio_allDocs\')\n
    .declareAcquiredMethod("redirect", "redirect")\n
\n
    .allowPublicAcquisition(\'triggerMaximize\', function () {\n
      var gadget = this;\n
      return RSVP.Queue()\n
        .push(function () {\n
          return maximize(gadget);\n
        })\n
        .fail(function (e) {\n
          console.log(e);\n
        });\n
    })\n
\n
    .allowPublicAcquisition(\'triggerSubmit\', function () {\n
      return this.props.element.querySelector(\'button\').click();\n
    })\n
\n
    .declareMethod(\'triggerSubmit\', function () {\n
      return this.props.element.querySelector(\'button\').click();\n
    })\n
\n
    .declareMethod("render", function (options) {\n
      var gadget = this;\n
      gadget.options = options;\n
      gadget.options.doc.title = gadget.options.doc.title || "";\n
      return new RSVP.Queue()\n
        .push(function () {\n
          return gadget.translateHtml(template(options.doc));\n
        })\n
        .push(function (html) {\n
          gadget.props.element.innerHTML = html;\n
          return gadget.updateHeader({\n
            title: options.doc.title + " | Spreadsheet",\n
            back_url: "#page=spreadsheet_list",\n
            panel_action: false,\n
            save_action: true\n
          });\n
        })\n
        .push(function () {\n
          return gadget.props.deferred.resolve();\n
        });\n
    })\n
\n
    /////////////////////////////////////////\n
    // Render text content gadget\n
    /////////////////////////////////////////\n
    .declareService(function () {\n
      var gadget = this,\n
        text_gadget = null;\n
\n
      return new RSVP.Queue()\n
        .push(function () {\n
          return gadget.props.deferred.promise;\n
        })\n
        .push(function () {\n
          return gadget.declareGadget(\n
            "rjsunsafe/gadget_ooffice.html",\n
            {\n
              scope: "my_text_content",\n
              sandbox: "dataurl",\n
              element: gadget.props.element.querySelector(".document-content")\n
            }\n
          );\n
        })\n
        .push(function (text_content_gadget) {\n
          var iframe = gadget.props.element.querySelector(\'iframe\');\n
          iframe.setAttribute(\n
            \'style\',\n
            \'width:100%; border: 0 none; height: 600px\'\n
          );\n
          text_gadget = text_content_gadget;\n
          return text_content_gadget.render({\n
            "key": \'text_content\',\n
            "value": gadget.options.doc.data\n
          });\n
        })\n
        .push(function () {\n
          return text_gadget.getElement();\n
        });\n
    })\n
\n
    /////////////////////////////////////////\n
    // Form submit\n
    /////////////////////////////////////////\n
    .declareService(function () {\n
      var gadget = this;\n
\n
      return new RSVP.Queue()\n
        .push(function () {\n
          return gadget.props.deferred.promise;\n
        })\n
        .push(function () {\n
          return loopEventListener(\n
            gadget.props.element.querySelector(\'form\'),\n
            \'submit\',\n
            true,\n
            function (event) {\n
              return saveContent(gadget, event);\n
            }\n
          );\n
        });\n
    });\n
\n
}(window, RSVP, rJS, Handlebars, loopEventListener));

]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>OfficeJS Jio Spreadsheet View JS</string> </value>
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
                        <float>1444170002.35</float>
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
                <value> <string>bk</string> </value>
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
                <value> <string>946.37161.13138.58606</string> </value>
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
                        <float>1445415095.01</float>
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
                        <float>1444169924.76</float>
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
