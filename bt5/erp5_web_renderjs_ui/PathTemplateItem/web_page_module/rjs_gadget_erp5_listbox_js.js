/*jslint indent: 2, maxerr: 3, nomen: true */
/*global window, document, rJS, URI, RSVP, console*/
(function (window, document, rJS, URI, RSVP, console) {
  "use strict";

  var variable = {},
    loading_class_list = ['ui-icon-spinner', 'ui-btn-icon-left'],
    disabled_class = 'ui-disabled';

  function listbox_tbody_template(options) {
/*
       <tbody>
        {{#each row_list}}
           <tr>
             {{#if ../show_anchor}}
                <th>
                  <a class="ui-icon-carat-r ui-btn-icon-notext" href="{{jump}}"> </a>
                </th>
             {{/if}}
           {{#each cell_list}}
              <td>
                {{#if ../../show_line_selector}}
                  {{#if @first}}
                    <input data-uid="{{../uid}}" type="checkbox" class="hide_element" id="listbox_line_{{../uid}}">
                  {{/if}}
                  {{#if type}}
                    <label for="listbox_line_{{../uid}}" class="editable_div" data-column="{{column}}" data-line="{{line}}"></label>
                  {{else}}
                    <label for="listbox_line_{{../uid}}">{{default}}</label>
                  {{/if}}

                {{else}}

                  {{#if type}}
                    {{#if editable}}
                      <div class="editable_div" data-column="{{column}}" data-line="{{line}}"></div>
                    {{else}}
                      {{#if href}}
                        <a href="{{href}}">
                          <div class="editable_div" data-column="{{column}}" data-line="{{line}}"></div>
                        </a>
                      {{else}}
                        <div class="editable_div" data-column="{{column}}" data-line="{{line}}"></div>
                      {{/if}}
                    {{/if}}
                  {{else}}
                    {{#if href}}
                      <a href="{{href}}">{{default}}</a>
                    {{else}}
                      <p>{{default}}</p>
                    {{/if}}
                  {{/if}}

                {{/if}}
              </td>
           {{/each}}
           {{#if line_icon}}
             <th>
               <a href ="{{jump}}" class="ui-btn-icon-right ui-icon-sign-in"></a>
             </th>
            {{/if}}
         </tr>
        {{/each}}
       </tbody>
*/
    var tbody_element = document.createElement('tbody'),
      i,
      j,
      row,
      cell,
      tr_element,
      td_element,
      sub_element,
      a_element;

    for (i = 0; i < options.row_list.length; i += 1) {
      tr_element = document.createElement('tr');
      row = options.row_list[i];
      if (options.show_anchor) {
        td_element = document.createElement('td');
        sub_element = document.createElement('a');
        sub_element.setAttribute('class', 'ui-icon-carat-r ui-btn-icon-notext');
        sub_element.href = row.jump;
        sub_element.textContent = ' ';
        td_element.appendChild(sub_element);
        tr_element.appendChild(td_element);
      }

      for (j = 0; j < row.cell_list.length; j += 1) {
        cell = row.cell_list[j];
        td_element = document.createElement('td');

        if (options.show_line_selector) {
          if (j === 0) {
            // If first cell, show a checkbox to select the line
            sub_element = document.createElement('input');
            sub_element.setAttribute('data-uid', row.uid);
            sub_element.setAttribute('type', 'checkbox');
            sub_element.setAttribute('class', 'hide_element');
            sub_element.setAttribute('id', 'listbox_line_' + row.uid);
            td_element.appendChild(sub_element);
          }

          // Create a label, to update the checkbox when clicking the text
          sub_element = document.createElement('label');
          sub_element.setAttribute('for', 'listbox_line_' + row.uid);
          if (cell.type) {
            sub_element.setAttribute('class', 'editable_div');
            sub_element.setAttribute('data-column', cell.column);
            sub_element.setAttribute('data-line', cell.line);
          } else {
            sub_element.textContent = cell.default;
          }
          td_element.appendChild(sub_element);

        } else {

          if (cell.type) {
            sub_element = document.createElement('div');
            sub_element.setAttribute('class', 'editable_div');
            sub_element.setAttribute('data-column', cell.column);
            sub_element.setAttribute('data-line', cell.line);
            if (cell.editable || !cell.href) {
              td_element.appendChild(sub_element);
            } else {
              a_element = document.createElement('a');
              a_element.href = cell.href;
              a_element.appendChild(sub_element);
              td_element.appendChild(a_element);
            }

          } else {
            if (cell.href) {
              sub_element = document.createElement('a');
              sub_element.href = cell.href;
            } else {
              sub_element = document.createElement('p');
            }
            sub_element.textContent = cell.default;
            td_element.appendChild(sub_element);
          }
        }

        tr_element.appendChild(td_element);
      }

      if (row.line_icon) {
        td_element = document.createElement('td');
        sub_element = document.createElement('a');
        sub_element.setAttribute('class', 'ui-btn-icon-right ui-icon-sign-in');
        sub_element.href = row.jump;
        td_element.appendChild(sub_element);
        tr_element.appendChild(td_element);
      }

      tbody_element.appendChild(tr_element);
    }
    return tbody_element;
  }

  function listbox_tfoot_template(options) {
/*
       <tfoot>
       {{#each row_list}}
         <tr>
           {{#if ../show_anchor}}
             <td>Total</td>
           {{/if}}
           {{#each cell_list}}
           <td>
             {{#if type}}
               <div class="editable_div" data-column="{{column}}" data-line="{{line}}"></div>
             {{else}}
               {{#if default}}
                 {{default}}
               {{else}}
                 {{#unless ../../show_anchor }}
                   {{#if @first}}
                     Total
                   {{/if}}
                 {{/unless}}
               {{/if}}
             {{/if}}
           </td>
           {{/each}}
         </tr>
       {{/each}}
       </tfoot>
*/
    var tfoot_element = document.createElement('tfoot'),
      i,
      j,
      row,
      cell,
      tr_element,
      td_element,
      div_element;
    for (i = 0; i < options.row_list.length; i += 1) {
      tr_element = document.createElement('tr');
      if (options.show_anchor) {
        td_element = document.createElement('td');
        td_element.textContent = 'Total';
        tr_element.appendChild(td_element);
      }
      row = options.row_list[i];
      for (j = 0; j < row.cell_list.length; j += 1) {
        cell = row.cell_list[j];
        td_element = document.createElement('td');
        if (cell.type) {
          div_element = document.createElement('div');
          div_element.setAttribute('class', 'editable_div');
          div_element.setAttribute('data-column', cell.column);
          div_element.setAttribute('data-line', cell.line);
          td_element.appendChild(div_element);
        } else {
          if (cell.default) {
            td_element.textContent = cell.default;
          } else if ((!options.show_anchor) && (j === 0)) {
            td_element.textContent = 'Total';
          }
        }
        tr_element.appendChild(td_element);
      }
      tfoot_element.appendChild(tr_element);
    }
    return tfoot_element;
  }

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

    container = template({
      "row_list": row_list,
      "show_anchor": gadget.state.show_anchor,
      "column_list": column_list,
      "show_line_selector": gadget.state.show_line_selector,
      "show_select_action": gadget.state.show_select_action,
      "show_clipboard_action": gadget.state.show_clipboard_action
    });
    return new RSVP.Queue()
      .push(function () {
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
    .setState({disabled: true})
    // Init local properties
    .ready(function () {
      this.props = {
        // holds references to all editable sub-fields
        cell_gadget_list: [],
        // ERP5 needs listbox_uid:list with UIDs of editable sub-documents
        // so it can search for them in REQUEST.form under <field.id>_<sub-document.uid>
        listbox_uid_dict: {},
        listbox_query_param_json: undefined
      };
    })

    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("renderEditorPanel", "renderEditorPanel")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getTranslationList", "getTranslationList")
    .declareAcquiredMethod("getListboxSelectActionList",
                           "getListboxSelectActionList")
    .declareAcquiredMethod("getListboxClipboardActionList",
                           "getListboxClipboardActionList")
    .declareAcquiredMethod("triggerListboxSelectAction",
                           "triggerListboxSelectAction")
    .declareAcquiredMethod("triggerListboxClipboardAction",
                           "triggerListboxClipboardAction")

    //////////////////////////////////////////////
    // initialize the gadget content
    //////////////////////////////////////////////
    .declareMethod('render', function render(options) {
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
            return gadget.getTranslationList(['Records', 'No records']);
          })
          .push(function (result_list) {
            variable.translated_records = result_list[0];
            variable.translated_no_record = result_list[1];
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
            default_value: field_json.default,

            // No error message
            has_error: false,
            show_line_selector: false,
            show_select_action: false,
            show_clipboard_action: false
          });
        });
      return queue;
    })

    .onStateChange(function onStateChange(modification_dict) {
      var gadget = this,
        sort_key = gadget.state.key + "_sort_list:json",
        sort_list,
        column_list,
        sortable_column_list,
        i,
        j,
        result_queue = new RSVP.Queue(),
        button_selector_list = ['button[name="Sort"]', 'button[name="Hide"]',
                                'button[name="Clipboard"]',
                                'button[name="Configure"]',
                                'button[name="SelectRows"]'],
        button;

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
            return RSVP.all([
              gadget.getUrlFor({
                command: 'store_and_change',
                options: options
              }),
              gadget.getTranslationList(['Invalid Search Criteria', 'Reset'])
            ]);
          })
          .push(function (result_list) {
/*
<div>
   <a href="{{reset_url}}">
     <span class='ui-info-error' data-i18n="Invalid Search Criteria">Invalid Search Criteria</span>
     <span>-</span>
     <span data-i18n="Reset">Reset</span>
   </a>
</div>
*/
            var container = gadget.element.querySelector(".document_table"),
              div_element = document.createElement('div'),
              a_element = document.createElement('a'),
              span_element;
            a_element.href = result_list[0];

            span_element = document.createElement('span');
            span_element.setAttribute('class', 'ui-info-error');
            span_element.textContent = result_list[1][0];
            a_element.appendChild(span_element);

            span_element = document.createElement('span');
            span_element.textContent = '-';
            a_element.appendChild(span_element);

            span_element = document.createElement('span');
            span_element.textContent = result_list[1][1];
            a_element.appendChild(span_element);

            div_element.appendChild(a_element);
            while (container.firstChild) {
              container.removeChild(container.firstChild);
            }
            container.appendChild(div_element);
          });
      }

      if (modification_dict.hasOwnProperty('disabled')) {
        // Mark buttons as enabled/disabled
        // so that Zelenium can explicitely wait for enabled button
        for (i = 0; i < button_selector_list.length; i += 1) {
          button = gadget.element.querySelector(button_selector_list[i]);
          if (button !== null) {
            button.disabled = gadget.state.disabled;
          }
        }
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
        sortable_column_list = JSON.parse(gadget.state.sort_column_list_json); // sortable columns

        result_queue
          .push(function () {
            var k,
              column,
              is_sortable,
              current_sort,
              options,
              url_for_option_list = [],
              is_sortable_list = [],
              select_list;

            for (k = 0; k < column_list.length; k += 1) {
              column = column_list[k];
              is_sortable = sortable_column_list.find(hasSameFirstItem(column)) !== undefined;
              current_sort = sort_list.find(hasSameFirstItem(column));

              is_sortable_list.push(is_sortable);
              if (is_sortable) {
                options = {};
                options[sort_key] = [[column[0], 'descending']];  // make it the only new sort (replace array instead of push)
                if (current_sort !== undefined && current_sort[1] === 'descending') {
                  options[sort_key] = [[column[0], 'ascending']];
                }
                url_for_option_list.push({"command": 'store_and_change', "options": options});
              }
            }

            if (gadget.state.show_select_action) {
              select_list = gadget.getListboxSelectActionList()
                .push(undefined, function (error) {
                  if (error instanceof rJS.AcquisitionError) {
                    // Do not break if parent gadget does not implement it
                    // XXX this could be a new rJS function when doing
                    // declareAcquiredMethod
                    return [];
                  }
                  throw error;
                });
            }

            if (gadget.state.show_clipboard_action) {
              select_list = gadget.getListboxClipboardActionList()
                .push(undefined, function (error) {
                  if (error instanceof rJS.AcquisitionError) {
                    // Do not break if parent gadget does not implement it
                    // XXX this could be a new rJS function when doing
                    // declareAcquiredMethod
                    return [];
                  }
                  throw error;
                });
            }

            return RSVP.all([
              gadget.getUrlForList(url_for_option_list),
              is_sortable_list,
              gadget.getTranslationList(['Jump',
                                         'Select', 'Configure', 'Sort',
                                         'Cancel', 'Edit']),
              select_list
            ]);
          })
          .push(function (result_list) {
            var container = gadget.element.querySelector(".document_table"),
              url_for_list = result_list[0],
              translation_list = result_list[2],
              is_sortable_list = result_list[1],
              select_option_list = result_list[3],
              k,
              url_for_index = 0,
              column,
              current_sort,
              fragment = document.createDocumentFragment(),
              div_element = document.createElement('div'),
              table_element = document.createElement('table'),
              button_element,
              h1_element = document.createElement('h1'),
              span_element = document.createElement('span'),
              tr_element,
              th_element,
              a_element;

            div_element.setAttribute('class', 'ui-table-header ui-header');
            // For an unknown reason, the title used to be translated previously,
            // which is unexpected, as the value can't be hardcoded in the gadget
            // <h1>{{title}} <span class="listboxloader ui-icon-spinner ui-btn-icon-left"></span></h1>
            h1_element.textContent = gadget.state.title + ' ';
            span_element.setAttribute('class', 'listboxloader ui-icon-spinner ui-btn-icon-left');
            h1_element.appendChild(span_element);
            div_element.appendChild(h1_element);

            if (gadget.state.show_select_action) {
              for (k = 0; k < select_option_list.length; k += 1) {
                // Add include button
                // <button data-rel="hide" data-i18n="Include" name="IncludeRows" type="button" class="ui-icon-eye ui-btn-icon-left {{hide_class}}"></button>
                button_element = document.createElement('button');
                button_element.setAttribute('data-rel', 'hide');
                button_element.setAttribute('data-select-action', select_option_list[k].action);
                button_element.setAttribute('name', 'SelectAction');
                button_element.type = 'button';
                button_element.setAttribute('class', 'ui-icon-' + select_option_list[k].icon + ' ui-btn-icon-left');
                button_element.textContent = select_option_list[k].title;
                div_element.appendChild(button_element);
              }

              // Add cancel button
              // <button data-rel="cancel" data-i18n="Cancel" name="ExcludeRows" type="button" class="ui-icon-times ui-btn-icon-left {{hide_class}}"></button>
              button_element = document.createElement('button');
              button_element.setAttribute('data-rel', 'hide');
              button_element.setAttribute('name', 'CancelSelect');
              button_element.type = 'button';
              button_element.setAttribute('class', 'ui-icon-times ui-btn-icon-left');
              button_element.textContent = translation_list[4];
              div_element.appendChild(button_element);

            } else if (gadget.state.show_clipboard_action) {
              for (k = 0; k < select_option_list.length; k += 1) {
                // Add include button
                // <button data-rel="hide" data-i18n="Include" name="IncludeRows" type="button" class="ui-icon-eye ui-btn-icon-left {{hide_class}}"></button>
                button_element = document.createElement('button');
                button_element.setAttribute('data-rel', 'clipboard');
                button_element.setAttribute('data-clipboard-action', select_option_list[k].action);
                button_element.setAttribute('name', 'ClipboardAction');
                button_element.type = 'button';
                button_element.setAttribute('class', 'ui-icon-' + select_option_list[k].icon + ' ui-btn-icon-left');
                button_element.textContent = select_option_list[k].title;
                div_element.appendChild(button_element);
              }

              // Add cancel button
              // <button data-rel="cancel" data-i18n="Cancel" name="ExcludeRows" type="button" class="ui-icon-times ui-btn-icon-left {{hide_class}}"></button>
              button_element = document.createElement('button');
              button_element.setAttribute('data-rel', 'hide');
              button_element.setAttribute('name', 'CancelSelect');
              button_element.type = 'button';
              button_element.setAttribute('class', 'ui-icon-times ui-btn-icon-left');
              button_element.textContent = translation_list[4];
              div_element.appendChild(button_element);

            } else {

              // Add Configure button
              // <button {{disabled}} data-rel="configure_columns" data-i18n="Configure" name="Configure" type="button" class="ui-icon-wrench ui-btn-icon-left {{configure_class}}"></button>
              button_element = document.createElement('button');
              button_element.disabled = gadget.state.disabled;
              button_element.setAttribute('data-rel', 'configure_columns');
              button_element.setAttribute('name', 'Configure');
              button_element.type = 'button';
              button_element.setAttribute('class', 'ui-icon-wrench ui-btn-icon-left ' + gadget.state.configure_class);
              button_element.textContent = translation_list[2];
              div_element.appendChild(button_element);

              // Add Sort button
              // <button {{disabled}} data-rel="Sort" data-i18n="Sort" name="Sort" type="button" class="ui-icon-sort-amount-desc ui-btn-icon-left {{sort_class}}"></button>
              button_element = document.createElement('button');
              button_element.disabled = gadget.state.disabled;
              button_element.setAttribute('data-rel', 'Sort');
              button_element.setAttribute('name', 'Sort');
              button_element.type = 'button';
              button_element.setAttribute('class', 'ui-icon-sort-amount-desc ui-btn-icon-left ' + gadget.state.sort_class);
              button_element.textContent = translation_list[3];
              div_element.appendChild(button_element);

              // Add Do button
              // <button {{disabled}} data-rel="hide" data-i18n="Select" name="Hide" type="button" class="ui-icon-check-square-o ui-btn-icon-left {{hide_class}}"></button>
              button_element = document.createElement('button');
              button_element.setAttribute('data-rel', 'clipboard');
              button_element.setAttribute('name', 'Clipboard');
              button_element.type = 'button';
              button_element.setAttribute('class', 'ui-icon-list-ul ui-btn-icon-left ');
              button_element.textContent = translation_list[5];
              div_element.appendChild(button_element);

              // Add Select button
              // <button {{disabled}} data-rel="hide" data-i18n="Select" name="Hide" type="button" class="ui-icon-check-square-o ui-btn-icon-left {{hide_class}}"></button>
              button_element = document.createElement('button');
              button_element.disabled = gadget.state.disabled;
              button_element.setAttribute('data-rel', 'hide');
              button_element.setAttribute('name', 'Hide');
              button_element.type = 'button';
              button_element.setAttribute('class', 'ui-icon-check-square-o ui-btn-icon-left ' + gadget.state.hide_class);
              button_element.textContent = translation_list[1];
              div_element.appendChild(button_element);
            }
            fragment.appendChild(div_element);

            table_element.innerHTML = '<thead class="thead"><tr></tr></thead><tbody></tbody><tfoot></tfoot>';
            tr_element = table_element.querySelector('tr');

            if (gadget.state.show_anchor) {
              th_element = document.createElement('th');
              th_element.textContent = translation_list[0];
              tr_element.appendChild(th_element);
            }

            for (k = 0; k < column_list.length; k += 1) {
              column = column_list[k];
              th_element = document.createElement('th');

              current_sort = sort_list.find(hasSameFirstItem(column));
              if (current_sort !== undefined) {
                if (current_sort[1] === 'ascending') {
                  th_element.setAttribute('class', "ui-icon ui-icon-sort-amount-asc");
                } else if (current_sort[1] === 'descending') {
                  th_element.setAttribute('class', "ui-icon ui-icon-sort-amount-desc");
                }
              }

              if (gadget.state.show_line_selector) {
                // <th class="{{class_value}}">{{text}}</th>
                th_element.textContent = column[1];
              } else {

                if (is_sortable_list[k]) {
                  // <th class="{{class_value}}"><a href="{{sort_link}}">{{text}}</a></th>
                  a_element = document.createElement('a');
                  a_element.textContent = column[1];
                  a_element.href = url_for_list[url_for_index];
                  th_element.appendChild(a_element);
                  url_for_index += 1;
                } else {
                  // <th class="{{class_value}}">{{text}}</th>
                  th_element.textContent = column[1];
                }
              }

              tr_element.appendChild(th_element);
            }

            if (gadget.state.line_icon) {
              th_element = document.createElement('th');
              tr_element.appendChild(th_element);
            }

            fragment.appendChild(table_element);

            fragment.appendChild(document.createElement('nav'));

            while (container.firstChild) {
              container.removeChild(container.firstChild);
            }
            container.appendChild(fragment);
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
              allDocs_result = JSON.parse(gadget.state.allDocs_result),
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
              promise_list.push({
                command: gadget.state.command,
                options: {
                  jio_key: allDocs_result.data.rows[i].id,
                  uid: allDocs_result.data.rows[i].value.uid,
                  selection_index: gadget.state.begin_from + i,
                  query: gadget.state.query_string,
                  list_method_template: gadget.state.list_method_template,
                  "sort_list:json": sort_list
                }
              });
              for (j = 0; j < column_list.length; j += 1) {
                content_value = allDocs_result.data.rows[i].value[column_list[j][0]] || "";
                if (content_value.url_value) {
                  if (content_value.url_value.command) {
                    url_promise_list.push(content_value.url_value);
                  }
                }
              }
            }
            promise_list.push.apply(promise_list, url_promise_list);
            return gadget.getUrlForList(promise_list)
              .push(function (line_link_list) {
                var row_list = [],
                  value,
                  cell_list,
                  url_value,
                  index = 0,
                  setNonEditable = function (cell) {cell.editable = false; };
                // reset list of UIDs of editable sub-documents
                gadget.props.listbox_uid_dict = {
                  key: undefined,
                  value: []
                };
                gadget.props.listbox_query_param_json = allDocs_result.listbox_query_param_json;
                // clear list of previous sub-gadgets
                gadget.props.cell_gadget_list = [];

                for (i = 0; i < counter; i += 1) {
                  cell_list = [];
                  for (j = 0; j < column_list.length; j += 1) {
                    value = allDocs_result.data.rows[i].value[column_list[j][0]] || "";
                     //url column
                    // get url value
                    if (value.url_value) {
                      if (value.url_value.command) {
                        url_value = line_link_list[counter + index];
                        index += 1;
                      } else {
                        url_value = false;
                      }
                    } else if (value === "") {
                      url_value = false;
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
                  if ((!gadget.state.show_line_selector) && (allDocs_result.data.rows[i].value['listbox_uid:list'] !== undefined)) {
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
                  gadget.getTranslationList(['sample of', 'Previous', 'Next']),
                  gadget.getUrlForList([
                    {command: 'change', options: prev_param},
                    {command: 'change', options: next_param}
                  ])
                ]);
              })
              .push(function (result_list) {
                var sample_string = result_list[0][0],
                  url_list = result_list[1],
                  record,
                  previous_url = url_list[0],
                  next_url = url_list[1],
                  previous_classname = "ui-btn ui-icon-carat-l ui-btn-icon-left responsive ui-first-child",
                  next_classname = "ui-btn ui-icon-carat-r ui-btn-icon-right responsive ui-last-child",
                  fragment = document.createDocumentFragment(),
                  sub_element,
                  nav_element = gadget.element.querySelector('nav'),
                  from_index;

                if ((gadget.state.begin_from === 0) && (counter === 0)) {
                  record = variable.translated_no_record;
                  pagination_message = 0;
                } else if ((allDocs_result.data.rows.length <= lines) && (gadget.state.begin_from === 0)) {
                  record = counter + " " + variable.translated_records;
                  pagination_message = counter;
                } else {
                  from_index = Math.round(((gadget.state.begin_from + lines) / lines - 1) * lines);
                  pagination_message = (from_index + 1) + " - " + (from_index + counter);
                  if (allDocs_result.count !== undefined) {
                    if ((allDocs_result.count === 1000) && (!gadget.state.show_count)) {
                      pagination_message += ' / ' + sample_string + ' ' + allDocs_result.count;
                    } else {
                      pagination_message += ' / ' + allDocs_result.count;
                    }
                  }
                  record = variable.translated_records + " " + pagination_message;
                }

                if (gadget.state.begin_from === 0) {
                  previous_classname += " ui-disabled";
                }
                if (allDocs_result.data.rows.length <= lines) {
                  next_classname += " ui-disabled";
                }

// <a class="{{previous_classname}}" data-i18n="Previous" href="{{previous_url}}">Previous</a>
// <a class="{{next_classname}}" data-i18n="Next" href="{{next_url}}">Next</a>
// <span class="ui-disabled">{{record}}</span>
                sub_element = document.createElement('a');
                sub_element.setAttribute('class', previous_classname);
                sub_element.href = previous_url;
                sub_element.textContent = result_list[0][1];
                fragment.appendChild(sub_element);

                sub_element = document.createElement('a');
                sub_element.setAttribute('class', next_classname);
                sub_element.href = next_url;
                sub_element.textContent = result_list[0][2];
                fragment.appendChild(sub_element);

                sub_element = document.createElement('span');
                sub_element.setAttribute('class', 'ui-disabled');
                sub_element.textContent = record;
                fragment.appendChild(sub_element);

                while (nav_element.firstChild) {
                  nav_element.removeChild(nav_element.firstChild);
                }
                nav_element.appendChild(fragment);
              })
              .push(function () {
                var result_sum = (allDocs_result.sum || {}).rows || [], // render summary footer if available
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

    .declareMethod('getListboxInfo', function getListboxInfo() {
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
    .declareJob('fetchLineContent', function fetchLineContent(only_cancel) {
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
        "default_value": this.state.default_value,
        "query": gadget.state.query_string,
        "limit": limit_options,
        "select_list": select_list,
        // "aggregation": aggregation_option_list
        "sort_on": JSON.parse(gadget.state.sort_list_json)
      })
        .push(function (result) {
          return gadget.changeState({
            allDocs_result: JSON.stringify(result)
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

    .declareMethod("getContent", function getContent(options) {
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
          if (form_gadget.props.listbox_query_param_json !== undefined) {
            // JSON query parameters are only sent when rendering an ERP5 Form
            data[form_gadget.props.listbox_query_param_json.key] =
              form_gadget.props.listbox_query_param_json.value;
          }
          return data;
        });
    }, {mutex: 'changestate'})

    .declareMethod("checkValidity", function checkValidity(options) {
      var form_gadget = this,
        k,
        field_gadget,
        count = form_gadget.props.cell_gadget_list.length,
        result = true,
        queue = new RSVP.Queue();

      function extendData(is_valid) {
        result = result && is_valid;
      }

      for (k = 0; k < count; k += 1) {
        field_gadget = form_gadget.props.cell_gadget_list[k];
        // XXX Hack until better defined
        if (field_gadget.checkValidity !== undefined) {
          queue
            .push(field_gadget.checkValidity.bind(field_gadget, options))
            .push(extendData);
        }
      }
      return queue
        .push(function () {
          return result;
        });
    }, {mutex: 'changestate'})

    .onEvent('click', function click(evt) {
      // For some reason, Zelenium can click even if button has the disabled
      // attribute. So, it is needed for now to manually checks
      if (this.state.disabled) {
        return;
      }

      var gadget = this,
        sort_button = gadget.element.querySelector('button[name="Sort"]'),
        hide_button = gadget.element.querySelector('button[name="Hide"]'),
        clipboard_button = gadget.element.querySelector('button[name="Clipboard"]'),
        configure_button = gadget.element.querySelector('button[name="Configure"]'),
        cancel_select_button = gadget.element.querySelector('button[name="CancelSelect"]'),
        url,
        options = {},
        all_hide_element_list,
        checked_uid_list,
        unchecked_uid_list,
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
          show_line_selector: true,
          show_select_action: true
        });
      }

      if (evt.target === clipboard_button) {
        evt.preventDefault();
        return gadget.changeState({
          show_line_selector: true,
          show_clipboard_action: true
        });
      }

      if (evt.target === cancel_select_button) {
        evt.preventDefault();
        return gadget.changeState({
          show_line_selector: false,
          show_select_action: false,
          show_clipboard_action: false
        });
      }

      if ((evt.target.type === 'button') &&
          ((evt.target.name === 'SelectAction') || (evt.target.name === 'ClipboardAction'))) {
        evt.preventDefault();

        checked_uid_list = [];
        unchecked_uid_list = [];

        //hide closed
        //maybe submit
        all_hide_element_list = gadget.element.querySelectorAll(".hide_element");
        for (i = 0; i < all_hide_element_list.length; i += 1) {
          if (all_hide_element_list[i].checked) {
            checked_uid_list.push(all_hide_element_list[i].getAttribute("data-uid"));
          } else {
            unchecked_uid_list.push(all_hide_element_list[i].getAttribute("data-uid"));
          }
        }
        if (evt.target.name === 'SelectAction') {
          return gadget.triggerListboxSelectAction(evt.target.getAttribute('data-select-action'), checked_uid_list, unchecked_uid_list);
        }
        return gadget.triggerListboxClipboardAction(evt.target.getAttribute('data-clipboard-action'), checked_uid_list, unchecked_uid_list);
      }
    }, false, false)

    .declareService(function enableButton() {
      // click event listener is now activated
      // Change the state of the gadget
      return this.changeState({disabled: false});
    })

    .allowPublicAcquisition("notifyInvalid", function notifyInvalid() {
      return;
    })

    .allowPublicAcquisition("notifyValid", function notifyValid() {
      return;
    });

}(window, document, rJS, URI, RSVP, console));
