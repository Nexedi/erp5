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
            <value> <string>gadget_officejs_webrtc_jio.js</string> </value>
        </item>
        <item>
            <key> <string>description</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>gadget_officejs_webrtc_jio_js</string> </value>
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
            <value> <string>/*global window, rJS, document, RSVP */\n
/*jslint indent: 2, maxerr: 3 */\n
(function (window, rJS, document, RSVP) {\n
  "use strict";\n
\n
  var timeout = 60000,\n
    websocket_timeout = 5000;\n
\n
  function S4() {\n
    return (\'0000\' + Math.floor(\n
      Math.random() * 0x10000 /* 65536 */\n
    ).toString(16)).slice(-4);\n
  }\n
\n
  function UUID() {\n
    return S4() + S4() + "-" +\n
      S4() + "-" +\n
      S4() + "-" +\n
      S4() + "-" +\n
      S4() + S4() + S4();\n
  }\n
\n
  function wrapJioAccess(gadget, method_name, argument_list) {\n
    if (!gadget.state_parameter_dict.jio_created) {\n
      return gadget.redirect({page: \'setting\'});\n
    }\n
    return gadget.getDeclaredGadget(\'gadget_webrtc_datachannel.html\')\n
      .push(function (rtc_gadget) {\n
        gadget.state_parameter_dict.message_count += 1;\n
        gadget.state_parameter_dict.message_dict[gadget.state_parameter_dict.message_count] = RSVP.defer();\n
        return RSVP.all([\n
          rtc_gadget.send(JSON.stringify({\n
            id: gadget.state_parameter_dict.message_count,\n
            type: "jio_query",\n
            method_name: method_name,\n
            argument_list: Array.prototype.slice.call(argument_list)\n
          })),\n
          RSVP.any([\n
            RSVP.timeout(timeout),\n
            gadget.state_parameter_dict.message_dict[gadget.state_parameter_dict.message_count].promise\n
          ])\n
        ]);\n
      })\n
      .push(function (result_list) {\n
        return result_list[1];\n
      });\n
\n
  }\n
\n
  function declareSubGadget(gadget, url) {\n
    var container_element = gadget.state_parameter_dict.element.querySelector("." + url.split(".")[0]),\n
      element = document.createElement("div");\n
    container_element.innerHTML = "";\n
    container_element.appendChild(element);\n
    return gadget.declareGadget(url, {\n
      element: element,\n
      scope: url,\n
      sandbox: "public"\n
    });\n
  }\n
\n
  rJS(window)\n
\n
    .ready(function (gadget) {\n
      // Initialize the gadget local parameters\n
      gadget.state_parameter_dict = {\n
        jio_created: false\n
      };\n
      return gadget.getElement()\n
        .push(function (element) {\n
          gadget.state_parameter_dict.element = element;\n
        });\n
    })\n
\n
    .allowPublicAcquisition("notifyDataChannelMessage", function (argument_list) {\n
      var json = JSON.parse(argument_list[0]),\n
        context = this;\n
      if (json.type === "jio_response") {\n
        context.state_parameter_dict.message_dict[json.id].resolve(json.result);\n
      } else if (json.type === "error") {\n
        context.state_parameter_dict.message_dict[json.id].reject(json.result);\n
      }\n
      // Drop all other kind of messages\n
    })\n
\n
    .allowPublicAcquisition("notifyWebSocketMessage", function (argument_list) {\n
\n
      var json = JSON.parse(argument_list[0]),\n
        gadget = this;\n
\n
      if (json.action === "answer") {\n
        if (json.to === gadget.state_parameter_dict.uuid) {\n
          gadget.state_parameter_dict.answer_defer.resolve(json.data);\n
        }\n
      }\n
\n
    })\n
\n
    .allowPublicAcquisition("notifyWebSocketClosed", function () {\n
      // WebSocket get closed as soon as webrtc connection is created\n
      return;\n
    })\n
\n
    .declareAcquiredMethod(\'redirect\', \'redirect\')\n
\n
    .declareMethod(\'createJio\', function (options) {\n
      var context = this,\n
        socket_gadget,\n
        rtc_gadget;\n
\n
      if ((options === undefined) || (options.socket_url === undefined)) {\n
        return context.redirect({page: \'setting\'});\n
      }\n
      context.state_parameter_dict.jio_created = true;\n
      return declareSubGadget(context, \'gadget_websocket.html\')\n
        .push(function (gadget) {\n
          socket_gadget = gadget;\n
\n
          context.state_parameter_dict.uuid = UUID();\n
          context.state_parameter_dict.answer_defer = RSVP.defer();\n
          context.state_parameter_dict.message_count = 0;\n
          context.state_parameter_dict.message_dict = {};\n
          // Send offer and expect answer in less than XXXms (arbitrary value...)\n
          return RSVP.any([\n
            RSVP.Queue()\n
              .push(function () {\n
                return RSVP.timeout(websocket_timeout);\n
              })\n
              .push(undefined, function () {\n
                return context.redirect({page: \'setting\'});\n
                // throw new Error("No remote WebRTC connection available");\n
              }),\n
            declareSubGadget(context, \'gadget_websocket.html\')\n
              .push(function (gadget) {\n
                socket_gadget = gadget;\n
                // XXX Drop hardcoded URL\n
                return socket_gadget.createSocket(options.socket_url);\n
              })\n
              .push(function () {\n
                return declareSubGadget(context, \'gadget_webrtc_datachannel.html\');\n
              })\n
              .push(function (gadget) {\n
                rtc_gadget = gadget;\n
                return rtc_gadget.createOffer(context.state_parameter_dict.uuid);\n
              })\n
              .push(function (description) {\n
                return RSVP.all([\n
                  socket_gadget.send(JSON.stringify({from: context.state_parameter_dict.uuid, action: "offer", data: description})),\n
                  context.state_parameter_dict.answer_defer.promise\n
                ]);\n
              })\n
              .push(function (response_list) {\n
                return rtc_gadget.registerAnswer(response_list[1]);\n
              })\n
              .push(function () {\n
                return socket_gadget.close();\n
              })\n
            ]);\n
        });\n
    })\n
    .declareMethod(\'allDocs\', function () {\n
      return wrapJioAccess(this, \'allDocs\', arguments);\n
    })\n
    .declareMethod(\'get\', function () {\n
      return wrapJioAccess(this, \'get\', arguments);\n
    })\n
    .declareMethod(\'put\', function () {\n
      return wrapJioAccess(this, \'put\', arguments);\n
    })\n
    .declareMethod(\'post\', function () {\n
      return wrapJioAccess(this, \'post\', arguments);\n
    })\n
    .declareMethod(\'remove\', function () {\n
      return wrapJioAccess(this, \'remove\', arguments);\n
    });\n
\n
}(window, rJS, document, RSVP));</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>OfficeJS WebRTC Jio Gadget JS</string> </value>
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
                <value> <string>romain</string> </value>
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
                        <float>1440000628.95</float>
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
                <value> <string>romain</string> </value>
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
                <value> <string>945.39449.60302.38024</string> </value>
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
                        <float>1441715721.23</float>
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
                <value> <string>romain</string> </value>
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
                        <float>1439999508.1</float>
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
