/*jslint indent: 2, maxerr: 3, nomen: true */
/*global window, document, rJS, URI, RSVP,
  SimpleQuery, ComplexQuery, Query, Handlebars, console, QueryFactory*/
(function (window, document, rJS, URI, RSVP,
  SimpleQuery, ComplexQuery, Query, Handlebars, console, QueryFactory) {
  "use strict";
  var gadget_klass = rJS(window),
    listbox_thead_source = gadget_klass.__template_element
                         .getElementById("listbox-thead-template")
                         .innerHTML,
    listbox_thead_template = Handlebars.compile(listbox_thead_source),

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
    error_message_template = Handlebars.compile(error_message_source),
    variable = {},
    loading_class_list = ['ui-icon-spinner', 'ui-btn-icon-left'],
    disabled_class = 'ui-disabled';


  function renderEditableField(gadget, element, column_list) {
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
      sub_field_json.editable = sub_field_json.editable && gadget.state.editable; // XXX 
      return gadget.getFieldTypeGadgetUrl(sub_field_json.type)
        .push(function (gadget_url) {
          return gadget.declareGadget(gadget_url, {element: element});
        })
        .push(function (cell_gadget) {
          gadget.props.cell_gadget_list.push(cell_gadget);
          return cell_gadget.render({field_json: sub_field_json});
        });
    }
    for (i = 0; i < element_list.length; i += 1) {
      column = element_list[i].getAttribute("column");
      line = element_list[i].getAttribute("line");
      if (gadget.props.listbox_uid_dict.key === undefined) {
        gadget.props.listbox_uid_dict.key = gadget.state.allDocs_result.data.rows[line].value["listbox_uid:list"].key;
        gadget.props.listbox_uid_dict.value = [gadget.state.allDocs_result.data.rows[line].value["listbox_uid:list"].value];
        uid_value_dict[gadget.state.allDocs_result.data.rows[line].value["listbox_uid:list"].value] = null;
      } else {
        uid_value = gadget.state.allDocs_result.data.rows[line].value["listbox_uid:list"].value;
        if (!uid_value_dict.hasOwnProperty(uid_value)) {
          uid_value_dict[uid_value] = null;
          gadget.props.listbox_uid_dict.value.push(uid_value);
        }
      }
      promise_list.push(renderSubCell(element_list[i],
        gadget.state.allDocs_result.data.rows[line].value[column_list[column][0]] || ""));
    }
    return RSVP.all(promise_list);
  }


  function renderListboxTbody(gadget, template, body_value) {
    var tmp,
      column_list = JSON.parse(gadget.state.column_list_json);

    return gadget.translateHtml(template(
      {
        "body_value": body_value,
        "show_anchor": gadget.state.show_anchor,
        "column_list": column_list
      }
    ))
      .push(function (my_html) {
        tmp = document.createElement("tbody");
        tmp.innerHTML = my_html;
        return renderEditableField(gadget, tmp, column_list);
      })
      .push(function () {
        var table =  gadget.element.querySelector("table"),
          tbody = table.querySelector("tbody");
        table.removeChild(tbody);
        table.appendChild(tmp);
      });
  }


  function renderListboxTfoot(gadget, foot) {
    return gadget.translateHtml(listbox_tfoot_template(
      {
        "colspan": foot.colspan,
        "previous_classname": foot.previous_classname,
        "previous_url": foot.previous_url,
        "record": foot.record,
        "next_classname": foot.next_classname,
        "next_url": foot.next_url
      }
    ));
  }

  /** Clojure to ease finding in lists of lists by the first item **/
  function hasSameFirstItem(a) {
    return function (b) {
      return a[0] === b[0];
    };
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function () {
      this.props = {
        cell_gadget_list: [],
        listbox_uid_dict: {}
      };
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
        i,
        sort_column_list = [],
        search_column_list = [],
        query_string,
        url_query,
        queue;

      /** Transform sort arguments (column_name, sort_direction) to jIO's "ascending" and "descending" **/
      function jioize_sort(column_sort) {
        if (column_sort[1].toLowerCase().startsWith('asc')) {
          return [column_sort[0], 'ascending'];
        }
        if (column_sort[1].toLowerCase().startsWith('desc')) {
          return [column_sort[0], 'descending'];
        }
        return column_sort;
      }

      /** Check whether item is in outer-scoped field_json.column_list */
      function is_in_column_list(item) {
        for (i = 0; i < field_json.column_list.length; i += 1) {
          if (field_json.column_list[i][0] === item[0] && field_json.column_list[i][1] === item[1]) {
            return true;
          }
        }
        return false;
      }

      // use only visible columns for sort
      if (field_json.sort_column_list.length) {
        sort_column_list = field_json.sort_column_list.filter(is_in_column_list);
      }

      // use only visible columns for search
      if (field_json.search_column_list.length) {
        search_column_list = field_json.search_column_list.filter(is_in_column_list);
      }
      search_column_list.push(["searchable_text", "Searchable Text"]);

      url_query = options.extended_search;
      query_string = new URI(field_json.query).query(true).query;
      if (url_query) {
        //query_string = field_json.column_list.reduce(buildQueryString, ' AND (').replace(new RegExp("OR " + '$'), ')');
        if (query_string) {
          query_string = '(' + query_string + ') AND (' + url_query + ')';
        } else {
          query_string = url_query;
        }
      }

      queue = RSVP.Queue();
      if (!variable.translated_records) {
        queue
          .push(function () {
            return RSVP.all([
              gadget.translate('Records'),
              gadget.translate('No records')
            ]);
          })
          .push(function (results) {
            variable.translated_records = results[0];
            variable.translated_no_record = results[1];
          });
      }
      queue
        .push(function () {
          // Cancel previous line rendering to not conflict with the asynchronous render for now
          return gadget.fetchLineContent(true);
        })
        .push(function () {
          // XXX Fix in case of multiple listboxes
          return RSVP.all([
            gadget.getUrlParameter(field_json.key + '_begin_from'),
            gadget.getUrlParameter(field_json.key + '_sort_list:json')
          ]);
        })
        .push(function (result_list) {
          return gadget.changeState({
            key: field_json.key,
            title: field_json.title,
            editable: field_json.editable,

            begin_from: parseInt(result_list[0] || '0', 10) || 0,

            // sorting is either specified in URL per listbox or we take default sorting from JSON's 'sort' attribute
            sort_list_json: JSON.stringify(result_list[1] || field_json.sort.map(jioize_sort)),

            show_anchor: field_json.show_anchor,
            line_icon: field_json.line_icon,
            query: field_json.query,
            query_string: query_string,
            lines: field_json.lines,
            list_method: field_json.list_method,
            list_method_template: field_json.list_method_template,

            column_list_json: JSON.stringify(field_json.column_list),

            sort_column_list_json: JSON.stringify(sort_column_list),
            search_column_list_json: JSON.stringify(search_column_list),
            hide_sort: field_json.sort_column_list.length ? "" : "ui-disabled",

            field_id: options.field_id,
            extended_search: options.extended_search,
            hide_class: options.hide_enabled ? "" : "ui-disabled",
            command: field_json.command || 'index',

            // Force line calculation in any case
            allDocs_result: undefined,

            // No error message
            has_error: false,
            show_line_selector: false
          });
        });
      return queue;
    })

    .onStateChange(function (modification_dict) {
      var gadget = this,
        sort_key = gadget.state.key + "_sort_list:json",
        sort_list,
        column_list,
        sort_column_list,
        i,
        j,
        result_queue = new RSVP.Queue();

/*
      if (modification_dict.hasOwnProperty('error_text') && this.state.error_text !== undefined) {
        // XXX TODO
        this.element.querySelector('tfoot').textContent =
          "Unsupported list method: '" + this.state.list_method + "'";
        loading_element_classList.remove.apply(loading_element_classList, loading_class_list);
        return;
      }
*/

      if (gadget.state.has_error) {
        return result_queue
          .push(function () {
            var options = {extended_search: undefined};
            options[sort_key] = undefined;
            return gadget.getUrlFor({
              command: 'store_and_change',
              options: options
            });
          })
          .push(function (url) {
            return gadget.translateHtml(error_message_template({
              reset_url: url
            }));
          })
          .push(function (html) {
            gadget.element.querySelector(".document_table").innerHTML = html;
          });
      }



      if ((modification_dict.hasOwnProperty('sort_list_json')) ||
          (modification_dict.hasOwnProperty('column_list_json')) ||
          (modification_dict.hasOwnProperty('title')) ||
          (modification_dict.hasOwnProperty('has_error')) ||
          (modification_dict.hasOwnProperty('show_line_selector')) ||
          (modification_dict.hasOwnProperty('hide_sort')) ||
          (modification_dict.hasOwnProperty('hide_class')) ||
          (modification_dict.hasOwnProperty('extended_search'))) {

        // display sorting arrow inside correct columns
        sort_list = JSON.parse(gadget.state.sort_list_json);  // current sort
        column_list = JSON.parse(gadget.state.column_list_json);  // shown columns
        sort_column_list = JSON.parse(gadget.state.sort_column_list_json); // sortable columns

        result_queue
          .push(function () {
            // construct array of links for sortable columns, undefined otherwise
            return RSVP.all(column_list.map(function (column) {

              var is_sortable = sort_column_list.find(hasSameFirstItem(column)) !== undefined,
                current_sort = sort_list.find(hasSameFirstItem(column)),
                options = {};

              if (is_sortable) {
                options[sort_key] = [[column[0], 'descending']];  // make it the only new sort (replace array instead of push)
                if (current_sort !== undefined && current_sort[1] === 'descending') {
                  options[sort_key] = [[column[0], 'ascending']];
                }
                return gadget.getUrlFor({"command": 'store_and_change', "options": options});
              }
              return undefined;
            }));
          })
          .push(function (column_sort_link_list) {
            // here we obtain links for sorting by columns
            // so we can construct array of header objects to be rendered in the header template
            var hide_button_text,
              hide_button_name,
              head_value_list = column_list.map(function (column, index) {
                var current_sort = sort_list.find(hasSameFirstItem(column)),
                  class_value = "";

                if (current_sort !== undefined) {
                  if (current_sort[1] === 'ascending') {
                    class_value = "ui-icon ui-icon-arrow-up";
                  }
                  if (current_sort[1] === 'descending') {
                    class_value = "ui-icon ui-icon-arrow-down";
                  }
                }

                return {
                  "data-i18n": column[1],
                  "class_value": class_value,
                  "sort_link": column_sort_link_list[index],
                  "text": column[1]
                };
              });

            if (gadget.state.show_line_selector) {
              hide_button_text = 'Submit';
              hide_button_name = 'SelectRows';
            } else {
              hide_button_text = 'Hide Rows';
              hide_button_name = 'Hide';
            }
            return RSVP.all([
              gadget.translateHtml(listbox_template({
                hide_class: gadget.state.hide_class,
                hide_sort: gadget.state.hide_sort,
                title: gadget.state.title,
                hide_button_text: hide_button_text,
                hide_button_name: hide_button_name
              })),
              gadget.translateHtml(listbox_thead_template({
                head_value: head_value_list,
                show_anchor: gadget.state.show_anchor,
                line_icon: gadget.state.line_icon
              }))
            ]);
          })
          .push(function (result_list) {
            gadget.element.querySelector(".document_table").innerHTML = result_list[0];
            gadget.element.querySelector(".thead").innerHTML = result_list[1];
          });
      }

      if (gadget.state.allDocs_result === undefined) {
        // Trigger line content calculation
        result_queue
          .push(function () {
            var loading_element_classList = gadget.element.querySelector(".listboxloader").classList,
              tbody_classList = gadget.element.querySelector("table").querySelector("tbody").classList;
            // Set the loading icon and trigger line calculation
            loading_element_classList.add.apply(loading_element_classList, loading_class_list);
            tbody_classList.add(disabled_class);

            return gadget.fetchLineContent(false);
          });

      } else if ((modification_dict.hasOwnProperty('show_line_selector')) ||
          (modification_dict.hasOwnProperty('allDocs_result'))) {

        // Render the listbox content
        result_queue
          .push(function () {
            var lines = gadget.state.lines,
              promise_list = [],
              allDocs_result = gadget.state.allDocs_result,
              counter;

            column_list = JSON.parse(gadget.state.column_list_json);

            if (lines === 0) {
              lines = allDocs_result.data.total_rows;
              counter = allDocs_result.data.total_rows;
            } else {
              counter = Math.min(allDocs_result.data.total_rows, lines);
            }
            sort_list = JSON.parse(gadget.state.sort_list_json);

            for (i = 0; i < counter; i += 1) {
              promise_list.push(
                gadget.getUrlFor({
                  command: gadget.state.command,
                  options: {
                    jio_key: allDocs_result.data.rows[i].id,
                    uid: allDocs_result.data.rows[i].value.uid,
                    selection_index: gadget.state.begin_from + i,
                    query: gadget.state.query_string,
                    list_method_template: gadget.state.list_method_template,
                    "sort_list:json": sort_list
                  }
                })
              );
            }
            return new RSVP.Queue()
              .push(function () {
                return RSVP.all(promise_list);
              })

              .push(function (result_list) {
                var value,
                  body_value = [],
                  tr_value = [],
                  tmp_url,
                  listbox_tbody_template;

                for (i = 0; i < counter; i += 1) {
                  tmp_url = result_list[i];
                  tr_value = [];
                  for (j = 0; j < column_list.length; j += 1) {
                    value = allDocs_result.data.rows[i].value[column_list[j][0]] || "";
                    tr_value.push({
                      "type": value.type,
                      "editable": value.editable && gadget.state.editable,
                      "href": tmp_url,
                      "text": value,
                      "line": i,
                      "column": j
                    });
                  }
                  body_value.push({
                    "value": allDocs_result.data.rows[i].value.uid,
                    "jump": tmp_url,
                    "tr_value": tr_value,
                    "line_icon": gadget.state.line_icon
                  });
                }

                if (gadget.state.show_line_selector) {
                  listbox_tbody_template = listbox_show_tbody_template;
                } else {
                  listbox_tbody_template = listbox_hidden_tbody_template;
                }

                return renderListboxTbody(gadget, listbox_tbody_template, body_value);
              })
              .push(function () {
                var prev_param = {},
                  next_param = {};
                function setNext() {
                  if (allDocs_result.data.rows.length > lines) {
                    next_param[gadget.state.key + '_begin_from'] = gadget.state.begin_from + lines;
                  }
                }

                if (gadget.state.begin_from === 0) {
                  setNext();
                } else {
                  prev_param[gadget.state.key + '_begin_from'] = gadget.state.begin_from - lines;
                  setNext();
                }
                return RSVP.all([
                  gadget.getUrlFor({command: 'change', options: prev_param}),
                  gadget.getUrlFor({command: 'change', options: next_param})
                ]);

              })
              .push(function (url_list) {
                var foot = {};
                foot.colspan = column_list.length + gadget.state.show_anchor +
                  (gadget.state.line_icon ? 1 : 0);
                foot.previous_classname = "ui-btn ui-icon-carat-l ui-btn-icon-left responsive ui-first-child";
                foot.previous_url = url_list[0];
                foot.next_classname = "ui-btn ui-icon-carat-r ui-btn-icon-right responsive ui-last-child";
                foot.next_url = url_list[1];
                if ((gadget.state.begin_from === 0) && (counter === 0)) {
                  foot.record = variable.translated_no_record;
                } else if ((allDocs_result.data.rows.length <= lines) && (gadget.state.begin_from === 0)) {
                  foot.record = counter + " " + variable.translated_records;
                } else {
                  foot.record = variable.translated_records + " " + (((gadget.state.begin_from + lines) / lines - 1) * lines + 1) + " - " + (((gadget.state.begin_from + lines) / lines - 1) * lines + counter);
                }

                if (gadget.state.begin_from === 0) {
                  foot.previous_classname += " ui-disabled";
                }
                if (allDocs_result.data.rows.length <= lines) {
                  foot.next_classname += " ui-disabled";
                }
                return renderListboxTfoot(gadget, foot);
              })
              .push(function (my_html) {
                gadget.element.querySelector(".tfoot").innerHTML = my_html;
                var loading_element_classList = gadget.element.querySelector(".listboxloader").classList;
                loading_element_classList.remove.apply(loading_element_classList, loading_class_list);
              });
          });
      }

      return result_queue;
    })

    .declareMethod('getListboxInfo', function () {
      //XXXXX search column list is used for search editor to
      //construct search panel
      //hardcoded begin_from key to define search position
      return {
        search_column_list: JSON.parse(this.state.search_column_list_json),
        begin_from: this.state.key + "_begin_from"
      };
    })

    //////////////////////////////////////////////
    // render the listbox in an asynchronous way
    //////////////////////////////////////////////
    .declareJob('fetchLineContent', function (only_cancel) {
      if (only_cancel) {
        return;
      }

      if (this.state.query === undefined) {
        /*
        return this.changeState({
          error_text: "Unsupported list method: '" + this.state.list_method + "'"
        });
        */
        return this.changeState({
          has_error: true
        });
      }

      var gadget = this,
        select_list = [],
        limit_options,
        column_list = JSON.parse(gadget.state.column_list_json),
        i;

      for (i = 0; i < column_list.length; i += 1) {
        select_list.push(column_list[i][0]);
      }
      select_list.push("uid");

      if (gadget.state.lines === 0) {
        limit_options = undefined;
      } else {
        limit_options = [gadget.state.begin_from, gadget.state.lines + 1];
      }


      return gadget.jio_allDocs({
        // XXX Not jIO compatible, but until a better api is found...
        "list_method_template": this.state.list_method_template,
        "query": gadget.state.query_string,
        "limit": limit_options,
        "select_list": select_list,
        "sort_on": JSON.parse(gadget.state.sort_list_json)
      })
        .push(function (result) {
          return gadget.changeState({
            allDocs_result: result
          });

        }, function (error) {
          // do not crash interface if allDocs fails
          //this will catch all error, not only search criteria invalid error
          if (error instanceof RSVP.CancellationError) {
            throw error;
          }
          console.warn(error);
          return gadget.changeState({
            has_error: true
          });
        });
    })

    .declareMethod("getContent", function (options) {
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
            .push(field_gadget.getContent.bind(field_gadget, options))
            .push(extendData);
        }
      }
      return queue
        .push(function () {
          data[form_gadget.props.listbox_uid_dict.key] = form_gadget.props.listbox_uid_dict.value;
          return data;
        });
    })

    .onEvent('click', function (evt) {
      var gadget = this,
        sort_button = gadget.element.querySelector('button[name="Sort"]'),
        hide_button = gadget.element.querySelector('button[name="Hide"]'),
        select_button = gadget.element.querySelector('button[name="SelectRows"]'),
        url,
        options = {},
        all_hide_element_list,
        hide_element_list = [],
        query_list = [],
        search_query,
        i;

      if (evt.target === sort_button) {
        evt.preventDefault();
        url = "gadget_erp5_sort_editor.html";
        options.sort_column_list = JSON.parse(gadget.state.sort_column_list_json);
        options.sort_list = JSON.parse(gadget.state.sort_list_json);
        options.key = gadget.state.key + "_sort_list:json";
        return gadget.renderEditorPanel(url, options);
      }

      if (evt.target === hide_button) {
        evt.preventDefault();
        return gadget.changeState({
          show_line_selector: true
        });
      }

      if (evt.target === select_button) {
        evt.preventDefault();

        //hide closed
        //maybe submit
        all_hide_element_list = gadget.element.querySelectorAll(".hide_element");
        for (i = 0; i < all_hide_element_list.length; i += 1) {
          if (!all_hide_element_list[i].checked) {
            hide_element_list.push(all_hide_element_list[i]);
          }
        }
        if (hide_element_list.length) {
          for (i = 0; i < hide_element_list.length; i += 1) {
            query_list.push(new SimpleQuery({
              key: "catalog.uid",
              type: "simple",
              operator: "!=",
              value: hide_element_list[i].getAttribute("value")
            }));
          }
          if (gadget.state.extended_search) {
            search_query = QueryFactory.create(gadget.state.extended_search);
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

        return gadget.changeState({
          show_line_selector: false
        });

      }

    }, false, false)

    .allowPublicAcquisition("notifyInvalid", function () {
      return;
    })

    .allowPublicAcquisition("notifyValid", function () {
      return;
    });

}(window, document, rJS, URI, RSVP,
  SimpleQuery, ComplexQuery, Query, Handlebars, console, QueryFactory));
