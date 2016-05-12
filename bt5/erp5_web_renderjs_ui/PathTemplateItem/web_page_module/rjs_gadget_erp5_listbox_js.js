/*jslint indent: 2, maxerr: 3, nomen: true */
/*global window, document, rJS, URI, RSVP, loopEventListener,
  SimpleQuery, ComplexQuery, Query, Handlebars, console, QueryFactory*/
(function (window, document, rJS, URI, RSVP, loopEventListener,
  SimpleQuery, ComplexQuery, Query, Handlebars, console, QueryFactory) {
  "use strict";
  var gadget_klass = rJS(window),
    listbox_hidden_thead_source = gadget_klass.__template_element
                         .getElementById("listbox-hidden-thead-template")
                         .innerHTML,
    listbox_hidden_thead_template = Handlebars.compile(listbox_hidden_thead_source),
    listbox_show_thead_source = gadget_klass.__template_element
                         .getElementById("listbox-show-thead-template")
                         .innerHTML,
    listbox_show_thead_template = Handlebars.compile(listbox_show_thead_source),

    listbox_hidden_tbody_source = gadget_klass.__template_element
                         .getElementById("listbox-hidden-tbody-template")
                         .innerHTML,
    listbox_hidden_tbody_template = Handlebars.compile(listbox_hidden_tbody_source),
    listbox_show_tbody_source = gadget_klass.__template_element
                         .getElementById("listbox-show-tbody-template")
                         .innerHTML,
    listbox_show_tbody_template = Handlebars.compile(listbox_show_tbody_source),

    listbox_tfoot_source = gadget_klass.__template_element
                         .getElementById("listbox-tfoot-template")
                         .innerHTML,
    listbox_tfoot_template = Handlebars.compile(listbox_tfoot_source),

    listbox_source = gadget_klass.__template_element
                         .getElementById("listbox-template")
                         .innerHTML,
    listbox_template = Handlebars.compile(listbox_source),

    error_message_source = gadget_klass.__template_element
                         .getElementById("error-message-template")
                         .innerHTML,
    error_message_template = Handlebars.compile(error_message_source);


  function renderListboxThead(gadget, template) {
    if (template === undefined) {
      template = listbox_hidden_thead_template;
    }
    return gadget.translateHtml(template(
      {
        "head_value": gadget.props.head_value,
        "show_anchor": gadget.props.field_json.show_anchor,
        "line_icon": gadget.props.field_json.line_icon
      }
    ));
  }



  function renderEditableField(gadget, element) {
    var i,
      promise_list = [],
      uid_value_dict = {},
      uid_value,
      column,
      line,
      element_list = element.querySelectorAll(".editable_div");
    gadget.props.listbox_uid_dict = {};
    gadget.props.cell_gadget_list = [];
    function renderSubCell(element, sub_field_json) {
      var options = {},
        queue;
      sub_field_json.editable = sub_field_json.editable && gadget.props.field_json.editable; // XXX 
      queue = gadget.getFieldTypeGadgetUrl(sub_field_json.type);
      queue
        .push(function (gadget_url) {
          if (sub_field_json.editable) {
            options = {
              element: element
            };
          }
          return gadget.declareGadget(gadget_url, options);
        })
        .push(function (cell_gadget) {
          if (sub_field_json.editable) {
            gadget.props.cell_gadget_list.push(cell_gadget);
          } else {
            if (cell_gadget.getTextContent) {
              queue
                .push(function () {
                  return cell_gadget.getTextContent();
                })
                .push(function (text_content) {
                  var text = document.createTextNode(text_content);
                  element.appendChild(text);
                });
            } else {
              queue
                .push(function () {
                  return cell_gadget.getElement();
                })
                .push(function (cell_element) {
                  element.appendChild(cell_element);
                });
            }
          }
          return cell_gadget.render({field_json: sub_field_json});
        });
      return queue;
    }
    for (i = 0; i < element_list.length; i += 1) {
      column = element_list[i].getAttribute("column");
      line = element_list[i].getAttribute("line");
      if (gadget.props.listbox_uid_dict.key === undefined) {
        gadget.props.listbox_uid_dict.key = gadget.props.result.data.rows[line].value["listbox_uid:list"].key;
        gadget.props.listbox_uid_dict.value = [gadget.props.result.data.rows[line].value["listbox_uid:list"].value];
        uid_value_dict[gadget.props.result.data.rows[line].value["listbox_uid:list"].value] = null;
      } else {
        uid_value = gadget.props.result.data.rows[line].value["listbox_uid:list"].value;
        if (!uid_value_dict.hasOwnProperty(uid_value)) {
          uid_value_dict[uid_value] = null;
          gadget.props.listbox_uid_dict.value.push(uid_value);
        }
      }
      promise_list.push(renderSubCell(element_list[i],
        gadget.props.result.data.rows[line].value[gadget.props.field_json.column_list[column][0]] || ""));
    }
    return RSVP.all(promise_list);
  }

  function renderListboxTbody(gadget, template) {
    var tmp;
    if (template === undefined) {
      template = listbox_hidden_tbody_template;
    }

    return gadget.translateHtml(template(
      {
        "body_value": gadget.props.body_value,
        "show_anchor": gadget.props.field_json.show_anchor,
        "column_list": gadget.props.field_json.column_list
      }
    ))
      .push(function (my_html) {
        tmp = document.createElement("tbody");
        tmp.innerHTML = my_html;
        return renderEditableField(gadget, tmp);
      })
      .push(function () {
        var table =  gadget.props.element.querySelector("table"),
          tbody = table.querySelector("tbody");
        table.removeChild(tbody);
        table.appendChild(tmp);
      });
  }

  function renderListboxTfoot(gadget) {
    return gadget.translateHtml(listbox_tfoot_template(
      {
        "colspan": gadget.props.foot.colspan,
        "previous_classname": gadget.props.foot.previous_classname,
        "previous_url": gadget.props.foot.previous_url,
        "record": gadget.props.foot.record,
        "next_classname": gadget.props.foot.next_classname,
        "next_url": gadget.props.foot.next_url
      }
    ));
  }


  function renderListbox(gadget) {
    return gadget.translateHtml(listbox_template(
      {
        "hide_class": gadget.props.hide_class,
        "hide_sort": gadget.props.hide_sort,
        "title": gadget.props.field_json.title
      }
    ));
  }


  function renderErrorMessage(gadget) {
    var options = {};
    options.extended_search = undefined;
    options[gadget.props.field_json.key + "_sort_list:json"] = undefined;
    return gadget.getUrlFor({
      command: 'store_and_change',
      options: options
    })
      .push(function (url) {
        return gadget.translateHtml(error_message_template(
          {
            'reset_url' : url
          }
        ));
      });
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {
        cell_gadget_list: [],
        listbox_uid_dict: {}
      };
    })

    // Assign the element to a variable
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })

    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("getFieldTypeGadgetUrl", "getFieldTypeGadgetUrl")
    .declareAcquiredMethod("renderEditorPanel", "renderEditorPanel")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("translate", "translate")
    //////////////////////////////////////////////
    // initialize the gadget content
    //////////////////////////////////////////////
    .declareMethod('render', function (options) {
      var gadget = this,
        field_json = options.field_json,
        head_value = [],
        class_value,
        tmp,
        i,
        j;

      gadget.props.field_json = field_json;
      gadget.props.field_id = options.field_id;
      gadget.props.extended_search = options.extended_search;
      gadget.props.hide_class = options.hide_enabled ? "" : "ui-disabled";
      gadget.props.sort_list = [];
      gadget.props.command = field_json.command || 'index';

      //only display which is in listbox's column list
      if (field_json.sort_column_list.length) {
        field_json.sort_column_list = field_json.sort_column_list.filter(function (n) {
          for (i = 0; i < field_json.column_list.length; i += 1) {
            if (field_json.column_list[i][0] === n[0] && field_json.column_list[i][1] === n[1]) {
              return true;
            }
          }
          return false;
        });
      }
      gadget.props.hide_sort = field_json.sort_column_list.length ? "" : "ui-disabled";

      if (field_json.search_column_list.length) {
        field_json.search_column_list = field_json.search_column_list.filter(function (n) {
          for (i = 0; i < field_json.column_list.length; i += 1) {
            if (field_json.column_list[i][0] === n[0] && field_json.column_list[i][1] === n[1]) {
              return true;
            }
          }
          return false;
        });
      }
      field_json.search_column_list.push(["searchable_text", "Searchable Text"]);

      return new RSVP.Queue()
        .push(function () {
          return renderListbox(gadget);
        })
        .push(function (my_html) {
          gadget.props.element.querySelector(".document_table").innerHTML = my_html;
          // XXX Fix in case of multiple listboxes
          return RSVP.all([
            gadget.getUrlParameter(field_json.key + '_begin_from'),
            gadget.getUrlParameter(field_json.key + '_sort_list:json')
          ]);
        })
        .push(function (all_result) {
          var result = all_result[0];
          gadget.props.sort_list = all_result[1] || [];
          if (result === undefined) {
            result = '0';
          }
          for (i = 0; i < gadget.props.field_json.column_list.length; i += 1) {
            class_value = "";
            for (j = 0; j < gadget.props.sort_list.length; j += 1) {
              tmp = gadget.props.sort_list[j];
              if (tmp[0] === gadget.props.field_json.column_list[i][0]) {
                if (tmp[1] === "ascending") {
                  class_value = "ui-icon-arrow-up";
                } else {
                  class_value = "ui-icon-arrow-down";
                }
                break;
              }
            }
            head_value.push({
              "data-i18n": field_json.column_list[i][1],
              "class_value": class_value,
              "text": field_json.column_list[i][1]
            });
          }
          gadget.props.head_value = head_value;
          gadget.props.begin_from = parseInt(result, 10) || 0;
          return renderListboxThead(gadget);
        })
        .push(function (my_html) {
          gadget.props.element.querySelector(".thead").innerHTML = my_html;
        });
    })
    .declareMethod('getListboxInfo', function () {
      //XXXXX search column list is used for search editor to
      //construct search panel
      //hardcoded begin_from key to define search position
      return { "search_column_list": this.props.field_json.search_column_list,
               "begin_from": this.props.field_json.key + "_begin_from"};
    })

    //////////////////////////////////////////////
    // render the listbox in an asynchronous way
    //////////////////////////////////////////////
    .declareService(function () {
      var gadget = this,
        props = gadget.props,
        field_json = props.field_json,
        begin_from = props.begin_from,
        url_query =  props.extended_search,
        query_string = new URI(field_json.query).query(true).query,
        lines = field_json.lines,
        select_list = [],
        dataset,
        counter,
        limit_options,
        queue,
        i;

      if (field_json.query === undefined) {
        gadget.props.element.querySelector('tfoot').textContent = "Unsupported list method: '" + field_json.list_method + "'";
        return;
      }
     // function buildQueryString(previous, next) {
     //   return previous + next[0] + ':= "' + url_query + '" OR ';
     // }

      if (url_query) {
        //query_string = field_json.column_list.reduce(buildQueryString, ' AND (').replace(new RegExp("OR " + '$'), ')');
        if (query_string) {
          query_string = '(' + query_string + ') AND (' + url_query + ')';
        } else {
          query_string = url_query;
        }
      }

      for (i = 0; i < field_json.column_list.length; i += 1) {
        select_list.push(field_json.column_list[i][0]);
      }
      select_list.push("uid");
      if (lines === 0) {
        limit_options = undefined;
      } else {
        limit_options = [begin_from, lines + 1];
      }
      queue = gadget.jio_allDocs({
        // XXX Not jIO compatible, but until a better api is found...
        "list_method_template": field_json.list_method_template,
        "query": query_string,
        "limit": limit_options,
        "select_list": select_list,
        "sort_on": gadget.props.sort_list
      });
      queue
        .push(undefined, function (error) {
          //XXXXX hack to not crash interface
          //this will catch all error, not only search criteria invalid error
          console.warn(error);
          return renderErrorMessage(gadget)
            .push(function (error_html) {
              gadget.props.element.querySelector(".document_table").innerHTML = error_html;
              queue.cancel();
            });
        })
        .push(function (result) {
          var promise_list = [result];
          if (lines === 0) {
            lines =  result.data.total_rows;
            counter = result.data.total_rows;
          } else {
            counter = Math.min(result.data.total_rows, lines);
          }
          for (i = 0; i < counter; i += 1) {
            promise_list.push(
              gadget.getUrlFor({
                command: gadget.props.command,
                options: {
                  jio_key: result.data.rows[i].id,
                  uid: result.data.rows[i].value.uid,
                  selection_index: begin_from + i,
                  query: query_string,
                  list_method_template: field_json.list_method_template,
                  "sort_list:json": gadget.props.sort_list
                }
              })
            );
          }
          return RSVP.all(promise_list);

        }).push(function (result_list) {
          var j,
            result = result_list[0],
            value,
            body_value = [],
            tr_value = [],
            tmp_url;
          dataset = result;
          for (i = 0; i < counter; i += 1) {
            tmp_url = result_list[i + 1];
            tr_value = [];
            for (j = 0; j < field_json.column_list.length; j += 1) {
              value = result.data.rows[i].value[field_json.column_list[j][0]] || "";
              tr_value.push({
                "type": value.type,
                "editable": value.editable && field_json.editable,
                "href": tmp_url,
                "text": value,
                "line": i,
                "column": j
              });
            }
            body_value.push({
              "value": result.data.rows[i].value.uid,
              "jump": tmp_url,
              "tr_value": tr_value,
              "line_icon": field_json.line_icon
            });
          }
          gadget.props.body_value = body_value;
          gadget.props.result = result;
          return renderListboxTbody(gadget);
        }).push(function () {
          var prev_param = {},
            next_param = {};
          function setNext() {
            if (dataset.data.rows.length > lines) {
              next_param[gadget.props.field_json.key + '_begin_from'] = begin_from + lines;
            }
          }

          if (begin_from === 0) {
            setNext();
          } else {
            prev_param[gadget.props.field_json.key + '_begin_from'] = begin_from - lines;
            setNext();
          }
          return RSVP.all([
            gadget.getUrlFor({command: 'change', options: prev_param}),
            gadget.getUrlFor({command: 'change', options: next_param})
          ]);

        }).push(function (url_list) {
          var foot = {};
          foot.colspan = field_json.column_list.length + field_json.show_anchor + 
            (field_json.line_icon? 1 : 0);
          foot.default_colspan = foot.colspan;
          foot.previous_classname = "ui-btn ui-icon-carat-l ui-btn-icon-left responsive ui-first-child";
          foot.previous_url = url_list[0];
          foot.next_classname = "ui-btn ui-icon-carat-r ui-btn-icon-right responsive ui-last-child";
          foot.next_url = url_list[1];
          if ((begin_from === 0) && (counter === 0)) {
            foot.record = "No records";
          } else if ((dataset.data.rows.length <= lines) && (begin_from === 0)) {
            foot.record = counter + " Records";
          } else {
            foot.record = "Records " + (((begin_from + lines) / lines - 1) * lines + 1) + " - " + (((begin_from + lines) / lines - 1) * lines + counter);
          }

          if (begin_from === 0) {
            foot.previous_classname += " ui-disabled";
          }
          if (dataset.data.rows.length <= lines) {
            foot.next_classname += " ui-disabled";
          }
          gadget.props.foot = foot;
          return renderListboxTfoot(gadget);
        }).push(function (my_html) {
          gadget.props.element.querySelector(".tfoot").innerHTML = my_html;
        });
      return queue;
    })


    .declareMethod("getContent", function (format) {
      var form_gadget = this,
        k,
        field_gadget,
        count = form_gadget.props.cell_gadget_list.length,
        data = {},
        queue = new RSVP.Queue();

      function extendData(field_data) {
        var key;
        for (key in field_data) {
          if (field_data.hasOwnProperty(key)) {
            data[key] = field_data[key];
          }
        }
      }

      for (k = 0; k < count; k += 1) {
        field_gadget = form_gadget.props.cell_gadget_list[k];
        // XXX Hack until better defined
        if (field_gadget.getContent !== undefined) {
          queue
            .push(field_gadget.getContent.bind(field_gadget, format))
            .push(extendData);
        }
      }
      return queue
        .push(function () {
          data[form_gadget.props.listbox_uid_dict.key] = form_gadget.props.listbox_uid_dict.value;
          return data;
        });
    })
    .declareService(function () {
      var gadget = this,
        url,
        options = {},
        sort_button = gadget.props.element.querySelector('button[name="Sort"]');
      return loopEventListener(
        sort_button,
        "click",
        false,
        function () {
          url = "gadget_erp5_sort_editor.html";
          options.sort_column_list = gadget.props.field_json.sort_column_list;
          options.sort_list = gadget.props.sort_list;
          options.key = gadget.props.field_json.key + "_sort_list:json";
          return gadget.renderEditorPanel(url, options);
        }
      );
    })
    .declareService(function () {
      var gadget = this,
        hide_button = gadget.props.element.querySelector('button[name="Hide"]');
      return loopEventListener(
        hide_button,
        "click",
        false,
        function () {
          return new RSVP.Queue()
            .push(function () {
              var i,
                all_hide_elements,
                query_list = [],
                search_query,
                thead_template,
                tbody_template,
                hide_button_html,
                hide_elements = [];
              if (gadget.props.foot.colspan === gadget.props.foot.default_colspan) {
                thead_template = listbox_show_thead_template;
                tbody_template = listbox_show_tbody_template;
                hide_button_html = "Submit";
                gadget.props.foot.colspan += 1;
              } else {
                //hide closed
                //maybe submit
                all_hide_elements = gadget.props.element.querySelectorAll(".hide_element");
                for (i = 0; i < all_hide_elements.length; i += 1) {
                  if (!all_hide_elements[i].checked) {
                    hide_elements.push(all_hide_elements[i]);
                  }
                }
                if (hide_elements.length) {
                  for (i = 0; i < hide_elements.length; i += 1) {
                    query_list.push(new SimpleQuery({
                      key: "catalog.uid",
                      type: "simple",
                      operator: "!=",
                      value: hide_elements[i].getAttribute("value")
                    }));
                  }
                  if (gadget.props.extended_search) {
                    search_query = QueryFactory.create(gadget.props.extended_search);
                  }
                  if (search_query) {
                    query_list.push(search_query);
                  }
                  search_query = new ComplexQuery({
                    operator: "AND",
                    query_list: query_list,
                    type: "complex"
                  });

                  return gadget.redirect({
                    command: 'store_and_change',
                    options: {
                      "extended_search": Query.objectToSearchText(search_query)
                    }
                  });
                }

                gadget.props.foot.colspan -= 1;
                hide_button_html = "Hide Rows";
                thead_template = listbox_hidden_thead_template;
                tbody_template = listbox_hidden_tbody_template;
              }
              return RSVP.all([
                renderListboxThead(gadget, thead_template),
                renderListboxTbody(gadget, tbody_template),
                renderListboxTfoot(gadget, listbox_tfoot_template),
                gadget.translate(hide_button_html)
              ]);
            })
            .push(function (all_innerHTML) {
              //change hide button's text
              hide_button.innerHTML = all_innerHTML[3];
              gadget.props.element.querySelector(".thead").innerHTML = all_innerHTML[0];
              gadget.props.element.querySelector(".tfoot").innerHTML = all_innerHTML[2];
            });
        }
      );
    })

    .allowPublicAcquisition("notifyInvalid", function () {
      return;
    })

    .allowPublicAcquisition("notifyValid", function () {
      return;
    });

}(window, document, rJS, URI, RSVP, loopEventListener,
  SimpleQuery, ComplexQuery, Query, Handlebars, console, QueryFactory));