/*jslint indent: 2, maxerr: 3, nomen: true */
/*global window, document, rJS, URI, RSVP, isEmpty, console, domsugar*/
(function () {
  "use strict";

  var variable = {},
    loading_class_list = ['ui-icon-spinner', 'ui-btn-icon-left'],
    disabled_class = 'ui-disabled';

  function getRelativeTimeString(current_date, date) {
    var diff,
      abs,
      second = 1000,
      minute = second * 60,
      hour = minute * 60,
      day = hour * 24,
      week = day * 7,
      time_format = new Intl.RelativeTimeFormat();

    diff = date.getFullYear() - current_date.getFullYear();
    if (diff !== 0) {
      return time_format.format(diff, 'year');
    }

    diff = date - current_date;
    abs = Math.abs(diff);
    // "year", "quarter", "month", "week", "day", "hour", "minute", "second"
    console.log(current_date, date, abs, week, day);
    if (abs > (week * 2)) {
      return time_format.format(Math.floor(diff / week), 'week');
    } else if (abs > (day * 2)) {
      return time_format.format(Math.floor(diff / day), 'day');
    } else if (abs > (hour * 2)) {
      return time_format.format(Math.floor(diff / hour), 'hour');
    } else {
      return time_format.format(Math.floor(diff / minute), 'minute');
    }
    return date;
  }

  function buildFieldGadgetParam(value) {
    var field_gadget_param;

    if ((value !== undefined) && (value !== null) && (value.constructor === Object)) {
      if (value.field_gadget_param) {
        field_gadget_param = value.field_gadget_param;
      } else {
        field_gadget_param = {
          'editable': 0,
          'default': value.default
        };
      }
    } else {
      field_gadget_param = {
        'editable': 0,
        'default': value
      };
    }

    return field_gadget_param;
  }

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

        if (options.show_line_selector || (options.form_id === 'form_dialog' && options.show_select)) {
          if (j === 0) {
            // If first cell, show a checkbox to select the line
            sub_element = document.createElement('input');
            sub_element.setAttribute('data-uid', row.uid);
            sub_element.setAttribute('type', 'checkbox');
            sub_element.setAttribute('class', 'hide_element');
            sub_element.setAttribute('id', 'listbox_line_' + row.uid);
            if (row.checked) {
              sub_element.setAttribute('checked', 'checked');
            }
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
      "show_select": gadget.state.show_select,
      "form_id": gadget.state.form_id,
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
    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("getTranslationList", "getTranslationList")

    //////////////////////////////////////////////
    // initialize the gadget content
    //////////////////////////////////////////////
    .declareMethod('render', function render(options) {
      console.log(options);
      var gadget = this;

      // Cancel previous line rendering to not conflict with the asynchronous render for now
      gadget.fetchLineContent(true);

      return gadget.changeState({
        query_string: new URI(options.query).query(true).query || '',
        begin_from: 0,
        lines: options.lines || 1,
        // Force line calculation in any case
        render_timestamp: new Date().getTime(),
        allDocs_result: undefined
      });
    })

    .onStateChange(function onStateChange(modification_dict) {
      var gadget = this,
        allDocs_result;
      console.log(gadget.state);

      if (modification_dict.hasOwnProperty('render_timestamp')) {
        return gadget.fetchLineContent(false);
      }

      if (modification_dict.hasOwnProperty('allDocs_result')) {
        allDocs_result = JSON.parse(gadget.state.allDocs_result);
        return new RSVP.Queue(RSVP.all(
          allDocs_result.data.rows.map(function (entry) {
            return gadget.declareGadget('gadget_html_viewer.html')
              .push(function (viewer) {
                return viewer.render({value: entry.value.asStrippedHTML})
                  .push(function () {
                    return viewer;
                  });
              });
          })
        ))
          .push(function (viewer_list) {
            var now = new Date();
            domsugar(gadget.element, [
              domsugar('ol', allDocs_result.data.rows.map(function (entry, i) {
                var source_title = entry.value.source_title || '',
                  word_list = source_title.split(' '),
                  source_short_title;
                if (word_list.length === 1) {
                  source_short_title = (word_list[0][0] || '?') + (word_list[0][1] || '');
                } else {
                  source_short_title = word_list[0][0] + word_list[1][0];
                }
                return domsugar('li', [
                  domsugar('div', {
                    class: 'post_avatar',
                    text: source_short_title
                  }),
                  domsugar('div', {
                    class: 'post_content',
                  }, [
                    domsugar('strong', {text: source_title}),
                    " ",
                    domsugar('time', {
                      datetime: entry.value.modification_date,
                      title: entry.value.modification_date,
                      text: getRelativeTimeString(
                        now, new Date(entry.value.modification_date)
                      )
                    }),
                    domsugar('br'),
                    viewer_list[i].element,
                    // domsugar('hr')
                  ])
                ]);
              }))
            ]);
          });
        return;
      }
    }, function onStateChange(modification_dict) {
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
      if (modification_dict.hasOwnProperty('render_timestamp') &&
          (gadget.state.allDocs_result === undefined)) {
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
      }

      return result_queue;
    })

    .onLoop(function () {
      // update relative time
      var now = new Date();
      this.element.querySelectorAll("div.post_content > time").forEach(
        function (element) {
          element.textContent = getRelativeTimeString(
            now, new Date(element.getAttribute('datetime'))
          );
        }
      );
      // Loop every minute
    }, 1000 * 60)

    //////////////////////////////////////////////
    // render the listbox in an asynchronous way
    //////////////////////////////////////////////
    .declareJob('fetchLineContent', function fetchLineContent(only_cancel) {
      if (only_cancel) {
        return;
      }

      var gadget = this,
        limit_options = [],
        i;

      if (gadget.state.lines === 0) {
        limit_options = undefined;
      } else {
        limit_options = [gadget.state.begin_from, gadget.state.lines + 1];
      }

      return gadget.jio_allDocs({
        query: gadget.state.query_string,
        limit: limit_options,
        select_list: ['asStrippedHTML', 'modification_date',
                      'source_title'],
        sort_on: [['modification_date', 'ASC']]
      })
        .push(function (result) {
          return gadget.changeState({
            allDocs_result: JSON.stringify(result)
          });
        });
    })

    .declareMethod("getContent", function getContent() {
      return {};
    })

    .declareMethod("checkValidity", function checkValidity() {
      return true;
    });

}());
