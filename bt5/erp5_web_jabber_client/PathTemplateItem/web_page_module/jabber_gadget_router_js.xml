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
            <key> <string>default_reference</string> </key>
            <value> <string>gadget_jabberclient_router.js</string> </value>
        </item>
        <item>
            <key> <string>description</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>jabber_gadget_router_js</string> </value>
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

/*global window, rJS, RSVP, loopEventListener, document, URL */\n
/*jslint nomen: true, indent: 2 */\n
(function (window, rJS, RSVP, loopEventListener, document, URL) {\n
  "use strict";\n
\n
  // Keep reference of the latest allDocs params which reach to this view\n
  // var SELECTION_KEY = "s",\n
  // Keep reference in the global navigation pattern\n
  // HISTORY KEY = "h"\n
  // Current display parameter\n
  // DISPLAY KEY = "d"\n
  var PREVIOUS_KEY = "p",\n
    NEXT_KEY = "n",\n
    DROP_KEY = "u",\n
    PREFIX_DISPLAY = "/",\n
    PREFIX_COMMAND = "!",\n
    // PREFIX_ERROR = "?",\n
    COMMAND_DISPLAY_STATE = "display",\n
    COMMAND_LOGIN = "login",\n
    COMMAND_RAW = "raw",\n
    COMMAND_RELOAD = "reload",\n
    COMMAND_DISPLAY_STORED_STATE = "display_stored_state",\n
    COMMAND_CHANGE_STATE = "change",\n
    COMMAND_STORE_AND_CHANGE_STATE = "store_and_change",\n
    COMMAND_INDEX_STATE = "index",\n
    COMMAND_SELECTION_PREVIOUS = "selection_previous",\n
    COMMAND_SELECTION_NEXT = "selection_next",\n
    COMMAND_HISTORY_PREVIOUS = "history_previous",\n
    COMMAND_PUSH_HISTORY = "push_history",\n
    REDIRECT_TIMEOUT = 5000,\n
    VALID_URL_COMMAND_DICT = {};\n
  VALID_URL_COMMAND_DICT[COMMAND_DISPLAY_STATE] = null;\n
  VALID_URL_COMMAND_DICT[COMMAND_DISPLAY_STORED_STATE] = null;\n
  VALID_URL_COMMAND_DICT[COMMAND_CHANGE_STATE] = null;\n
  VALID_URL_COMMAND_DICT[COMMAND_STORE_AND_CHANGE_STATE] = null;\n
  VALID_URL_COMMAND_DICT[COMMAND_INDEX_STATE] = null;\n
  VALID_URL_COMMAND_DICT[COMMAND_SELECTION_PREVIOUS] = null;\n
  VALID_URL_COMMAND_DICT[COMMAND_SELECTION_NEXT] = null;\n
  VALID_URL_COMMAND_DICT[COMMAND_HISTORY_PREVIOUS] = null;\n
  VALID_URL_COMMAND_DICT[COMMAND_PUSH_HISTORY] = null;\n
  VALID_URL_COMMAND_DICT[COMMAND_LOGIN] = null;\n
  VALID_URL_COMMAND_DICT[COMMAND_RAW] = null;\n
  VALID_URL_COMMAND_DICT[COMMAND_RELOAD] = null;\n
\n
\n
  function endsWith(str, suffix) {\n
    return str.indexOf(suffix, str.length - suffix.length) !== -1;\n
  }\n
\n
  //////////////////////////////////////////////////////////////////\n
  // Change URL functions\n
  //////////////////////////////////////////////////////////////////\n
  function changeState(hash) {\n
    // window.location = hash;\n
    return window.location.replace(hash);\n
  }\n
\n
  function synchronousChangeState(hash) {\n
    changeState(hash);\n
    // prevent returning unexpected response\n
    // wait for the hash change to occur\n
    // fail if nothing happens\n
    return RSVP.timeout(REDIRECT_TIMEOUT);\n
  }\n
\n
  //////////////////////////////////////////////////////////////////\n
  // Build URL functions\n
  //////////////////////////////////////////////////////////////////\n
  function getCommandUrlFor(gadget, command, options) {\n
    if (command === COMMAND_RAW) {\n
      return options.url;\n
    }\n
    var result = "#" + PREFIX_COMMAND + (command || ""),\n
      prefix = "?",\n
      key,\n
      tmp,\n
      tmp_dict;\n
    tmp_dict = gadget.props.options;\n
    for (key in tmp_dict) {\n
      if (tmp_dict.hasOwnProperty(key) && (tmp_dict[key] !== undefined)) {\n
        tmp = tmp_dict[key];\n
        if (endsWith(key, ":json")) {\n
          tmp = JSON.stringify(tmp);\n
        }\n
        result += prefix + PREVIOUS_KEY + "." + encodeURIComponent(key) + "=" + encodeURIComponent(tmp);\n
        prefix = "&";\n
      }\n
    }\n
    for (key in options) {\n
      if (options.hasOwnProperty(key)) {\n
        tmp = options[key];\n
        if (tmp === undefined) {\n
          // Key should be dropped from the URL\n
          result += prefix + DROP_KEY + "." + encodeURIComponent(key) + "=";\n
        } else {\n
          if (endsWith(key, ":json")) {\n
            tmp = JSON.stringify(tmp);\n
          }\n
          result += prefix + NEXT_KEY + "." + encodeURIComponent(key) + "=" + encodeURIComponent(tmp);\n
        }\n
        prefix = "&";\n
      }\n
    }\n
    if (command === COMMAND_LOGIN) {\n
      // Build URL template to allow getting user information\n
      result += \'{\' + prefix + \'n.me}\';\n
    }\n
    return result;\n
  }\n
\n
  function getDisplayUrlFor(jio_key, options) {\n
    var prefix = \'?\',\n
      result,\n
      tmp,\n
      key;\n
    result = "#" + PREFIX_DISPLAY + (jio_key || "");\n
    for (key in options) {\n
      if (options.hasOwnProperty(key) && options[key] !== undefined) {\n
        // Don\'t keep empty values\n
        tmp = options[key];\n
        if (endsWith(key, ":json")) {\n
          tmp = JSON.stringify(tmp);\n
        }\n
        result += prefix + encodeURIComponent(key) + "=" + encodeURIComponent(tmp);\n
        prefix = \'&\';\n
      }\n
    }\n
    return result;\n
  }\n
\n
  //////////////////////////////////////////////////////////////////\n
  // exec command functions\n
  //////////////////////////////////////////////////////////////////\n
  function execDisplayCommand(next_options) {\n
    // console.warn(command_options);\n
    var jio_key = next_options.jio_key,\n
      hash;\n
    delete next_options.jio_key;\n
\n
    hash = getDisplayUrlFor(jio_key, next_options);\n
    return new RSVP.Queue()\n
      .push(function () {\n
        return synchronousChangeState(hash);\n
      });\n
  }\n
\n
  //////////////////////////////////////////////////////////////////\n
  // Command URL functions\n
  //////////////////////////////////////////////////////////////////\n
  function routeMethodLess() {\n
    // Nothing. Go to front page\n
    return synchronousChangeState(\n
      getDisplayUrlFor(undefined, {page: \'contact\'})\n
    );\n
  }\n
\n
  function routeDisplay(command_options) {\n
    if (command_options.args.page === undefined) {\n
      return routeMethodLess();\n
    }\n
\n
    return {\n
      url: "gadget_jabberclient_page_" + command_options.args.page + ".html",\n
      options: command_options.args\n
    };\n
\n
  }\n
\n
  function routeCommand(command_options) {\n
    var args = command_options.args,\n
      key,\n
      split_list,\n
      previous_options = {},\n
      next_options = {},\n
      drop_options = {},\n
      valid = true;\n
    // Rebuild the previous and next parameter dict\n
    for (key in args) {\n
      if (args.hasOwnProperty(key)) {\n
        split_list = key.split(\'.\', 2);\n
        if (split_list.length !== 2) {\n
          valid = false;\n
          break;\n
        }\n
        if (split_list[0] === PREVIOUS_KEY) {\n
          previous_options[split_list[1]] = args[key];\n
        } else if (split_list[0] === NEXT_KEY) {\n
          next_options[split_list[1]] = args[key];\n
        } else if (split_list[0] === DROP_KEY) {\n
          drop_options[split_list[1]] = args[key];\n
        } else {\n
          valid = false;\n
          break;\n
        }\n
      }\n
    }\n
    if (!valid) {\n
      throw new Error(\'Unsupported parameters: \' + key);\n
    }\n
\n
    if (command_options.path === COMMAND_DISPLAY_STATE) {\n
      return execDisplayCommand(next_options);\n
    }\n
    throw new Error(\'Unsupported command \' + command_options.path);\n
\n
  }\n
\n
  function listenHashChange(gadget) {\n
    // Handle hash in this format: #$path1/path2?a=b&c=d\n
    function extractHashAndDispatch(evt) {\n
      var hash = (evt.newURL || window.location.toString()).split(\'#\')[1],\n
        split,\n
        command = "",\n
        query = "",\n
        subhashes,\n
        subhash,\n
        keyvalue,\n
        index,\n
        key,\n
        tmp,\n
        args = {};\n
      if (hash !== undefined) {\n
        split = hash.split(\'?\');\n
        command = split[0] || "";\n
        query = split[1] || "";\n
      }\n
      subhashes = query.split(\'&\');\n
      for (index in subhashes) {\n
        if (subhashes.hasOwnProperty(index)) {\n
          subhash = subhashes[index];\n
          if (subhash !== \'\') {\n
            keyvalue = subhash.split(\'=\');\n
            if (keyvalue.length === 2) {\n
              key = decodeURIComponent(keyvalue[0]);\n
              tmp = decodeURIComponent(keyvalue[1]);\n
              if (endsWith(key, ":json")) {\n
                tmp = JSON.parse(tmp);\n
              }\n
              args[key] = tmp;\n
            }\n
          }\n
        }\n
      }\n
\n
      return gadget.renderApplication({\n
        method: command[0],\n
        path: command.substr(1),\n
        args: args\n
      });\n
\n
    }\n
    var result = loopEventListener(window, \'hashchange\', false,\n
                                   extractHashAndDispatch),\n
      event = document.createEvent("Event");\n
    event.initEvent(\'hashchange\', true, true);\n
    event.newURL = window.location.toString();\n
    window.dispatchEvent(event);\n
    return result;\n
  }\n
\n
\n
  rJS(window)\n
    .ready(function (gadget) {\n
      gadget.props = {\n
        options: {},\n
        start_deferred: RSVP.defer()\n
      };\n
    })\n
\n
    .declareMethod(\'getCommandUrlFor\', function (options) {\n
      var command = options.command,\n
        absolute_url = options.absolute_url,\n
        hash,\n
        args = options.options,\n
        valid = true,\n
        key;\n
      // Only authorize \'command\', \'options\', \'absolute_url\' keys\n
      // Drop all other kind of parameters, to detect issue more easily\n
      for (key in options) {\n
        if (options.hasOwnProperty(key)) {\n
          if ((key !== \'command\') && (key !== \'options\') && (key !== \'absolute_url\')) {\n
            valid = false;\n
          }\n
        }\n
      }\n
      if (valid && (options.command) && (VALID_URL_COMMAND_DICT.hasOwnProperty(options.command))) {\n
        hash = getCommandUrlFor(this, command, args);\n
      } else {\n
        hash = getCommandUrlFor(this, \'error\', options);\n
      }\n
\n
      if (absolute_url) {\n
        hash = new URL(hash, window.location.href).href;\n
      }\n
      return hash;\n
    })\n
\n
    .declareMethod(\'redirect\', function (options) {\n
      return this.getCommandUrlFor(options)\n
        .push(function (hash) {\n
          window.location.replace(hash);\n
\n
          // prevent returning unexpected response\n
          // wait for the hash change to occur\n
          // fail if nothing happens\n
          return RSVP.timeout(REDIRECT_TIMEOUT);\n
        });\n
    })\n
\n
    .declareMethod(\'getUrlParameter\', function (key) {\n
      return this.props.options[key];\n
    })\n
\n
    .declareMethod(\'route\', function (command_options) {\n
      if (command_options.method === PREFIX_DISPLAY) {\n
        return routeDisplay(command_options);\n
      }\n
      if (command_options.method === PREFIX_COMMAND) {\n
        return routeCommand(command_options);\n
      }\n
      if (command_options.method) {\n
        throw new Error(\'Unsupported hash method: \' + command_options.method);\n
      }\n
      return routeMethodLess();\n
    })\n
\n
    .declareMethod(\'start\', function () {\n
      this.props.start_deferred.resolve();\n
    })\n
\n
    .declareAcquiredMethod(\'renderApplication\', \'renderApplication\')\n
\n
    .declareService(function () {\n
      var gadget = this;\n
      return new RSVP.Queue()\n
        .push(function () {\n
          return gadget.props.start_deferred.promise;\n
        })\n
        .push(function () {\n
          // console.info(\'router service: listen to hash change\');\n
          return listenHashChange(gadget);\n
        });\n
    });\n
\n
}(window, rJS, RSVP, loopEventListener, document, URL));\n


]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>JabberClient Gadget  Router JS</string> </value>
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
                        <float>1456334186.39</float>
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
                <value> <string>949.35416.23201.12748</string> </value>
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
                        <float>1456845631.45</float>
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
                        <float>1456333611.91</float>
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
