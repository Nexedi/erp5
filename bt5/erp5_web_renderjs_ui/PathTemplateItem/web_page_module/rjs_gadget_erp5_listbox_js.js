/*jslint indent: 2, maxerr: 3, nomen: true */
/*global window, document, rJS, URI, RSVP,
  SimpleQuery, ComplexQuery, Query, Handlebars, console, QueryFactory*/
(function (window, document, rJS, URI, RSVP,
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

    listbox_nav_source = gadget_klass.__template_element
                         .getElementById("listbox-nav-template")
                         .innerHTML,
    listbox_nav_template = Handlebars.compile(listbox_nav_source),

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

  function renderSubField(gadget, element, sub_field_json) {
    sub_field_json.editable = sub_field_json.editable && gadget.state.editable;
    return gadget.declareGadget(
      'gadget_erp5_label_field.html',
      {
        element: element,
        scope: sub_field_json.key
      }
    )
      .push(function (cell_gadget) {
        gadget.props.cell_gadget_list.push(cell_gadget);
        return cell_gadget.render({
          field_type: sub_field_json.type,
          field_json: sub_field_json,
          label: false
        });
      });
  }

  function renderEditableField(gadget, element, field_table) {
    var i,
      promise_list = [],
      column,
      line,
      element_list = element.querySelectorAll(".editable_div");

    for (i = 0; i < element_list.length; i += 1) {
      column = element_list[i].getAttribute("data-column");
      line = element_list[i].getAttribute("data-line");

      promise_list.push(renderSubField(
        gadget,
        element_list[i],
        field_table[line].cell_list[column] || ""
      ));
    }
    return RSVP.all(promise_list);
  }

  /**Put resulting `row_list` into `template` together with necessary gadget.state parameters.

  First, it removes all similar containers from within the table! Currently it is tricky
  to have multiple tbody/thead/tfoot elements! Feel free to refactor.

  Example call: renderTablePart(gadget, compiled_template, row_list, "tbody");
  **/
  function renderTablePart(gadget, template, row_list, container_name) {
    var container,
      column_list = JSON.parse(gadget.state.column_list_json);

    return gadget.translateHtml(template(
      {
        "row_list": row_list,
        "show_anchor": gadget.state.show_anchor,
        "column_list": column_list
      }
    ))
      .push(function (table_part_html) {
        container = document.createElement(container_name);
        container.innerHTML = table_part_html;
        return renderEditableField(gadget, container, row_list);
      })
      .push(function () {
        var table =  gadget.element.querySelector("table"),
          old_container = table.querySelector(container_name);
        if (old_container) {
          table.replaceChild(container, old_container);
        } else {
          table.appendChild(container);
        }
        return table;
      });
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
        // holds references to all editable sub-fields
        cell_gadget_list: [],
        // ERP5 needs listbox_uid:list with UIDs of editable sub-documents
        // so it can search for them in REQUEST.form under <field.id>_<sub-document.uid>
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
    .declareAcquiredMethod("renderEditorPanel", "renderEditorPanel")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("translate", "translate")

    //////////////////////////////////////////////
    // initialize the gadget content
    //////////////////////////////////////////////
    .declareMethod('render', function (options) {
      var gadget = this,
        field_json = options.field_json,
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

      // use only visible columns for sort
      if (field_json.sort_column_list.length) {
        sort_column_list = field_json.sort_column_list;
      }

      // use only visible columns for search
      if (field_json.search_column_list.length) {
        search_column_list = field_json.search_column_list;
      }

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

      // Cancel previous line rendering to not conflict with the asynchronous render for now
      gadget.fetchLineContent(true);
      queue = new RSVP.Queue();
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
          // XXX Fix in case of multiple listboxes
          return RSVP.all([
            gadget.getUrlParameter(field_json.key + '_begin_from'),
            gadget.getUrlParameter(field_json.key + '_sort_list:json'),
            gadget.getUrlParameter(field_json.key + '_column_list:json')
          ]);
        })
        .push(function (result_list) {
          var displayed_column_list = result_list[2] || [],
            displayed_column_item_list = [],
            displayable_column_item_list = [],
            displayable_column_dict = {},
            i,
            j,
            column_id,
            column_title,
            not_concatenated_list = [field_json.column_list, (field_json.all_column_list || [])];
          // Calculate the list of all displayable columns
          for (i = 0; i < not_concatenated_list.length; i += 1) {
            for (j = 0; j < not_concatenated_list[i].length; j += 1) {
              column_id = not_concatenated_list[i][j][0];
              if (!displayable_column_dict.hasOwnProperty(column_id)) {
                column_title = not_concatenated_list[i][j][1];
                displayable_column_dict[column_id] = column_title;
                displayable_column_item_list.push([column_id, column_title]);
              }
            }
          }

          // Check if user filters the column to display
          if (displayed_column_list !== 0) {
            for (i = 0; i < displayed_column_list.length; i += 1) {
              if (displayable_column_dict.hasOwnProperty(displayed_column_list[i])) {
                displayed_column_item_list.push([
                  displayed_column_list[i],
                  displayable_column_dict[displayed_column_list[i]]
                ]);
              }
            }
          }
          if (displayed_column_item_list.length === 0) {
            displayed_column_item_list = field_json.column_list;
          }

          return gadget.changeState({
            key: field_json.key,
            title: field_json.title,
            editable: field_json.editable,

            begin_from: parseInt(result_list[0] || '0', 10) || 0,

            // sorting is either specified in URL per listbox or we take default sorting from JSON's 'sort' attribute
            sort_list_json: JSON.stringify(result_list[1] || field_json.sort.map(jioize_sort)),

            show_anchor: field_json.show_anchor,
            show_stat: field_json.show_stat,
            show_count: field_json.show_count,

            line_icon: field_json.line_icon,
            query: field_json.query,
            query_string: query_string,
            lines: field_json.lines,
            list_method: field_json.list_method,
            list_method_template: field_json.list_method_template,

            domain_list_json: JSON.stringify(field_json.domain_root_list || []),
            domain_dict_json: JSON.stringify(field_json.domain_dict || {}),

            column_list_json: JSON.stringify(displayed_column_item_list),
            displayable_column_list_json:
              JSON.stringify(displayable_column_item_list),

            sort_column_list_json: JSON.stringify(sort_column_list),
            search_column_list_json: JSON.stringify(search_column_list),
            sort_class: field_json.sort_column_list.length ? "" : "ui-disabled",

            field_id: options.field_id,
            extended_search: options.extended_search,
            hide_class: options.hide_enabled ? "" : "ui-disabled",
            configure_class: options.configure_enabled ? "" : "ui-disabled",
            command: field_json.command || 'index',

            // Force line calculation in any case
            render_timestamp: new Date().getTime(),
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
          (modification_dict.hasOwnProperty('sort_class')) ||
          (modification_dict.hasOwnProperty('hide_class')) ||
          (modification_dict.hasOwnProperty('configure_class')) ||
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
            var listbox_thead_template,
              hide_button_text,
              hide_button_name,
              head_value_list = column_list.map(function (column, index) {
                var current_sort = sort_list.find(hasSameFirstItem(column)),
                  class_value = "";

                if (current_sort !== undefined) {
                  if (current_sort[1] === 'ascending') {
                    class_value = "ui-icon ui-icon-sort-amount-asc";
                  }
                  if (current_sort[1] === 'descending') {
                    class_value = "ui-icon ui-icon-sort-amount-desc";
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
              listbox_thead_template = listbox_show_thead_template;
              hide_button_text = 'Submit';
              hide_button_name = 'SelectRows';
            } else {
              listbox_thead_template = listbox_hidden_thead_template;
              hide_button_text = 'Hide Rows';
              hide_button_name = 'Hide';
            }
            return RSVP.all([
              gadget.translateHtml(listbox_template({
                hide_class: gadget.state.hide_class,
                sort_class: gadget.state.sort_class,
                configure_class: gadget.state.configure_class,
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

      /* Function `fetchLineContent` calls changeState({"allDocs_result": JIO.allDocs()})
         so this if gets re-evaluated later with allDocs_result defined. */
      if (gadget.state.allDocs_result === undefined) {
        // Trigger line content calculation
        result_queue
          .push(function () {
            var loading_element = gadget.element.querySelector(".listboxloader"),
              loading_element_classList = loading_element.classList,
              tbody_classList = gadget.element.querySelector("table").querySelector("tbody").classList;
            // Set the loading icon and trigger line calculation
            loading_element_classList.add.apply(loading_element_classList, loading_class_list);
            // remove pagination information
            loading_element.textContent = '';
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
              url_promise_list = [],
              allDocs_result = gadget.state.allDocs_result,
              counter,
              pagination_message = '',
              content_value;

            column_list = JSON.parse(gadget.state.column_list_json);
            // for actual allDocs_result structure see ref:gadget_erp5_jio.js
            if (lines === 0) {
              lines = allDocs_result.data.total_rows;
              counter = allDocs_result.data.total_rows;
            } else {
              counter = Math.min(allDocs_result.data.total_rows, lines);
            }
            sort_list = JSON.parse(gadget.state.sort_list_json);
            // Every line points to a sub-document so we need those links
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
              for (j = 0; j < column_list.length; j += 1) {
                content_value = allDocs_result.data.rows[i].value[column_list[j][0]] || "";
                if (content_value.url_value) {
                  if (content_value.url_value.command) {
                    url_promise_list.push(
                      gadget.getUrlFor(content_value.url_value)
                    );
                  } else {
                    url_promise_list.push(false);
                  }
                }
              }
            }
            return new RSVP.Queue()
              .push(function () {
                return RSVP.all([
                  RSVP.all(promise_list),
                  RSVP.all(url_promise_list)
                ]);
              })
              .push(function (result_list) {
                var row_list = [],
                  value,
                  cell_list,
                  url_value,
                  index = 0,
                  listbox_tbody_template,
                  line_link_list = result_list[0],
                  url_column_list = result_list[1],
                  setNonEditable = function (cell) {cell.editable = false; };
                // reset list of UIDs of editable sub-documents
                gadget.props.listbox_uid_dict = {
                  key: undefined,
                  value: []
                };
                // clear list of previous sub-gadgets
                gadget.props.cell_gadget_list = [];

                for (i = 0; i < counter; i += 1) {
                  cell_list = [];
                  for (j = 0; j < column_list.length; j += 1) {
                    value = allDocs_result.data.rows[i].value[column_list[j][0]] || "";
                     //url column
                    // get url value
                    if (value.url_value) {
                      url_value = url_column_list[index];
                      index += 1;
                    } else {
                      url_value = line_link_list[i];
                    }
                    // We need to check for field_gadget_param and then update
                    // value accordingly. value can be simply just a value in
                    // case of non-editable field thus we construct "field_json"
                    // manually and insert the value in "default"

                    if (value.constructor === Object) {
                      if (value.field_gadget_param) {
                        value = value.field_gadget_param;
                      } else {
                        value = {
                          'editable': 0,
                          'default': value.default
                        };
                      }
                    } else {
                      value = {
                        'editable': 0,
                        'default': value
                      };
                    }
                    value.href = url_value;
                    value.editable = value.editable && gadget.state.editable;
                    value.line = i;
                    value.column = j;
                    cell_list.push(value);
                  }
                  // note row's editable UID into gadget.props.listbox_uid_dict if exists to send it back to ERP5
                  // together with ListBox data. The listbox_uid_dict has quite surprising structure {key: <key>, value: <uid-array>}
                  if (allDocs_result.data.rows[i].value['listbox_uid:list'] !== undefined) {
                    gadget.props.listbox_uid_dict.key = allDocs_result.data.rows[i].value['listbox_uid:list'].key;
                    gadget.props.listbox_uid_dict.value.push(allDocs_result.data.rows[i].value['listbox_uid:list'].value);
                    // we could come up with better name than "value" for almost everything ^^
                  } else {
                    // if the document does not have listbox_uid:list then no gadget should be editable
                    cell_list.forEach(setNonEditable);
                  }
                  row_list.push({
                    "uid": allDocs_result.data.rows[i].value.uid,
                    "jump": line_link_list[i],
                    "cell_list": cell_list,
                    "line_icon": gadget.state.line_icon
                  });
                }

                if (gadget.state.show_line_selector) {
                  listbox_tbody_template = listbox_show_tbody_template;
                } else {
                  listbox_tbody_template = listbox_hidden_tbody_template;
                }

                return renderTablePart(gadget, listbox_tbody_template, row_list, "tbody");
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
                var record,
                  previous_url = url_list[0],
                  next_url = url_list[1],
                  previous_classname = "ui-btn ui-icon-carat-l ui-btn-icon-left responsive ui-first-child",
                  next_classname = "ui-btn ui-icon-carat-r ui-btn-icon-right responsive ui-last-child";

                if ((gadget.state.begin_from === 0) && (counter === 0)) {
                  record = variable.translated_no_record;
                  pagination_message = 0;
                } else if ((allDocs_result.data.rows.length <= lines) && (gadget.state.begin_from === 0)) {
                  record = counter + " " + variable.translated_records;
                  pagination_message = counter;
                } else {
                  pagination_message = (((gadget.state.begin_from + lines) / lines - 1) * lines + 1) + " - " + (((gadget.state.begin_from + lines) / lines - 1) * lines + counter);
                  if (allDocs_result.count !== undefined) {
                    pagination_message += ' / ' + allDocs_result.count;
                  }
                  record = variable.translated_records + " " + pagination_message;
                }

                if (gadget.state.begin_from === 0) {
                  previous_classname += " ui-disabled";
                }
                if (allDocs_result.data.rows.length <= lines) {
                  next_classname += " ui-disabled";
                }
                return gadget.translateHtml(
                  listbox_nav_template({
                    "previous_classname": previous_classname,
                    "previous_url": previous_url,
                    "record": record,
                    "next_classname": next_classname,
                    "next_url": next_url
                  })
                );
              })
              .push(function (listbox_nav_html) {
                gadget.element.querySelector('nav').innerHTML = listbox_nav_html;

                var result_sum = (gadget.state.allDocs_result.sum || {}).rows || [], // render summary footer if available
                  summary = result_sum.map(function (row, row_index) {
                    var row_editability = row['listbox_uid:list'] !== undefined;
                    return {
                      "uid": 'summary' + row_index,
                      "cell_list": column_list.map(function (col_name, col_index) {
                        var field_json = row.value[col_name[0]] || "";
                        if (field_json.constructor !== Object) {
                          field_json = {'default': field_json, 'editable': 0};
                        }
                        field_json.editable = field_json.editable && row_editability;
                        field_json.column = col_index;
                        field_json.line = row_index;
                        return field_json;
                      })
                    };
                  }),
                  element;

                if (counter === 0) {
                  // do not render footer (summary) when no data in Listbox because it is ugly
                  element = gadget.element.querySelector("table tfoot tr");
                  if (element !== null) {
                    element.remove();
                  }
                  return null;
                }
                return renderTablePart(gadget, listbox_tfoot_template, summary, "tfoot");
              })
              .push(function () {
                var loading_element = gadget.element.querySelector(".listboxloader"),
                  loading_element_classList = loading_element.classList;
                loading_element_classList.remove.apply(loading_element_classList, loading_class_list);
                loading_element.textContent = '(' + pagination_message + ')';
              });
          });
      }

      return result_queue;
    })

    .declareMethod('getListboxInfo', function () {
      var domain_list = JSON.parse(this.state.domain_list_json),
        domain_dict = JSON.parse(this.state.domain_dict_json),
        i,
        len = domain_list.length;
      for (i = 0; i < len; i += 1) {
        if (domain_dict.hasOwnProperty(domain_list[i][0])) {
          domain_dict['selection_domain_' + domain_list[i][0]] = domain_dict[domain_list[i][0]];
          delete domain_dict[domain_list[i][0]];
        }
        domain_list[i][0] = 'selection_domain_' + domain_list[i][0];
      }
      //XXXXX search column list is used for search editor to
      //construct search panel
      //hardcoded begin_from key to define search position
      return {
        search_column_list: JSON.parse(this.state.search_column_list_json),
        domain_list: domain_list,
        domain_dict: domain_dict,
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
        limit_options = [],
        aggregation_option_list = [],
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

      if (gadget.state.show_stat === true) {
        aggregation_option_list.push("sum");
      }
      if (gadget.state.show_count === true) {
        aggregation_option_list.push("count");
      }

      return gadget.jio_allDocs({
        // XXX Not jIO compatible, but until a better api is found...
        "list_method_template": this.state.list_method_template,
        "query": gadget.state.query_string,
        "limit": limit_options,
        "select_list": select_list,
        // "aggregation": aggregation_option_list
        "sort_on": JSON.parse(gadget.state.sort_list_json)
      })
        .push(function (result) {
          return gadget.changeState({
            allDocs_result: result
          });

        }, function (error) {
          // do not crash interface if allDocs fails
          // this will catch all error, not only search criteria invalid error
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
    }, {mutex: 'changestate'})

    .onEvent('click', function (evt) {
      var gadget = this,
        sort_button = gadget.element.querySelector('button[name="Sort"]'),
        hide_button = gadget.element.querySelector('button[name="Hide"]'),
        configure_button = gadget.element.querySelector('button[name="Configure"]'),
        select_button = gadget.element.querySelector('button[name="SelectRows"]'),
        url,
        options = {},
        all_hide_element_list,
        hide_element_list = [],
        query_list = [],
        search_query,
        i;

      if (evt.target === configure_button) {
        evt.preventDefault();
        url = "gadget_erp5_configure_editor.html";
        options.column_list = JSON.parse(gadget.state.column_list_json);
        options.displayable_column_list = JSON.parse(gadget.state.displayable_column_list_json);
        options.key = gadget.state.key + "_column_list:json";
        return gadget.renderEditorPanel(url, options);
      }

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
