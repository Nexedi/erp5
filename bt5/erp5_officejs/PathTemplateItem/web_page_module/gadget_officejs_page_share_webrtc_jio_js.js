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
              <tuple/>
            </value>
        </item>
        <item>
            <key> <string>content_md5</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>contributors</string> </key>
            <value>
              <tuple/>
            </value>
        </item>
        <item>
            <key> <string>default_reference</string> </key>
            <value> <string>gadget_officejs_page_share_webrtc_jio.js</string> </value>
        </item>
        <item>
            <key> <string>description</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>gadget_officejs_page_share_webrtc_jio_js</string> </value>
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

/*global window, rJS, document, RSVP, console, DOMException */\n
/*jslint indent: 2, maxerr: 3 */\n
(function (window, rJS, document, RSVP, console, DOMException) {\n
  "use strict";\n
\n
  function dropSubGadget(gadget, scope) {\n
    return gadget.getDeclaredGadget(scope)\n
      .push(function (result) {\n
        return result.getElement();\n
      })\n
      .push(function (element) {\n
        if (element.parentElement) {\n
          element.parentElement.removeChild(element);\n
        }\n
        delete gadget.state_parameter_dict.scope_ip[scope];\n
        return gadget.dropGadget(scope);\n
      });\n
  }\n
\n
  function getWebRTCScopeList(gadget) {\n
    var result_list = [],\n
      element_list = gadget.state_parameter_dict.element.querySelector(".gadget_webrtc_datachannel")\n
                                                        .childNodes,\n
      i;\n
    for (i = 0; i < element_list.length; i += 1) {\n
      result_list.push(element_list[i].getAttribute("data-gadget-scope"));\n
    }\n
    return result_list;\n
  }\n
\n
  function updateInfo(gadget) {\n
    var scope_list = getWebRTCScopeList(gadget),\n
      i,\n
      result = "";\n
    for (i = 0; i < scope_list.length; i += 1) {\n
      result += gadget.state_parameter_dict.scope_ip[scope_list[i]] + "\\n";\n
    }\n
    gadget.state_parameter_dict.element.querySelector(".info").textContent = result;\n
    gadget.state_parameter_dict.element.querySelector(".peer_count").textContent = i;\n
  }\n
\n
  function sendWebRTC(gadget, rtc_gadget, scope, message) {\n
    return rtc_gadget.send(message)\n
      .push(undefined, function (error) {\n
        if ((error instanceof DOMException) && (error.name === \'InvalidStateError\')) {\n
          return dropSubGadget(gadget, scope)\n
            .push(function () {\n
              return updateInfo(gadget);\n
            }, function (error) {\n
              console.log("-- Can not drop remote subgadget " + scope);\n
              console.log(error);\n
              return;\n
            });\n
        }\n
        throw error;\n
      });\n
  }\n
\n
  rJS(window)\n
\n
    .ready(function (gadget) {\n
      // Initialize the gadget local parameters\n
      gadget.state_parameter_dict = {\n
        websocket_initialized: false,\n
        counter: 0,\n
        connecting: false,\n
        scope_ip: {}\n
      };\n
      return gadget.getElement()\n
        .push(function (element) {\n
          gadget.state_parameter_dict.element = element;\n
        })\n
        .push(function () {\n
          return updateInfo(gadget);\n
        });\n
    })\n
\n
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")\n
    .declareAcquiredMethod("jio_post", "jio_post")\n
    .declareAcquiredMethod("jio_put", "jio_put")\n
    .declareAcquiredMethod("jio_get", "jio_get")\n
    .declareAcquiredMethod("jio_repair", "jio_repair")\n
\n
    .allowPublicAcquisition(\'notifyDataChannelClosed\', function (argument_list, scope) {\n
      /*jslint unparam:true*/\n
      var gadget = this;\n
      return dropSubGadget(this, scope)\n
        .push(function () {\n
          return updateInfo(gadget);\n
        });\n
    })\n
\n
    .allowPublicAcquisition("notifyDataChannelMessage", function (argument_list, scope) {\n
      var json = JSON.parse(argument_list[0]),\n
        rtc_gadget,\n
        context = this;\n
      return context.getDeclaredGadget(scope)\n
        .push(function (g) {\n
          rtc_gadget = g;\n
          // Call jio API\n
          return context["jio_" + json.method_name].apply(context, json.argument_list);\n
        })\n
        .push(function (result) {\n
          return sendWebRTC(context, rtc_gadget, scope, JSON.stringify({\n
            id: json.id,\n
            result: result,\n
            type: "jio_response"\n
          }));\n
        }, function (error) {\n
          return sendWebRTC(context, rtc_gadget, scope, JSON.stringify({\n
            id: json.id,\n
            result: error,\n
            type: "error"\n
          }));\n
        });\n
    })\n
/*\n
    .allowPublicAcquisition("notifyWebSocketClosed", function () {\n
      if (this.state_parameter_dict.user_type !== "user") {\n
        throw new Error("Unexpected Web Socket connection close");\n
      }\n
    })\n
*/\n
    .allowPublicAcquisition("notifyWebSocketMessage", function (argument_list) {\n
      var json = JSON.parse(argument_list[0]),\n
        scope,\n
        rtc_gadget,\n
        socket_gadget,\n
        gadget = this;\n
\n
      if (json.action === "offer") {\n
        // XXX https://github.com/diafygi/webrtc-ips\n
        return gadget.getDeclaredGadget("gadget_websocket.html")\n
          .push(function (gg) {\n
            gadget.state_parameter_dict.connecting = true;\n
            gadget.state_parameter_dict.counter += 1;\n
            socket_gadget = gg;\n
            var new_element = document.createElement("div");\n
            gadget.state_parameter_dict.element.querySelector(".gadget_webrtc_datachannel").appendChild(new_element);\n
            scope = "webrtc" + gadget.state_parameter_dict.counter;\n
            return gadget.declareGadget("gadget_webrtc_datachannel.html", {\n
              scope: scope,\n
              element: new_element\n
            });\n
          })\n
          .push(function (gg) {\n
            rtc_gadget = gg;\n
            // https://github.com/diafygi/webrtc-ips\n
            var ip_regex = /([0-9]{1,3}(\\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/,\n
              ip_list = [],\n
              ip_dict = {},\n
              ip_addr,\n
              line_list = JSON.parse(json.data).sdp.split(\'\\n\'),\n
              i;\n
            for (i = 0; i < line_list.length; i += 1) {\n
              if (line_list[i].indexOf(\'a=candidate:\') === 0) {\n
                ip_addr = ip_regex.exec(line_list[i])[1];\n
                if (!ip_addr.match(/^[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7}$/)) {\n
                  // Hide ipv6\n
                  if (!ip_dict[ip_addr]) {\n
                    ip_list.push(ip_addr);\n
                    ip_dict[ip_addr] = true;\n
                  }\n
                }\n
              }\n
            }\n
            gadget.state_parameter_dict.scope_ip[scope] = ip_list;\n
            return rtc_gadget.createAnswer(json.from, json.data);\n
          })\n
          .push(function (local_connection) {\n
            return socket_gadget.send(JSON.stringify({to: json.from, action: "answer", data: local_connection}));\n
          })\n
          .push(function () {\n
            return RSVP.any([\n
              RSVP.Queue()\n
                .push(function () {\n
                  return RSVP.delay(10000);\n
                })\n
                .push(function () {\n
                  console.info(\'-- webrtc client disappears...\');\n
                  return dropSubGadget(gadget, scope);\n
                }),\n
              rtc_gadget.waitForConnection()\n
            ]);\n
          })\n
          .push(function () {\n
            gadget.state_parameter_dict.connecting = false;\n
            return updateInfo(gadget);\n
          });\n
      }\n
    })\n
\n
    .declareService(function () {\n
      var sgadget,\n
        gadget = this;\n
      return this.getDeclaredGadget(\'gadget_websocket.html\')\n
        .push(function (socket_gadget) {\n
          sgadget = socket_gadget;\n
          return socket_gadget.createSocket("ws://127.0.0.1:9999/");\n
        })\n
        .push(function () {\n
          // Wait for the gadget to be dropped from the page\n
          // and close the socket/rtc connections\n
          return RSVP.defer().promise;\n
        })\n
        .push(undefined, function (error) {\n
          if (sgadget === undefined) {\n
            return;\n
          }\n
          return sgadget.close()\n
            .push(function () {\n
              var scope_list = getWebRTCScopeList(gadget),\n
                i,\n
                promise_list = [];\n
\n
              function close(scope) {\n
                return gadget.getDeclaredGadget(scope)\n
                  .push(function (rtc_gadget) {\n
                    return rtc_gadget.close();\n
                  });\n
              }\n
\n
              for (i = 0; i < scope_list.length; i += 1) {\n
                promise_list.push(close(scope_list[i]));\n
              }\n
              return RSVP.all(promise_list);\n
            })\n
            .push(function () {\n
              throw error;\n
            });\n
        });\n
    });\n
\n
}(window, rJS, document, RSVP, console, DOMException));

]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>OfficeJS Share jIO Page JS</string> </value>
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
                        <float>1441026776.09</float>
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
                <value> <string>945.33680.49983.21452</string> </value>
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
                        <float>1441358513.14</float>
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
                        <float>1440770697.62</float>
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
