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
            <value> <string>gadget_translation.js</string> </value>
        </item>
        <item>
            <key> <string>description</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>rjs_gadget_translation_js</string> </value>
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

/*global document, window, rJS, translation_data */\n
/*jslint nomen: true, indent: 2 */\n
(function (document, window, rJS, translation_data) {\n
  "use strict";\n
\n
  function translate(string) {\n
    // XXX i18n.t\n
    return translation_data.en[string] || string;\n
  }\n
\n
  rJS(window)\n
\n
    /////////////////////////////////////////////////////////////////\n
    // ready\n
    /////////////////////////////////////////////////////////////////\n
    .ready(function (gadget) {\n
      gadget.property_dict = {};\n
    })\n
\n
    .declareMethod(\'translate\', function (string) {\n
      // XXX Allow to change the language\n
      return translate(string);\n
    })\n
\n
    // translate a list of elements passed and returned as string\n
    .declareMethod(\'translateHtml\', function (my_string) {\n
      var temp, element_list, i, i_len, element, lookup, translate_list, target,\n
        route_text, has_breaks, l, l_len, gadget, j, j_len;\n
\n
      gadget = this;\n
\n
      // skip if no translations available\n
      if (gadget.property_dict.translation_disabled) {\n
        return my_string;\n
      }\n
\n
      // NOTE: <div> cannot be used for everything... (like table rows)\n
      // XXX: currently I only update where needed. Eventually all calls to\n
      // translateHtml should pass "their" proper wrapping element\n
      temp = document.createElement("div");\n
      temp.innerHTML = my_string;\n
\n
      element_list = temp.querySelectorAll("[data-i18n]");\n
\n
      for (i = 0, i_len = element_list.length; i < i_len; i += 1) {\n
        element = element_list[i];\n
        lookup = element.getAttribute("data-i18n");\n
\n
        if (lookup) {\n
          translate_list = lookup.split(";");\n
\n
          for (l = 0, l_len = translate_list.length; l < l_len; l += 1) {\n
            target = translate_list[l].split("]");\n
\n
            switch (target[0]) {\n
            case "[placeholder":\n
            case "[alt":\n
            case "[title":\n
              element.setAttribute(target[0].substr(1), translate(target[1]));\n
              break;\n
            case "[value":\n
              has_breaks = element.previousSibling.textContent.match(/\\n/g);\n
\n
              // JQM inputs > this avoids calling checkboxRadio("refresh")!\n
              if (element.tagName === "INPUT") {\n
                switch (element.type) {\n
                case "submit":\n
                case "reset":\n
                case "button":\n
                  route_text = true;\n
                  break;\n
                }\n
              }\n
              if (route_text && (has_breaks || []).length === 0) {\n
                element.previousSibling.textContent = translate(target[1]);\n
              }\n
              element.value = translate(target[1]);\n
              break;\n
            case "[parent":\n
              element.parentNode.childNodes[0].textContent =\n
                  translate(target[1]);\n
              break;\n
            case "[node":\n
              element.childNodes[0].textContent = translate(target[1]);\n
              break;\n
            case "[last":\n
              // if null, append, if textnode replace, if span, appned\n
              if (element.lastChild && element.lastChild.nodeType === 3) {\n
                element.lastChild.textContent = translate(target[1]);\n
              } else {\n
                element.appendChild(document.createTextNode(translate(target[1])));\n
              }\n
              break;\n
            case "[html":\n
              element.innerHTML = translate(target[1]);\n
              break;\n
            default:\n
              if (element.hasChildNodes()) {\n
                for (j = 0, j_len = element.childNodes.length; j < j_len; j += 1) {\n
                  if (element.childNodes[j].nodeType === 3) {\n
                    element.childNodes[j].textContent = translate(translate_list[l]);\n
                  }\n
                }\n
              } else {\n
                element.textContent = translate(translate_list[l]);\n
              }\n
              break;\n
            }\n
          }\n
        }\n
      }\n
      // return string\n
      return temp.innerHTML;\n
    });\n
\n
}(document, window, rJS, translation_data));\n


]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Gadget Translation JS</string> </value>
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
                        <float>1438012141.03</float>
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
                <value> <string>948.17388.42239.34542</string> </value>
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
                        <float>1452009218.06</float>
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
                        <float>1438012010.81</float>
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
