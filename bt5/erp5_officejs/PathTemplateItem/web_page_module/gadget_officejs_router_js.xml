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
            <value> <string>gadget_officejs_router.js</string> </value>
        </item>
        <item>
            <key> <string>description</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>gadget_officejs_router_js</string> </value>
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

/*global window, rJS */\n
/*jslint nomen: true, indent: 2, maxerr: 3*/\n
(function (window, rJS) {\n
  "use strict";\n
\n
  var gadget_klass = rJS(window),\n
    MAIN_PAGE_PREFIX = "gadget_officejs_",\n
    DEFAULT_PAGE = "text_editor_list",\n
    REDIRECT_TIMEOUT = 5000;\n
\n
  function listenHashChange(gadget) {\n
    function extractHashAndDispatch(evt) {\n
      var hash = (evt.newURL || window.location.toString()).split(\'#\')[1],\n
        subhashes,\n
        subhash,\n
        keyvalue,\n
        index,\n
        args = {};\n
      if (hash !== undefined) {\n
        subhashes = hash.split(\'&\');\n
        for (index in subhashes) {\n
          if (subhashes.hasOwnProperty(index)) {\n
            subhash = subhashes[index];\n
            if (subhash !== \'\') {\n
              keyvalue = subhash.split(\'=\');\n
              if (keyvalue.length === 2) {\n
                args[decodeURIComponent(keyvalue[0])] = decodeURIComponent(keyvalue[1]);\n
              }\n
            }\n
          }\n
        }\n
      }\n
\n
      return gadget.renderApplication({\n
        args: args\n
      });\n
\n
    }\n
\n
    var result = loopEventListener(window, \'hashchange\', false,\n
                                   extractHashAndDispatch),\n
      event = document.createEvent("Event");\n
    event.initEvent(\'hashchange\', true, true);\n
    event.newURL = window.location.toString();\n
    window.dispatchEvent(event);\n
    return result;\n
  }\n
\n
  gadget_klass\n
\n
    .ready(function (gadget) {\n
      gadget.props = {\n
        start_deferred: RSVP.defer()\n
      };\n
    })\n
\n
    .declareMethod("getCommandUrlFor", function(options) {\n
      var prefix = \'\',\n
        result,\n
        key;\n
      result = "#";\n
      for (key in options) {\n
        if (options.hasOwnProperty(key) && options[key] !== undefined) {\n
          // Don\'t keep empty values\n
          result += prefix + encodeURIComponent(key) + "=" + encodeURIComponent(options[key]);\n
          prefix = \'&\';\n
        }\n
      }\n
      return result;\n
    })\n
\n
    .declareMethod(\'redirect\', function (options) {\n
      if (options !== undefined && options.toExternal) {\n
        window.location.replace(options.url);\n
        return RSVP.timeout(REDIRECT_TIMEOUT); // timeout if not redirected\n
      }\n
      else {\n
        return this.getCommandUrlFor(options)\n
          .push(function (hash) {\n
            window.location.replace(hash);\n
            // prevent returning unexpected response\n
            // wait for the hash change to occur\n
            // fail if nothing happens\n
            return RSVP.timeout(REDIRECT_TIMEOUT);\n
          });\n
      }\n
    })\n
\n
    .declareMethod(\'route\', function (options) {\n
      var gadget = this,\n
        args = options.args;\n
      gadget.options = options;\n
      if (args.jio_key === undefined || args.jio_key === \'\') {\n
        if (args.page === undefined || args.page === \'\' || args.page === "document_list") {\n
          args.page = DEFAULT_PAGE;\n
        }\n
        return {\n
          url: MAIN_PAGE_PREFIX + "page_" + args.page + ".html",\n
          options: args\n
        };\n
      }\n
      return gadget.jio_get(args.jio_key)\n
        .push(function (doc) {\n
          var sub_options = {},\n
            base_portal_type = doc.portal_type.toLowerCase().replace(/\\s/g, "_");\n
          sub_options = {\n
            doc: doc,\n
            jio_key: args.jio_key,\n
            search: args.search\n
          };\n
          if (base_portal_type.search(/_temp$/) >= 0) {\n
            //Remove "_temp"\n
            base_portal_type = base_portal_type.substr(\n
              0,\n
              base_portal_type.length - 5\n
            );\n
          }\n
          return {\n
            url: MAIN_PAGE_PREFIX + "jio_"\n
              + base_portal_type\n
              + "_" + args.page + ".html",\n
            options: sub_options\n
          };\n
        });\n
    })\n
    \n
    .declareAcquiredMethod(\'jio_get\', \'jio_get\')\n
    .declareAcquiredMethod(\'renderApplication\', \'renderApplication\')\n
    .declareMethod(\'start\', function () {\n
      this.props.start_deferred.resolve();\n
    })\n
    .declareService(function () {\n
      var gadget = this;\n
      return new RSVP.Queue()\n
        .push(function () {\n
          return gadget.props.start_deferred.promise;\n
        })\n
        .push(function () {\n
          return listenHashChange(gadget);\n
        });\n
    });\n
\n
}(window, rJS));

]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>OfficeJS router Gadget JS</string> </value>
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
                <value> <string>cedric.le.ninivin</string> </value>
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
                        <float>1441648217.21</float>
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
                <value> <string>947.54085.31754.65399</string> </value>
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
                        <float>1450274255.9</float>
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
                <value> <string>cedric.le.ninivin</string> </value>
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
                        <float>1441648101.99</float>
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
