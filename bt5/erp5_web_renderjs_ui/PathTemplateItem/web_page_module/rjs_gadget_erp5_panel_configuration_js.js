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
            <value> <string>gadget_erp5_panel_configuration.js</string> </value>
        </item>
        <item>
            <key> <string>description</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>rjs_gadget_erp5_panel_configuration_js</string> </value>
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

/*jslint nomen: true, indent: 2, maxerr: 3 */\n
/*global window, rJS, Handlebars, jQuery, RSVP, loopEventListener */\n
(function (window, rJS, Handlebars, $, RSVP, loopEventListener) {\n
  "use strict";\n
\n
  /////////////////////////////////////////////////////////////////\n
  // TEMPLATE API\n
  /////////////////////////////////////////////////////////////////\n
  \n
  // panel_category_list_header\n
  // {\n
  //  "close_i18n":       [SET],\n
  //  "i18n":             [title],\n
  //  "clear_i18n":       [SET],\n
  //  "update_i18n":      [SET]\n
  //  "tag_list":         [{\n
  //    "type_i18n":      [type of filter|create|...],\n
  //    "value_i18n":     [value to create or filter for, eg. region:foo]\n
  //  }]\n
  \n
  // panel_category_list_partial\n
  // {\n
  //    "i18n":           [category title],\n
  //    "tree":  [{\n
  //      "multiple":     [true to make checkbox],\n
  //      "search":       [search term, like "filter:region=France"],\n
  //      "i18n":"        [text to display]\n
  //    }]\n
  //  }]\n
  // } \n
\n
  /////////////////////////////////////////////////////////////////\n
  // some methods\n
  /////////////////////////////////////////////////////////////////\n
\n
  /////////////////////////////////////////////////////////////////\n
  // Handlebars\n
  /////////////////////////////////////////////////////////////////\n
  var gadget_klass = rJS(window),\n
    templater = gadget_klass.__template_element,\n
    \n
    // pre-compile \n
    panel_category_list_header = Handlebars.compile(\n
      templater.getElementById("panel-category-list-header").innerHTML\n
    )\n
    /*\n
    ,panel_category_list_partial = Handlebars.registerPartial(\n
      "category-taglist-partial",\n
      templater.getElementById("category-taglist-partial").innerHTML\n
    )*/;\n
  \n
  gadget_klass\n
    \n
    /////////////////////////////////////////////////////////////////\n
    // ready\n
    /////////////////////////////////////////////////////////////////\n
    .ready(function (my_gadget) {\n
      my_gadget.property_dict = {};\n
    })\n
\n
    .ready(function (my_gadget) {\n
      return my_gadget.getElement()\n
        .push(function (my_element) {\n
          my_gadget.property_dict.element = my_element;\n
          my_gadget.property_dict.defer = new RSVP.defer();\n
          my_gadget.property_dict.panel_element =\n
            my_element.querySelector(".jqm-configuration-panel");\n
        });\n
    })\n
\n
    /////////////////////////////////////////////////////////////////\n
    // acquired methods\n
    /////////////////////////////////////////////////////////////////\n
    .declareAcquiredMethod("translateHtml", "translateHtml")\n
    .declareAcquiredMethod("changeLanguage", "changeLanguage")\n
    .declareAcquiredMethod("getLanguageList", "getLanguageList")\n
    .declareAcquiredMethod(\n
      "whoWantToDisplayThisFrontPage",\n
      "whoWantToDisplayThisFrontPage"\n
    )\n
\n
    /////////////////////////////////////////////////////////////////\n
    // declared methods\n
    /////////////////////////////////////////////////////////////////\n
    .declareMethod(\'setPanelHeader\', function (my_option_dict) {\n
      var gadget = this,\n
        panel_element = gadget.property_dict.panel_element;\n
\n
      return new RSVP.Queue()\n
        .push(function () {\n
          return gadget.translateHtml(\n
            panel_category_list_header(my_option_dict)\n
          );\n
        })\n
        .push(function (my_panel_header) {\n
          panel_element.innerHTML = my_panel_header;\n
          $(panel_element).enhanceWithin();\n
          return gadget;\n
        })\n
        .push(function () {\n
          return gadget.property_dict.defer.resolve();\n
        });\n
    })\n
    .declareMethod(\'setPanelContent\', function (my_option_dict) {\n
      /*\n
        so Romain requested to have a gadget depending on use case of this\n
        panel. In our case it should be  a domain tree and it should load a \n
        certain amount  or type of domains/categories\n
        Alternatively we can load something else. Question is whether this\n
        should be a domain tree per ... app or if every domaintree can be \n
        different depending on a parameter passed into intialization.\n
        \n
        Also, we must make clear that the content can be dumped to make space \n
        for new content!\n
        \n
        Do this.\n
      */\n
    })\n
\n
    .declareMethod(\'togglePanel\', function () {\n
      var gadget = this;\n
\n
      $(gadget.property_dict.panel_element).panel("toggle");\n
    })\n
\n
    .declareMethod(\'render\', function (my_option_dict) {\n
      var gadget = this,\n
        panel_element = gadget.property_dict.panel_element;\n
\n
      return new RSVP.Queue()\n
        .push(function () {\n
          $(panel_element).panel({\n
            display: "overlay",\n
            position: "right",\n
            theme: "c"\n
          });\n
        });\n
    })\n
\n
    /////////////////////////////////////////////////////////////////\n
    // declared services\n
    /////////////////////////////////////////////////////////////////\n
    .declareService(function () {\n
      var gadget = this,\n
        $panel_element = $(gadget.property_dict.panel_element);\n
\n
      function formSubmit() {\n
        return gadget.togglePanel();\n
      }\n
    \n
      return new RSVP.Queue()\n
        .push(function () {\n
          return gadget.property_dict.defer.promise;\n
        })\n
        .push(function () {\n
          $panel_element.enhanceWithin();\n
          var form_list = gadget.property_dict.element.querySelectorAll(\'form\'),\n
            event_list = [],\n
            i,\n
            len;\n
\n
          for (i = 0, len = form_list.length; i < len; i += 1) {\n
            event_list[i] = loopEventListener(\n
              form_list[i],\n
              \'submit\',\n
              false,\n
              formSubmit\n
            );\n
          }\n
          return RSVP.all(event_list);\n
        })\n
      \n
    });\n
\n
}(window, rJS, Handlebars, jQuery, RSVP, loopEventListener));\n
\n
\n
\n
  /*\n
  \n
        .push(function (my_panel_category_list) {\n
          return gadget.factoryPanelCategoryList({\n
            "theme": "a",\n
            "position": "left",\n
            "animate_class": "overlay",\n
            "close_i18n": "gen.close",\n
            "i18n": "gen.categories",\n
            "clear_i18n": "gen.clear",\n
            "update_i18n": "gen.update",\n
            "tag_list": tag_list,\n
            "tree": my_panel_category_list\n
          });\n
        })\n
        .push(function (my_panel_content) {\n
          return gadget.translateHtml(my_panel_content);\n
        })\n
        .push(function (my_translated_panel_content) {\n
          return gadget.setPanel("panel_search", my_translated_panel_content);\n
        });\n
  \n
  */

]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Gadget ERP5 Panel Configuration JS</string> </value>
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
                <value> <string>publish</string> </value>
            </item>
            <item>
                <key> <string>actor</string> </key>
                <value> <string>sven</string> </value>
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
                        <float>1429106462.69</float>
                        <string>GMT</string>
                      </tuple>
                    </state>
                  </object>
                </value>
            </item>
            <item>
                <key> <string>validation_state</string> </key>
                <value> <string>published</string> </value>
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
                <value> <string>sven</string> </value>
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
                <value> <string>942.62105.59106.27904</string> </value>
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
                        <float>1431354245.91</float>
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
                <value> <string>sven</string> </value>
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
                        <float>1429105919.74</float>
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
