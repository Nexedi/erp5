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
            <value> <string>gadget_websocket.js</string> </value>
        </item>
        <item>
            <key> <string>description</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>rjs_gadget_websocket_js</string> </value>
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

/*jslint indent: 2*/\n
/*global rJS, window, WebSocket, RSVP*/\n
(function (rJS, window, WebSocket, RSVP) {\n
  "use strict";\n
\n
  function enqueueDefer(gadget, callback) {\n
    var deferred = gadget.props.current_deferred;\n
\n
    // Unblock queue\n
    if (deferred !== undefined) {\n
      deferred.resolve("Another event added");\n
    }\n
\n
    // Add next callback\n
    try {\n
      gadget.props.service_queue.push(callback);\n
    } catch (error) {\n
      throw new Error("Connection gadget already crashed... " +\n
                      gadget.props.service_queue.rejectedReason.toString());\n
    }\n
\n
    // Block the queue\n
    deferred = RSVP.defer();\n
    gadget.props.current_deferred = deferred;\n
    gadget.props.service_queue.push(function () {\n
      return deferred.promise;\n
    });\n
\n
  }\n
\n
  function deferOnClose() {\n
    var gadget = this;\n
    enqueueDefer(gadget, function () {\n
      return gadget.notifyWebSocketClosed();\n
    });\n
  }\n
\n
  function deferOnOpen() {\n
    var gadget = this;\n
    enqueueDefer(gadget, function () {\n
      gadget.props.socket_defer.resolve();\n
//       return gadget.notifyWebSocketOpened();\n
    });\n
  }\n
\n
  function deferOnMessage(evt) {\n
    var gadget = this;\n
    enqueueDefer(gadget, function () {\n
      return gadget.notifyWebSocketMessage(evt.data);\n
    });\n
  }\n
\n
  function deferServerDisconnection(gadget) {\n
    enqueueDefer(gadget, function () {\n
      // Try to auto connection\n
      if (gadget.props.connection !== undefined) {\n
        gadget.props.connection.disconnect();\n
        delete gadget.props.connection;\n
      }\n
    });\n
  }\n
\n
  function deferErrorHandler(error) {\n
    if ((!this.props.socket_defer.isFulfilled) && (!this.props.socket_defer.isRejected)) {\n
      this.props.socket_defer.reject(error);\n
    } else {\n
      enqueueDefer(this, function () {\n
        throw error;\n
      });\n
    }\n
  }\n
\n
  function deferServerConnection(gadget) {\n
    deferServerDisconnection(gadget);\n
\n
  }\n
\n
\n
  rJS(window)\n
    .ready(function (g) {\n
      g.props = {};\n
    })\n
\n
    .declareAcquiredMethod(\'notifyWebSocketClosed\',\n
                           \'notifyWebSocketClosed\')\n
    .declareAcquiredMethod(\'notifyWebSocketMessage\',\n
                           \'notifyWebSocketMessage\')\n
\n
    .declareService(function () {\n
      /////////////////////////\n
      // Handle WebSocket connection\n
      /////////////////////////\n
      var context = this;\n
\n
      context.props.service_queue = new RSVP.Queue();\n
      deferServerConnection(context);\n
\n
      return new RSVP.Queue()\n
        .push(function () {\n
          return context.props.service_queue;\n
        })\n
        .push(function () {\n
          // XXX Handle cancellation\n
          throw new Error("Service should not have been stopped!");\n
        })\n
        .push(undefined, function (error) {\n
          // Always disconnect in case of error\n
          if (context.props.connection !== undefined) {\n
            context.props.connection.close();\n
          }\n
          throw error;\n
        });\n
    })\n
\n
    .declareMethod(\'createSocket\', function (address) {\n
      // Improve to support multiple sockets?\n
      this.props.socket = new WebSocket(address);\n
      this.props.socket_defer = RSVP.defer();\n
      this.props.socket.addEventListener(\'open\', deferOnOpen.bind(this));\n
      this.props.socket.addEventListener(\'close\', deferOnClose.bind(this));\n
      this.props.socket.addEventListener(\'message\', deferOnMessage.bind(this));\n
      this.props.socket.addEventListener(\'error\', deferErrorHandler.bind(this));\n
      return this.props.socket_defer.promise;\n
    })\n
\n
    .declareMethod(\'send\', function (message) {\n
      this.props.socket.send(message);\n
    })\n
\n
    .declareMethod(\'close\', function () {\n
      if (this.props.socket === undefined) {\n
        return;\n
      }\n
      this.props.socket.close();\n
      delete this.props.socket;\n
    });\n
\n
}(rJS, window, WebSocket, RSVP));\n


]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>WebSocket Gadget JS</string> </value>
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
                        <float>1439903737.59</float>
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
                <value> <string>945.33605.10741.21811</string> </value>
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
                        <float>1441353954.68</float>
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
                        <float>1439903510.97</float>
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
