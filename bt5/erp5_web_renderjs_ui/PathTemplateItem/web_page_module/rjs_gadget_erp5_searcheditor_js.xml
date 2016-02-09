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
            <value> <string>gadget_erp5_search_editor.js</string> </value>
        </item>
        <item>
            <key> <string>description</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>rjs_gadget_erp5_searcheditor_js</string> </value>
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

/*jslint indent: 2, maxerr: 3, maxlen: 100, nomen: true */\n
/*global window, document, rJS, RSVP, Handlebars, $, loopEventListener,\n
  QueryFactory, SimpleQuery, ComplexQuery, Query, console*/\n
(function (window, document, rJS, RSVP, Handlebars, $, loopEventListener,\n
  QueryFactory, SimpleQuery, ComplexQuery, Query, console) {\n
  "use strict";\n
  var gadget_klass = rJS(window),\n
    filter_item_source = gadget_klass.__template_element\n
                         .getElementById("filter-item-template")\n
                         .innerHTML,\n
    filter_item_template = Handlebars.compile(filter_item_source),\n
    filter_source = gadget_klass.__template_element\n
                         .getElementById("filter-template")\n
                         .innerHTML,\n
    filter_template = Handlebars.compile(filter_source),\n
\n
    options_source = gadget_klass.__template_element\n
                         .getElementById("options-template")\n
                         .innerHTML,\n
    options_template = Handlebars.compile(options_source);\n
\n
  Handlebars.registerHelper(\'equal\', function (left_value,\n
    right_value, options) {\n
    if (arguments.length < 3) {\n
      throw new Error("Handlebars Helper equal needs 2 parameters");\n
    }\n
    if (left_value !== right_value) {\n
      return options.inverse(this);\n
    }\n
    return options.fn(this);\n
  });\n
\n
  //XXXXX\n
  //define input\'s type according to column\'s value\n
  //the way to determiner is not generic\n
  function isNumericComparison(value) {\n
    return value.indexOf(\'date\') !== -1 ||\n
      value.indexOf(\'quantity\') !== -1 ||\n
      value.indexOf(\'price\') !== -1;\n
  }\n
\n
  function createOptionsTemplate(gadget, value) {\n
    var option = [],\n
      tmp,\n
      i;\n
    if (value !== "searchable_text") {\n
      if (isNumericComparison(value)) {\n
        tmp = gadget.props.numeric;\n
      } else {\n
        tmp = gadget.props.other;\n
      }\n
    } else {\n
      tmp = gadget.props.default;\n
    }\n
    for (i = 0; i < tmp.length; i += 1) {\n
      option.push({\n
        "text": tmp[i][0],\n
        "value": tmp[i][1]\n
      });\n
    }\n
    return gadget.translateHtml(options_template({option: option}));\n
  }\n
\n
\n
\n
\n
  function createFilterItemTemplate(gadget, class_value, filter_item) {\n
    var column_list = gadget.props.search_column_list,\n
      option = [],\n
      tmp,\n
      operator_option = [],\n
      input_type = "text",\n
      i;\n
\n
    if (filter_item) {\n
      if (isNumericComparison(filter_item.key)) {\n
        tmp = gadget.props.numeric;\n
        if (filter_item.key.indexOf("date") !== -1) {\n
          input_type = "date";\n
        } else {\n
          input_type = "number";\n
        }\n
      } else {\n
        tmp = gadget.props.other;\n
      }\n
    } else {\n
      tmp = gadget.props.default;\n
      filter_item = {};\n
    }\n
\n
    for (i = 0; i < tmp.length; i += 1) {\n
      operator_option.push({\n
        "text": tmp[i][0],\n
        "value": tmp[i][1],\n
        "selected_option": filter_item.operator\n
      });\n
    }\n
\n
    for (i = 0; i < column_list.length; i += 1) {\n
      option.push({\n
        "text": column_list[i][1],\n
        "value": column_list[i][0],\n
        "selected_option": filter_item.key || "searchable_text"\n
      });\n
    }\n
    return gadget.translateHtml(filter_item_template({\n
      option: option,\n
      operator_option: operator_option,\n
      class_value: class_value,\n
      input_value: filter_item.value,\n
      input_type: input_type\n
    }));\n
  }\n
\n
\n
  function listenToSelect(gadget, class_value) {\n
    var list = [],\n
      i,\n
      filter_item_list =\n
        gadget.props.element.querySelectorAll("." + class_value);\n
    function createFunction(i) {\n
      var select_list = filter_item_list[i].querySelectorAll("select"),\n
        input = filter_item_list[i].querySelector("input");\n
      return loopEventListener(\n
        select_list[0],\n
        "change",\n
        false,\n
        function (event) {\n
          return new RSVP.Queue()\n
            .push(function () {\n
              return createOptionsTemplate(gadget, event.target.value);\n
            })\n
            .push(function (innerHTML) {\n
              select_list[1].innerHTML = innerHTML;\n
              $(select_list[1]).selectmenu(\'refresh\');\n
              if (isNumericComparison(event.target.value)) {\n
                if (event.target.value.indexOf("date") !== -1) {\n
                  input.setAttribute("type", "date");\n
                } else {\n
                  input.setAttribute("type", "number");\n
                }\n
              } else {\n
                input.setAttribute("type", "text");\n
              }\n
            });\n
        }\n
      );\n
    }\n
    for (i = 0; i < filter_item_list.length; i += 1) {\n
      list.push(createFunction(i));\n
    }\n
    return RSVP.all(list);\n
  }\n
\n
\n
\n
\n
  rJS(window)\n
    /////////////////////////////////////////////////////////////////\n
    // ready\n
    /////////////////////////////////////////////////////////////////\n
    // Init local properties\n
    .ready(function (g) {\n
      g.props = {};\n
    })\n
    .ready(function (g) {\n
      return g.getElement()\n
        .push(function (element) {\n
          g.props.element = element;\n
          g.props.numeric = [["Equals To", "="], ["Greater Than", ">"],\n
            ["Less Than", "<"], ["Not Greater Than", "<="],\n
            ["Not Less Than", ">="]];\n
          g.props.other = [["Exact Match", "exacte_match"],\n
            ["keyword", "keyword"]];\n
          g.props.default = [["Contain", "Contain"]];\n
        });\n
    })\n
\n
\n
\n
    //////////////////////////////////////////////\n
    // acquired method\n
    //////////////////////////////////////////////\n
    .declareAcquiredMethod("translateHtml", "translateHtml")\n
    .declareAcquiredMethod("redirect", "redirect")\n
    .declareAcquiredMethod("trigger", "trigger")\n
    //////////////////////////////////////////////\n
    // initialize the gadget content\n
    //////////////////////////////////////////////\n
    .declareMethod(\'render\', function (options) {\n
      var gadget = this;\n
      gadget.props.search_column_list = options.search_column_list;\n
      gadget.props.begin_from = options.begin_from;\n
\n
      gadget.props.extended_search = options.extended_search;\n
\n
      return new RSVP.Queue()\n
        .push(function () {\n
          var tmp = filter_template();\n
          return gadget.translateHtml(tmp);\n
        })\n
        .push(function (translated_html) {\n
          var tmp = document.createElement("div");\n
          tmp.innerHTML = translated_html;\n
          gadget.props.element.querySelector(".container").appendChild(tmp);\n
        });\n
    })\n
    //////////////////////////////////////////////\n
    .declareService(function () {\n
      var gadget = this,\n
        i,\n
        list = [],\n
        or = gadget.props.element.querySelector(".or"),\n
        and = gadget.props.element.querySelector(".and"),\n
        container = gadget.props.element.querySelector(".filter_item_container"),\n
        query_list;\n
      if (gadget.props.extended_search) {\n
        //string to query\n
        try {\n
          query_list = QueryFactory.create(gadget.props.extended_search);\n
        } catch (error) {\n
          //XXXX hack to not crash interface\n
          //it catch all error, not only search criteria invalid error\n
          console.warn(error);\n
          return;\n
        }\n
        if (query_list.operator === "OR") {\n
          or.checked = true;\n
          and.checked = false;\n
          or.parentElement.children[0].setAttribute("class",\n
            "ui-btn ui-corner-all ui-btn-inherit ui-btn-icon-left ui-radio-on");\n
          and.parentElement.children[0].setAttribute("class",\n
            "ui-btn ui-corner-all ui-btn-inherit ui-btn-icon-left ui-radio-off");\n
        }\n
\n
        query_list = query_list.query_list || [query_list];\n
        for (i = 0; i < query_list.length; i += 1) {\n
          list.push(createFilterItemTemplate(gadget, "auto", query_list[i]));\n
        }\n
        return RSVP.Queue()\n
          .push(function () {\n
            return RSVP.all(list);\n
          })\n
          .push(function (all_result) {\n
            var innerHTML = "",\n
              select_list;\n
            for (i = 0; i < all_result.length; i += 1) {\n
              innerHTML += all_result[i];\n
            }\n
            container.innerHTML = innerHTML;\n
            select_list = container.querySelectorAll("select");\n
            for (i = 0; i < select_list.length; i += 1) {\n
              $(select_list[i]).selectmenu();\n
            }\n
            return listenToSelect(gadget, "auto");\n
          });\n
      }\n
    })\n
    .declareService(function () {\n
      var gadget = this,\n
        container = gadget.props.element.querySelector(".filter_item_container");\n
      return loopEventListener(\n
        gadget.props.element.querySelector(".filter_editor"),\n
        "submit",\n
        false,\n
        function () {\n
          var focused = document.activeElement;\n
          if (focused.nodeName === "BUTTON") {\n
            container.removeChild(focused.parentElement.parentElement);\n
          }\n
        }\n
      );\n
    })\n
    .declareService(function () {\n
      var gadget = this;\n
      return loopEventListener(\n
        gadget.props.element.querySelector(".submit"),\n
        "submit",\n
        false,\n
        function () {\n
          var i,\n
            simple_operator,\n
            query,\n
            key,\n
            select_list,\n
            simple_query_list = [],\n
            complex_query,\n
            select,\n
            value,\n
            options = {},\n
            filter_item_list = gadget.props.element.querySelectorAll(".filter_item"),\n
            and = gadget.props.element.querySelector(".and");\n
          for (i = 0; i < filter_item_list.length; i += 1) {\n
            select_list = filter_item_list[i].querySelectorAll("select");\n
            value = filter_item_list[i].querySelector("input").value;\n
            simple_operator = "";\n
            select = select_list[1][select_list[1].selectedIndex].value;\n
            if (select === "keyword") {\n
              value = "%" + value + "%";\n
            } else if (["", ">", "<", "<=", ">="].indexOf(select) !== -1) {\n
              simple_operator = select;\n
            }\n
\n
            if (select_list[0][select_list[0].selectedIndex].value === "searchable_text") {\n
              key = "";\n
            } else {\n
              key = select_list[0][select_list[0].selectedIndex].value;\n
            }\n
\n
            simple_query_list.push(new SimpleQuery(\n
              {\n
                key: key,\n
                operator: simple_operator,\n
                type: "simple",\n
                value: value\n
              }\n
            ));\n
          }\n
\n
          if (simple_query_list.length > 0) {\n
            complex_query = new ComplexQuery({\n
              operator: and.checked ? "AND" : "OR",\n
              query_list: simple_query_list,\n
              type: "complex"\n
            });\n
            //query to string\n
            query = Query.objectToSearchText(complex_query);\n
          } else {\n
            query = "";\n
          }\n
          options.extended_search = query;\n
          options[gadget.props.begin_from] = undefined;\n
          return gadget.redirect(\n
            {\n
              command: \'store_and_change\',\n
              options : options\n
            }\n
          );\n
        }\n
      );\n
    })\n
    .declareService(function () {\n
      var gadget = this,\n
        class_value = "add_after";\n
      return loopEventListener(\n
        gadget.props.element.querySelector(".plus"),\n
        "submit",\n
        false,\n
        function () {\n
          return new RSVP.Queue()\n
            .push(function () {\n
              return createFilterItemTemplate(gadget, class_value);\n
            })\n
            .push(function (template) {\n
              var tmp = document.createElement("div"),\n
                container = gadget.props.element.querySelector(".filter_item_container"),\n
                select_list,\n
                i;\n
              tmp.innerHTML = template;\n
              select_list = tmp.querySelectorAll("select");\n
              for (i = 0; i < select_list.length; i += 1) {\n
                $(select_list[i]).selectmenu();\n
              }\n
              container.appendChild(tmp.querySelector("div"));\n
              return listenToSelect(gadget, class_value);\n
            });\n
        }\n
      );\n
    })\n
    .declareService(function () {\n
      var gadget = this;\n
      return loopEventListener(\n
        gadget.props.element.querySelector(".delete"),\n
        "submit",\n
        false,\n
        function () {\n
          return gadget.trigger();\n
        }\n
      );\n
    });\n
\n
}(window, document, rJS, RSVP, Handlebars, $, loopEventListener,\n
  QueryFactory, SimpleQuery, ComplexQuery, Query, console));

]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Gadget Erp5 Search Editor JS</string> </value>
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
                        <float>1447863363.66</float>
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
                <value> <string>949.2121.59518.17646</string> </value>
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
                        <float>1455022145.56</float>
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
                <value>
                  <none/>
                </value>
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
                <value> <string>empty</string> </value>
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
                        <float>1447863335.99</float>
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
