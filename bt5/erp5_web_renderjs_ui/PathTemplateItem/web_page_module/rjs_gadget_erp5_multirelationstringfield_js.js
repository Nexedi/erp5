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
            <value> <string>gadget_erp5_field_multirelationstring.js</string> </value>
        </item>
        <item>
            <key> <string>description</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>rjs_gadget_erp5_multirelationstringfield_js</string> </value>
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

/*global window, document, rJS, RSVP, URI, loopEventListener,\n
promiseEventListener */\n
/*jslint indent: 2, maxerr: 3 */\n
(function (window, document, rJS, RSVP, URI, loopEventListener,\n
  promiseEventListener) {\n
  "use strict";\n
\n
  ////////////////////////////////////\n
  // Some methods\n
  ////////////////////////////////////\n
\n
  // XXX: re-factor.\n
  // clear the autocomplete options, reset the plane tag and remove the create\n
  // new tag. Since plane and new tag sometimes need to stay, "override_tag"\n
  // can be set to something arbitrary to prevent removal of the respective\n
  // element.\n
\n
  function clearResults(wrapper, my_override_tag) {\n
    function dump(my_parent, my_tag_name) {\n
      var child_list = my_parent.children,\n
        i,\n
        i_len,\n
        child;\n
\n
      // XXX: now that link ("A") stays, rewrite the whole element clearing!\n
      for (i = 0, i_len = child_list.length; i < i_len; i += 1) {\n
        child = child_list[i];\n
        if (child && child.tagName === my_tag_name) {\n
          if (my_tag_name === "A") {\n
            child.className += " ui-disabled";\n
          } else {\n
            my_parent.removeChild(child);\n
          }\n
        }\n
      }\n
    }\n
\n
    // always clear autocomplete results (UL), the create new record input (DIV)\n
    // will only be removed on new searches, while the plane (A) is disabled\n
    dump(wrapper, "UL");\n
    dump(wrapper, my_override_tag || "DIV");\n
    dump(wrapper.parentElement, my_override_tag || "A");\n
  }\n
\n
  // creates a tag indicating the value entered will be added as new object\n
  // of displayed type when the form is submitted. Clicking the tag will\n
  // reset the field, because otherwise accidentially typing something always\n
  // requires to reselect and manually backspace the value. Click to reset is\n
  // much easier/faster\n
  function createNewTag(my_gadget, i) {\n
    var props = my_gadget.props,\n
      field_json = props.field_json,\n
      tag,\n
      group,\n
      controls,\n
      info,\n
      link;\n
\n
    info = field_json.portal_types.filter(function (item, pos, self) {\n
      return self.indexOf(item) === pos;\n
    }).join("");\n
\n
    link = document.createElement("a");\n
    link.setAttribute("href", "#");\n
    link.className = "ui-first-child ui-last-child ui-btn ui-corner-all " +\n
      "ui-btn-inherit ui-btn-active ui-btn-icon-right ui-icon-delete";\n
    link.textContent = "Create: " + info;\n
    my_gadget.props.select_uid_list[i] = "_newContent_" + info;\n
\n
    controls = document.createElement("div");\n
    controls.className = "ui-controlgroup-controls";\n
    controls.appendChild(link);\n
\n
\n
    group = document.createElement("div");\n
    group.className = "ui-controlgroup ui-controlgroup-horizontal " +\n
      "ui-corner-all";\n
    group.appendChild(controls);\n
\n
    tag = document.createElement("div");\n
    tag.className = "ui-tag-list ui-tag-list-inset";\n
    tag.appendChild(group);\n
\n
    return tag;\n
  }\n
\n
  // creates a set of autocomplete suggestings. Currently this is only a plain\n
  // list of elements. The list will display the number of results (>10 or \n
  // exact). Clicking on an option will set this option as field value\n
  function createResults(my_result_list, index) {\n
    var list = document.createElement("ul"),\n
      head = document.createElement("li"),\n
      str = "ui-li-static ui-body-inherit ui-icon-mail-forward " +\n
        "ui-btn-icon-right",\n
      len = my_result_list.length,\n
      prefix = "",\n
      item,\n
      value_dict,\n
      result,\n
      i;\n
\n
    if (len === 11) {\n
      prefix = ">";\n
      len = 10;\n
    }\n
\n
    head.className = "ui-autocomplete ui-li ui-li-divider ui-bar-inherit";\n
    head.setAttribute("role", "heading");\n
    head.textContent = prefix + " " + len + " Result(s)";\n
    list.appendChild(head);\n
\n
    for (i = 0; i < len; i += 1) {\n
      result = my_result_list[i];\n
      value_dict = result.value;\n
      item = document.createElement("li");\n
      item.className = str;\n
\n
      // NOTE: gadget does not properties it gets here, so just concat\n
      // NOTE: if doing more complex UI, beware the textContent value won\'t\n
      // work, because currently it\'s used to retrieve the link from\n
      // the last autocomplete query results!\n
      item.textContent = value_dict[index];\n
      item.setAttribute("data-relative-url", result.id);\n
      item.setAttribute("name", value_dict.uid);\n
      list.appendChild(item);\n
    }\n
\n
    list.className = "ui-listview ui-corner-all";\n
    list.firstChild.className += " ui-first-child";\n
    list.lastChild.className += " ui-last-child";\n
\n
    return list;\n
  }\n
\n
  ////////////////////////////////////\n
  // Promise methods\n
  ////////////////////////////////////\n
\n
  // notify change of field value, done here, since called from multiple sources\n
  function notifyChange(my_gadget) {\n
    return RSVP.all([\n
      my_gadget.checkValidity(),\n
      my_gadget.notifyChange()\n
    ]);\n
  }\n
\n
\n
\n
\n
  function createSingleRelationField(gadget, i, allow_jump) {\n
    var div_input = document.createElement("div"),\n
      wrapper = document.createElement("div"),\n
      fieldset = document.createElement("fieldset"),\n
      a1 = document.createElement("a"),\n
      a2 = document.createElement("a"),\n
      field_json = gadget.props.field_json,\n
      value = field_json.value || field_json.default,\n
      input = document.createElement("input");\n
    //create element\n
    wrapper.setAttribute("class", "sub" + field_json.key + "_" + i);\n
    div_input.setAttribute("class", "ui-input-text ui-body-inherit ui-corner-all ui-shadow-inset ui-input-has-clear ui-input-has-icon");\n
    input.setAttribute("type", "text");\n
    input.setAttribute("autocomplete", "off");\n
    input.setAttribute("data-enhanced", "true");\n
    a1.setAttribute("herf", "#");\n
    a1.setAttribute("tabindex", "-1");\n
    a1.setAttribute("class", "ui-hidden-accessible");\n
    a1.innerText = "&nbsp;";\n
\n
    a2.setAttribute("herf", "#");\n
    a2.setAttribute("tabindex", "-1");\n
    a2.setAttribute("class", "ui-btn ui-corner-all ui-btn-icon-notext ui-icon-plane ui-shadow-inset ui-btn-inline ui-disabled");\n
    a2.innerText = "Jump to this document";\n
\n
    div_input.appendChild(input);\n
    div_input.appendChild(a1);\n
    wrapper.appendChild(div_input);\n
    wrapper.appendChild(a2);\n
    fieldset.appendChild(wrapper);\n
    gadget.props.element.querySelector(".div_field").appendChild(fieldset);\n
\n
    //initialize\n
    input.setAttribute(\'value\', value[i] || "");\n
    input.setAttribute(\'name\', "sub" + field_json.key + "_" + i);\n
    if (field_json.editable !== 1) {\n
      input.setAttribute(\'readonly\', \'readonly\');\n
      div_input.className += \' ui-state-readonly \';\n
    }\n
    if (field_json.allow_jump && allow_jump) {\n
      return new RSVP.Queue()\n
        .push(function () {\n
          return gadget.getUrlFor({\n
            command: \'index\',\n
            options: {\n
              jio_key: field_json.relation_item_relative_url[i]\n
            }\n
          });\n
        })\n
        .push(function (my_url) {\n
          a2.href = my_url;\n
          a2.className = "ui-btn ui-corner-all ui-btn-icon-notext " +\n
            "ui-icon-plane ui-shadow-inset ui-btn-inline";\n
        });\n
    }\n
  }\n
\n
  rJS(window)\n
\n
    /////////////////////////////////////////////////////////////////\n
    // ready\n
    /////////////////////////////////////////////////////////////////\n
    // Init local properties\n
    .ready(function (my_gadget) {\n
      return my_gadget.getElement()\n
        .push(function (element) {\n
          my_gadget.props = {};\n
          my_gadget.props.pending_promise_list = [];\n
          my_gadget.props.select_uid_list = [];\n
          my_gadget.props.element = element;\n
        });\n
    })\n
    /////////////////////////////////////////////////////////////////\n
    // acquired methods\n
    /////////////////////////////////////////////////////////////////\n
    .declareAcquiredMethod("notifyValid", "notifyValid")\n
    .declareAcquiredMethod("notifyInvalid", "notifyInvalid")\n
    .declareAcquiredMethod("notifyChange", "notifyChange")\n
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")\n
    .declareAcquiredMethod("translateHtml", "translateHtml")\n
    .declareAcquiredMethod("getUrlFor", "getUrlFor")\n
    /////////////////////////////////////////////////////////////////\n
    // declared methods\n
    /////////////////////////////////////////////////////////////////\n
    .declareMethod(\'render\', function (options) {\n
      var gadget = this,\n
        i,\n
        url_list = options.field_json.relation_item_relative_url,\n
        value_list = options.field_json.value || options.field_json.default;\n
      gadget.props.field_json = options.field_json || {};\n
      for (i = 0; i < value_list.length && url_list !== undefined && url_list[i] !== undefined; i += 1) {\n
        gadget.props.select_uid_list[i] = options.field_json.relation_item_uid[i];\n
        createSingleRelationField(gadget, i, true);\n
      }\n
      if (options.field_json.editable === 1) {\n
        createSingleRelationField(gadget, i, false);\n
        gadget.props.relation_field_number = i;\n
      }\n
    })\n
    // get content (needs hidden fields, too, when creating new records)\n
    .declareMethod(\'checkValidity\', function () {\n
      return true;\n
    })\n
    .declareMethod(\'getContent\', function () {\n
      var field_json = this.props.field_json,\n
        input_list = this.props.element.querySelectorAll(\'input\'),\n
        result = {},\n
        i,\n
        value = "",\n
        i_len,\n
        input;\n
\n
      for (i = 0, i_len = input_list.length; i < i_len; i += 1) {\n
        input = input_list[i];\n
        if (input.value !== "") {\n
          value = value + input.value + "\\n";\n
          result[this.props.field_json.relation_field_id + "_" + i] = this.props.select_uid_list[i];\n
        }\n
      }\n
      result[field_json.key] = value;\n
      return result;\n
    })\n
\n
    /////////////////////////////////////////////////////////////////\n
    // declared services\n
    /////////////////////////////////////////////////////////////////\n
    .declareService(function () {\n
      var gadget = this,\n
        i,\n
        index_list,\n
        createEmptyField,\n
        triggerAutocomplete,\n
        stop,\n
        handler,\n
        element_list = gadget.props.element.querySelectorAll(\'input\');\n
\n
       // trigger autocomplete for field value, on render() with value only sets link\n
      triggerAutocomplete = function (my_gadget, my_event, i) {\n
        var props = my_gadget.props,\n
          field_json = props.field_json,\n
          index = field_json.catalog_index,\n
          begin_from = props.begin_from || 0,\n
          lines = field_json.lines || 11,\n
          select_list = [index, "uid"],\n
          query_string = " AND (" + index + \':"\' + my_event.target.value + \'")\',\n
          result_dict,\n
          tag_list,\n
          spin,\n
          target_div = my_gadget.props.element.querySelector("." + my_event.target.name),\n
          wrapper = target_div.querySelector("div.ui-input-text"),\n
          no_results;\n
\n
        spin = target_div.querySelector(".ui-hidden-accessible");\n
        return new RSVP.Queue()\n
          .push(function () {\n
            clearResults(wrapper);\n
            spin.className = "ui-btn ui-corner-all ui-btn-icon-notext" +\n
              " ui-input-clear ui-icon-spinner ui-icon-spin";\n
            return my_gadget.jio_allDocs({\n
              "query": new URI(field_json.query).query(true).query + query_string,\n
              "limit": [begin_from, begin_from + lines],\n
              "select_list": select_list\n
            });\n
          }).push(function (my_result) {\n
            result_dict = my_result.data;\n
            spin.className = "ui-hidden-accessible";\n
            no_results = result_dict.total_rows === 0;\n
\n
            // show "new" tag, clicking it will remove it and reset the field!\n
            // XXX Not active - reset should be handled by a generic reset method!\n
            if (no_results && field_json.allow_creation) {\n
              return new RSVP.Queue()\n
                .push(function () {\n
                  wrapper.appendChild(createNewTag(my_gadget, i));\n
                  return notifyChange(my_gadget);\n
                })\n
                .push(function () {\n
                  var tag = wrapper.querySelector(".ui-tag-list .ui-btn");\n
                  if (i === gadget.props.relation_field_number) {\n
                    createEmptyField();\n
                  }\n
                  return RSVP.any([\n
                    promiseEventListener(tag, "click", true),\n
                    promiseEventListener(tag, "tap", true)\n
                  ]);\n
                })\n
                .push(function (my_event_to_clear) {\n
                  my_event_to_clear.preventDefault();\n
                  wrapper.querySelector("input").value = my_event.target.defaultValue;\n
                  tag_list = wrapper.querySelector(".ui-tag-list");\n
                  tag_list.parentNode.removeChild(tag_list);\n
                  if (my_event.target.defaultValue !== "") {\n
                    wrapper.parentElement.lastChild.className = "ui-btn ui-corner-all ui-btn-icon-notext " +\n
                      "ui-icon-plane ui-shadow-inset ui-btn-inline";\n
                  }\n
                });\n
            }\n
            // have element\n
            return new RSVP.Queue()\n
              .push(function () {\n
                var list;\n
\n
                if (no_results === false) {\n
                  wrapper.appendChild(createResults(result_dict.rows, index));\n
                  list = wrapper.querySelector("ul");\n
\n
                  return RSVP.any([\n
                    promiseEventListener(list, "click", true),\n
                    promiseEventListener(list, "touchend", true)\n
                  ]);\n
                }\n
              });\n
\n
          }).push(undefined, function (my_error) {\n
            if (my_error instanceof RSVP.CancellationError) {\n
              spin.className = "ui-hidden-accessible";\n
              clearResults(my_gadget, "skip");\n
            }\n
            throw my_error;\n
          }).push(function (my_selection_event) {\n
            var element,\n
              jump_url;\n
\n
            // take entered text, set to input and clear list options\n
            if (my_selection_event && my_selection_event.target) {\n
              element = my_selection_event.target;\n
              jump_url = element.getAttribute("data-relative-url");\n
              props.select_uid_list[i] = element.getAttribute("name");\n
              wrapper.querySelector("input").value = element.textContent;\n
              clearResults(wrapper, "skip");\n
              return my_gadget.getUrlFor({\n
                command: \'index\',\n
                options: {\n
                  jio_key: jump_url\n
                }\n
              });\n
            }\n
          }).push(function (my_url) {\n
            if (my_url !== undefined) {\n
              wrapper.parentElement.lastChild.href = my_url;\n
              wrapper.parentElement.lastChild.className = "ui-btn ui-corner-all ui-btn-icon-notext " +\n
                "ui-icon-plane ui-shadow-inset ui-btn-inline";\n
              if (i === gadget.props.relation_field_number) {\n
                createEmptyField();\n
              }\n
            }\n
          });\n
      };\n
\n
      stop = function (e) {\n
        e.preventDefault();\n
        return false;\n
      };\n
\n
      handler = function (my_event) {\n
        var value = my_event.target.value,\n
          pending_promise;\n
\n
        // field value unchanged (tab-bing)\n
        if (my_event.target.defaultValue === value) {\n
          return;\n
        }\n
\n
        // empty value, do nothing but notify\n
        if (value === "") {\n
          return notifyChange(gadget);\n
        }\n
        index_list = my_event.target.name.split("_");\n
        i = parseInt(index_list[index_list.length - 1], 10);\n
        // replace existing promise in case it has not triggered\n
        pending_promise = gadget.props.pending_promise_list[i];\n
        if (pending_promise) {\n
          pending_promise.cancel();\n
        }\n
\n
        // create a new queue, expose it to replace it with trailing events\n
        pending_promise = new RSVP.Queue()\n
          .push(function () {\n
            return RSVP.delay(200);\n
          })\n
          .push(function () {\n
            return triggerAutocomplete(gadget, my_event, i);\n
          });\n
\n
        gadget.props.pending_promise_list[i] = pending_promise;\n
        return pending_promise;\n
      };\n
\n
      createEmptyField = function () {\n
        var new_input;\n
        gadget.props.relation_field_number += 1;\n
        createSingleRelationField(gadget, gadget.props.relation_field_number, false);\n
        element_list = gadget.props.element.querySelectorAll(\'input\');\n
        new_input = element_list[element_list.length - 1];\n
        loopEventListener(new_input, \'onmouseout\', false, stop);\n
        loopEventListener(new_input, \'keyup\', false, handler);\n
        loopEventListener(new_input, \'input\', false, handler);\n
      };\n
\n
      // Listen to all necessary events (blur not needed currently)\n
      for (i = 0; i < element_list.length; i += 1) {\n
        loopEventListener(element_list[i], \'onmouseout\', false, stop);\n
        loopEventListener(element_list[i], \'keyup\', false, handler);\n
        loopEventListener(element_list[i], \'input\', false, handler);\n
      }\n
    });\n
}(window, document, rJS, RSVP, URI, loopEventListener, promiseEventListener));

]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Gadget ERP5 MultiRelationstringfield JS</string> </value>
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
                <value> <string>xiaowu</string> </value>
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
                        <float>1432174100.69</float>
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
                <value> <string>948.41913.14733.35481</string> </value>
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
                        <float>1453478150.45</float>
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
                <value> <string>xiaowu</string> </value>
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
                        <float>1432174063.33</float>
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
