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
            <value> <string>gadget_jabberclient_page_connect.js</string> </value>
        </item>
        <item>
            <key> <string>description</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>jabber_gadget_page_connect_js</string> </value>
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
            <value> <string>/*global window, rJS, RSVP, loopEventListener*/\n
/*jslint nomen: true, indent: 2, maxerr: 3 */\n
(function (window, rJS, RSVP, loopEventListener) {\n
  "use strict";\n
\n
  rJS(window)\n
    /////////////////////////////////////////////////////////////////\n
    // ready\n
    /////////////////////////////////////////////////////////////////\n
    // Init local properties\n
    .ready(function (g) {\n
      g.props = {};\n
    })\n
\n
    // Assign the element to a variable\n
    .ready(function (g) {\n
      return g.getElement()\n
        .push(function (element) {\n
          g.props.element = element;\n
        });\n
    })\n
\n
    /////////////////////////////////////////////////////////////////\n
    // Acquired methods\n
    /////////////////////////////////////////////////////////////////\n
    .declareAcquiredMethod("updateHeader", "updateHeader")\n
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")\n
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")\n
    .declareAcquiredMethod("jio_put", "jio_put")\n
    .declareAcquiredMethod("jio_get", "jio_get")\n
    .declareAcquiredMethod("redirect", "redirect")\n
\n
    /////////////////////////////////////////////////////////////////\n
    // declared methods\n
    /////////////////////////////////////////////////////////////////\n
    .declareMethod(\'triggerSubmit\', function () {\n
      this.props.element.querySelector(\'button\').click();\n
    })\n
    .declareMethod("render", function () {\n
      var page_gadget = this,\n
        data;\n
      return page_gadget.updateHeader({\n
        page_title: \'Connect to a Jabber server\',\n
        submit_action: true\n
      })\n
        .push(function () {\n
          return page_gadget.jio_get("CONNECTION");\n
        })\n
        .push(function (result) {\n
          data = result;\n
          return page_gadget.getDeclaredGadget("erp5_form");\n
        })\n
        .push(function (form_gadget) {\n
          return form_gadget.render({\n
            erp5_document: {"_embedded": {"_view": {\n
              "server": {\n
                "description": "",\n
                "title": "Server URL",\n
                "default": data.server,\n
                "css_class": "",\n
                "required": 1,\n
                "editable": 1,\n
                "key": "server",\n
                "hidden": 0,\n
                "type": "StringField"\n
              },\n
              "jid": {\n
                "description": "",\n
                "title": "Jabber ID",\n
                "default": data.jid,\n
                "css_class": "",\n
                "required": 1,\n
                "editable": 1,\n
                "key": "jid",\n
                "hidden": 0,\n
                "type": "StringField"\n
              },\n
              "passwd": {\n
                "description": "",\n
                "title": "Password",\n
                "default": data.passwd,\n
                "css_class": "",\n
                "required": 1,\n
                "editable": 1,\n
                "key": "passwd",\n
                "hidden": 0,\n
                "type": "PasswordField"\n
              }\n
            }}},\n
            form_definition: {\n
              group_list: [[\n
                "center",\n
                [["server"], ["jid"], ["passwd"]]\n
              ]]\n
            }\n
          });\n
        });\n
    })\n
\n
    .declareService(function () {\n
      var form_gadget = this;\n
\n
      function formSubmit() {\n
        return form_gadget.notifySubmitting()\n
          .push(function () {\n
            return form_gadget.getDeclaredGadget("erp5_form");\n
          })\n
          .push(function (erp5_form) {\n
            return erp5_form.getContent();\n
          })\n
          .push(function (content_dict) {\n
            return form_gadget.jio_put(\n
              \'CONNECTION\',\n
              content_dict\n
            );\n
          })\n
          .push(function () {\n
            return RSVP.all([\n
              form_gadget.notifySubmitted(),\n
              form_gadget.redirect({command: \'display\', options: {page: \'contact\'}})\n
            ]);\n
          })\n
          .push(undefined, function (error) {\n
            return form_gadget.notifySubmitted()\n
              .push(function () {\n
                form_gadget.props.element.querySelector(\'pre\').textContent = error;\n
              });\n
          });\n
      }\n
\n
      // Listen to form submit\n
      return loopEventListener(\n
        form_gadget.props.element.querySelector(\'form\'),\n
        \'submit\',\n
        false,\n
        formSubmit\n
      );\n
    });\n
\n
}(window, rJS, RSVP, loopEventListener));</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>JabberClient Gadget Page Connect JS</string> </value>
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
                        <float>1456389329.61</float>
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
                <value> <string>949.35328.64444.1843</string> </value>
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
                        <float>1456843227.61</float>
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
                        <float>1456389199.52</float>
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
