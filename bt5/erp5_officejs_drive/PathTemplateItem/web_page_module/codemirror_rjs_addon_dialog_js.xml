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
            <value> <string>codemirror_addon_dialog.js</string> </value>
        </item>
        <item>
            <key> <string>description</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>codemirror_rjs_addon_dialog_js</string> </value>
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

// CodeMirror, copyright (c) by Marijn Haverbeke and others\n
// Distributed under an MIT license: http://codemirror.net/LICENSE\n
\n
// Open simple dialogs on top of an editor. Relies on dialog.css.\n
\n
(function(mod) {\n
  if (typeof exports == "object" && typeof module == "object") // CommonJS\n
    mod(require("../../lib/codemirror"));\n
  else if (typeof define == "function" && define.amd) // AMD\n
    define(["../../lib/codemirror"], mod);\n
  else // Plain browser env\n
    mod(CodeMirror);\n
})(function(CodeMirror) {\n
  function dialogDiv(cm, template, bottom) {\n
    var wrap = cm.getWrapperElement();\n
    var dialog;\n
    dialog = wrap.appendChild(document.createElement("div"));\n
    if (bottom)\n
      dialog.className = "CodeMirror-dialog CodeMirror-dialog-bottom";\n
    else\n
      dialog.className = "CodeMirror-dialog CodeMirror-dialog-top";\n
\n
    if (typeof template == "string") {\n
      dialog.innerHTML = template;\n
    } else { // Assuming it\'s a detached DOM element.\n
      dialog.appendChild(template);\n
    }\n
    return dialog;\n
  }\n
\n
  function closeNotification(cm, newVal) {\n
    if (cm.state.currentNotificationClose)\n
      cm.state.currentNotificationClose();\n
    cm.state.currentNotificationClose = newVal;\n
  }\n
\n
  CodeMirror.defineExtension("openDialog", function(template, callback, options) {\n
    if (!options) options = {};\n
\n
    closeNotification(this, null);\n
\n
    var dialog = dialogDiv(this, template, options.bottom);\n
    var closed = false, me = this;\n
    function close(newVal) {\n
      if (typeof newVal == \'string\') {\n
        inp.value = newVal;\n
      } else {\n
        if (closed) return;\n
        closed = true;\n
        dialog.parentNode.removeChild(dialog);\n
        me.focus();\n
\n
        if (options.onClose) options.onClose(dialog);\n
      }\n
    }\n
\n
    var inp = dialog.getElementsByTagName("input")[0], button;\n
    if (inp) {\n
      if (options.value) {\n
        inp.value = options.value;\n
        if (options.selectValueOnOpen !== false) {\n
          inp.select();\n
        }\n
      }\n
\n
      if (options.onInput)\n
        CodeMirror.on(inp, "input", function(e) { options.onInput(e, inp.value, close);});\n
      if (options.onKeyUp)\n
        CodeMirror.on(inp, "keyup", function(e) {options.onKeyUp(e, inp.value, close);});\n
\n
      CodeMirror.on(inp, "keydown", function(e) {\n
        if (options && options.onKeyDown && options.onKeyDown(e, inp.value, close)) { return; }\n
        if (e.keyCode == 27 || (options.closeOnEnter !== false && e.keyCode == 13)) {\n
          inp.blur();\n
          CodeMirror.e_stop(e);\n
          close();\n
        }\n
        if (e.keyCode == 13) callback(inp.value, e);\n
      });\n
\n
      if (options.closeOnBlur !== false) CodeMirror.on(inp, "blur", close);\n
\n
      inp.focus();\n
    } else if (button = dialog.getElementsByTagName("button")[0]) {\n
      CodeMirror.on(button, "click", function() {\n
        close();\n
        me.focus();\n
      });\n
\n
      if (options.closeOnBlur !== false) CodeMirror.on(button, "blur", close);\n
\n
      button.focus();\n
    }\n
    return close;\n
  });\n
\n
  CodeMirror.defineExtension("openConfirm", function(template, callbacks, options) {\n
    closeNotification(this, null);\n
    var dialog = dialogDiv(this, template, options && options.bottom);\n
    var buttons = dialog.getElementsByTagName("button");\n
    var closed = false, me = this, blurring = 1;\n
    function close() {\n
      if (closed) return;\n
      closed = true;\n
      dialog.parentNode.removeChild(dialog);\n
      me.focus();\n
    }\n
    buttons[0].focus();\n
    for (var i = 0; i < buttons.length; ++i) {\n
      var b = buttons[i];\n
      (function(callback) {\n
        CodeMirror.on(b, "click", function(e) {\n
          CodeMirror.e_preventDefault(e);\n
          close();\n
          if (callback) callback(me);\n
        });\n
      })(callbacks[i]);\n
      CodeMirror.on(b, "blur", function() {\n
        --blurring;\n
        setTimeout(function() { if (blurring <= 0) close(); }, 200);\n
      });\n
      CodeMirror.on(b, "focus", function() { ++blurring; });\n
    }\n
  });\n
\n
  /*\n
   * openNotification\n
   * Opens a notification, that can be closed with an optional timer\n
   * (default 5000ms timer) and always closes on click.\n
   *\n
   * If a notification is opened while another is opened, it will close the\n
   * currently opened one and open the new one immediately.\n
   */\n
  CodeMirror.defineExtension("openNotification", function(template, options) {\n
    closeNotification(this, close);\n
    var dialog = dialogDiv(this, template, options && options.bottom);\n
    var closed = false, doneTimer;\n
    var duration = options && typeof options.duration !== "undefined" ? options.duration : 5000;\n
\n
    function close() {\n
      if (closed) return;\n
      closed = true;\n
      clearTimeout(doneTimer);\n
      dialog.parentNode.removeChild(dialog);\n
    }\n
\n
    CodeMirror.on(dialog, \'click\', function(e) {\n
      CodeMirror.e_preventDefault(e);\n
      close();\n
    });\n
\n
    if (duration)\n
      doneTimer = setTimeout(close, duration);\n
\n
    return close;\n
  });\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>CodeMirror Addon Dialog</string> </value>
        </item>
        <item>
            <key> <string>version</string> </key>
            <value> <string>4.3.0</string> </value>
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
                        <float>1406898405.97</float>
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
                <value> <string>948.28974.19283.5956</string> </value>
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
                        <float>1453133785.24</float>
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
                        <float>1405084229.95</float>
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
