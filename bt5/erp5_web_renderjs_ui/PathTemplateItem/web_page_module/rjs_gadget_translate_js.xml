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
            <value> <string>gadget_translate.js</string> </value>
        </item>
        <item>
            <key> <string>description</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>rjs_gadget_translate_js</string> </value>
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

/*jslint indent: 2, maxlen: 80, nomen: true, todo: true, unparam:true*/\n
/*global window, rJS, document, i18n, UriTemplate, fetchLanguage, RSVP*/\n
(function (window, rJS, i18n, UriTemplate) {\n
  "use strict";\n
\n
  /////////////////////////////////////////////////////////////////\n
  // Some methods\n
  /////////////////////////////////////////////////////////////////\n
  function getTranslationDict(my_gadget, my_language) {\n
    var props = my_gadget.property_dict,\n
      cookie_lang = fetchLanguage(),\n
      lang = cookie_lang || props.default_language || my_language,\n
      path =  props.src + "?language=" + lang + "&namespace=dict";\n
    return new RSVP.Queue()\n
      .push(function () {\n
        return my_gadget.jio_getAttachment({\n
          "_id": "erp5",\n
          "_attachment": path\n
        });\n
      })\n
      .push(function (my_event) {\n
        return my_event.data;\n
      });\n
  }\n
\n
  // XXX: language definitions are not standard compliant!\n
  // "zh-CN" is a language, "zh" is not, browser will return the "zh-CN"\n
  // on internal i18n methods, which requires this method to "fix"\n
  function fetchLanguage() {\n
    var lang = i18n.detectLanguage();\n
    if (lang.length > 2) {\n
      return lang.substring(0, 2);\n
    }\n
    return lang;\n
  }\n
\n
  /////////////////////////////////////////////////////////////////\n
  // Gadget behaviour\n
  /////////////////////////////////////////////////////////////////\n
  rJS(window)\n
\n
    /////////////////////////////////////////////////////////////////\n
    // ready\n
    /////////////////////////////////////////////////////////////////\n
\n
    // retrieve initializatin and web site properties\n
    // XXX: This takes too long for header and sometimes for panel as both\n
    // run things on .ready() = outside chain (eg. calling header.render() on \n
    // header .ready())\n
    // XXX: Header "fixable" by adding notifyUpdate\n
    .ready(function (my_gadget) {\n
      my_gadget.property_dict = {};\n
\n
      return new RSVP.Queue()\n
        .push(function () {\n
          return RSVP.all([\n
            my_gadget.getSiteRoot(),\n
            my_gadget.getTranslationMethod()\n
          ]);\n
        })\n
        .push(function (my_config_list) {\n
          var url;\n
          url = my_config_list[0]\n
          my_gadget.property_dict.src = my_config_list[1];\n
          return my_gadget.jio_getAttachment({\n
            "_id": "erp5",\n
            "_attachment": url\n
          });\n
        })\n
        .push(function (my_hateoas) {\n
          var url;\n
          // NOTE: at this point createJIO has not been called yet, so allDocs\n
          // is not available and must be called "manually"\n
          // XXX: Improve\n
          url = UriTemplate.parse(my_hateoas.data._links.raw_search.href)\n
            .expand({\n
              query: \'portal_type: "Web Site" AND title: "\'\n
                + my_hateoas.data._links.parent.name  + \'"\',\n
              select_list: [\n
                "available_language_set",\n
                "default_available_language"\n
              ],\n
              limit: [0, 1]\n
            });\n
\n
          return my_gadget.jio_getAttachment({\n
            "_id": "erp5",\n
            "_attachment": url\n
          });\n
        })\n
        .push(function (my_site_configuration) {\n
          var web_site = my_site_configuration.data._embedded.contents[0];\n
          // set remaining properties\n
          my_gadget.property_dict.language_list =\n
            web_site.available_language_set;\n
          my_gadget.property_dict.default_language =\n
            web_site.default_available_language;\n
        });\n
    })\n
\n
    // Fetch first dict here, based on info retrieved from ERP5 website object\n
    .ready(function (my_gadget) {\n
      var props = my_gadget.property_dict;\n
      // skip if translations are not available\n
      if (props.translation_disabled) {\n
        return my_gadget;\n
      }\n
\n
      return new RSVP.Queue()\n
        .push(function () {\n
          return getTranslationDict(my_gadget);\n
        })\n
        .push(function (my_language_dict) {\n
          props.current_language_dict = my_language_dict;\n
\n
          // initialize i18n\n
          i18n.init({\n
            "customLoad": function (my_lng, my_ns,\n
               my_option_dict, my_callback) {\n
              // translations available now\n
              my_callback(null, props.current_language_dict);\n
            },\n
            //"use_browser_language": true,\n
            "lng": fetchLanguage() || props.default_language,\n
            "load": "current",\n
            "fallbackLng": false,\n
            "ns": \'dict\'\n
          });\n
          return my_gadget.notifyUpdate();\n
        });\n
    })\n
\n
\n
    /////////////////////////////////////////////////////////////////\n
    // acquired methods\n
    /////////////////////////////////////////////////////////////////\n
    .declareAcquiredMethod("notifyUpdate", "notifyUpdate")\n
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")\n
    .declareAcquiredMethod("getSiteRoot", "getSiteRoot")\n
    .declareAcquiredMethod("getTranslationMethod", "getTranslationMethod")\n
\n
    /////////////////////////////////////////////////////////////////\n
    // declared methods\n
    /////////////////////////////////////////////////////////////////\n
\n
    // expose languages to gadget which want to know (eg panel)\n
    .declareMethod(\'getLanguageList\', function () {\n
      return JSON.stringify(this.property_dict.language_list);\n
    })\n
\n
    .declareMethod(\'changeLanguage\', function (my_new_language) {\n
      var gadget = this,\n
        current_language = fetchLanguage();\n
\n
      // XXX: relies on cookie value set by i18n!\n
      if (current_language !== my_new_language &&\n
          gadget.property_dict.translation_disabled === undefined) {\n
        return RSVP.Queue()\n
          .push(function () {\n
            return getTranslationDict(gadget, my_new_language);\n
          })\n
          .push(function (my_language_dict) {\n
            gadget.property_dict.current_language_dict = my_language_dict;\n
            i18n.setLng(my_new_language);\n
            // XXX: for now, reload as the language is stored in cookie\n
            window.location.reload();\n
            //return gadget.translateElementList();\n
          });\n
      }\n
\n
      return gadget;\n
    })\n
\n
    // translate a list of elements passed and returned as string\n
    .declareMethod(\'translateHtml\', function (my_string) {\n
      var temp, element_list, i, i_len, element, lookup, translate_list, target,\n
        route_text, has_breaks, l, l_len, gadget;\n
\n
      gadget = this;\n
\n
      // skip if no translations available\n
      if (gadget.property_dict.translation_disabled) {\n
        return my_string;\n
      }\n
\n
      // NOTE: <div> cannot be used for everything... (like table rows)\n
      // TODO: currently I only update where needed. Eventually all calls to\n
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
              element.setAttribute(target[0].substr(1), i18n.t(target[1]));\n
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
                element.previousSibling.textContent = i18n.t(target[1]);\n
              }\n
              element.value = i18n.t(target[1]);\n
              break;\n
            case "[parent":\n
              element.parentNode.childNodes[0].textContent =\n
                  i18n.t(target[1]);\n
              break;\n
            case "[node":\n
              element.childNodes[0].textContent = i18n.t(target[1]);\n
              break;\n
            case "[last":\n
              // if null, append, if textnode replace, if span, appned\n
              if (element.lastChild && element.lastChild.nodeType === 3) {\n
                element.lastChild.textContent = i18n.t(target[1]);\n
              } else {\n
                element.appendChild(document.createTextNode(i18n.t(target[1])));\n
              }\n
              break;\n
            case "[html":\n
              element.innerHTML = i18n.t(target[1]);\n
              break;\n
            default:\n
              // NOTE: be careful of emptying elements with children!\n
              while (element.hasChildNodes()) {\n
                element.removeChild(element.lastChild);\n
              }\n
              element.appendChild(document.createTextNode(i18n.t(translate_list[l])));\n
              element.appendChild(document.createElement("span"));\n
              break;\n
            }\n
          }\n
        }\n
      }\n
      // return string\n
      return temp.innerHTML;\n
    });\n
}(window, rJS, i18n, UriTemplate));

]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Gadget Translate JS</string> </value>
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
                <value> <string>super_sven</string> </value>
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
                        <float>1418835927.52</float>
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
                <value> <string>xiaowu</string> </value>
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
                <value> <string>942.40436.35446.62327</string> </value>
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
                        <float>1430140853.25</float>
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
                <value> <string>super_sven</string> </value>
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
                        <float>1418835843.83</float>
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
