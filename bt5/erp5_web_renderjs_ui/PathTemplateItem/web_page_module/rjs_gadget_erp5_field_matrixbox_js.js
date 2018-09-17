/*jslint indent: 2, maxerr: 3, nomen: true */
/*global window, document, rJS, RSVP, Handlebars, JSON*/
/** MatrixBox renders a N-dimensional cube of editable values based on axes description.
 *
 * Example JSON returned from HATEOAS where cell_range format is
 * [<column-labels> <line1> <line2> ... where
 *   <column-labels>: tuple (relative-url, title) (ex. [("sale_supply_module/1/3", "Sale Supply Line")])
 *   <lineN>: array of [label, values...]
 *
 * Example:
 *
  "matrixbox": {
    "title": "matrixbox",
    "css_class": "",
    "editable": 1,
    "data": [[
      [ <tabID>, "Col1 Title", "Col2 Title"],
      ["Row1 Title", <field_json>, null, null],
      ["50.0 <= Quantity < 100.0", , null, null], // example
    ]],
    "key": "field_matrixbox",
    "hidden": 0,
    "type": "MatrixBox"
  },

  where <field_json> consists of
    "field_id" - name of the template field for this cell
    "key" - key in REQUEST (without 'field_' prefix)
    "type" - meta type for RenderJS rendering
    "default" - default value to render
    "value" - current validated value

  see around https://lab.nexedi.com/nexedi/erp5/blob/feature/renderjs-matrixbox/product/ERP5Form/MatrixBox.py#L427
  *
  */
(function (window, document, rJS, RSVP, Handlebars, JSON) {
  "use strict";

  var gadget_klass = rJS(window),
    table_template_source = gadget_klass.__template_element
                                        .getElementById("table-template")
                                        .innerHTML,
    table_template = Handlebars.compile(table_template_source);

  /** Recursively introspect an object if it is empty */
  function is_empty_recursive(data) {
    var item;

    if (typeof data === 'object') {
      for (item in data) {
        if (data.hasOwnProperty(item) && !item.startsWith("_")) {
          if (is_empty_recursive(data[item]) === false) {return false; } // one non-empty element is enough
        }
      }
      return true;
    }
    return !data && true; // convert basic types to boolean
  }

  function copy(obj) {
    return JSON.parse(JSON.stringify(obj));
  }

  rJS(window)

    .ready(function () {
      this.props = {
        gadget_dict: {}  // holds references to initialized gadgets
      };
    })

    .setState({
      data: '',
      template_field_dict: '',
      editable: undefined,
      hidden: undefined,
      key: ''
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

    /** Render constructs and saves gadgets into `props.gadget_dict` if they don not exist yet. 
     */
    .declareMethod('render', function (options) {
      var gadget = this,
        element = gadget.element.querySelector('div.document_table'),
        data = options.field_json.data,
        // note we make COPY of data in their original form - important since
        // data.shift used later modify the structure inplace!
        new_state = {
          'data': JSON.stringify(options.field_json.data),
          'template_field_dict': JSON.stringify(options.field_json.template_field_dict),
          'editable': options.field_json.editable,
          'hidden': options.field_json.hidden,
          'key': options.field_json.key
        };

      if (is_empty_recursive(data)) {
        return;
      }

      if (!is_empty_recursive(gadget.props.gadget_dict)) {
        return this.changeState(new_state);
      }

      return new RSVP.Queue()
        .push(function () {
          return RSVP.all(data.map(function (table, table_index) {
            var header = table.shift(), // first item of table is the header
              table_title = header.shift(),  // first item of header is the table (tab) title
              table_body = document.createElement('tbody'),
              table_element = document.createElement('table');

            table_element.innerHTML = table_template({table_title: table_title, header: header});

            return new RSVP.Queue()
              .push(function () {
                return RSVP.all(table.map(function (row, row_index) {
                  var row_element = document.createElement('tr'),
                    row_id = new_state.key + "T" + table_index + "R" + row_index;

                  row.shift(); // drop the row label definition because it is not usable now
                  row_element.setAttribute('id', row_id);
                  row_element.appendChild(document.createElement('th'));

                  return new RSVP.Queue()
                    .push(function () {

                      return RSVP.all(row.map(function (column) {
                        // transform all cell-definitions into actual gadgets
                        var col_element = document.createElement('td');

                        return gadget.declareGadget('gadget_erp5_label_field.html', {
                          scope: column.key,
                          element: col_element,
                          sandbox: "public"
                        })
                          .push(function (sub_gadget) {
                            gadget.props.gadget_dict[column.key] = sub_gadget;
                            return col_element;
                          });
                      }));
                    })
                    .push(function (column_element_list) {
                      column_element_list.forEach(function (column_element) {
                        row_element.appendChild(column_element);
                      });
                      return row_element;
                    });
                }));
              })
              .push(function (row_element_list) {
                row_element_list.forEach(function (row_element) {
                  table_body.appendChild(row_element);
                });
                table_element.appendChild(table_body);
                return table_element;
              });
          }));
        })
        .push(function (table_element_list) {
          table_element_list.forEach(function (table_element) {
            element.appendChild(table_element);
          });
          return gadget.changeState(new_state);
        });
    })

    /** Changes state of existing gadgets inside `props.gadget_dict`. */
    .onStateChange(function (modification_dict) {
      var gadget = this,
        template_field_dict = JSON.parse(gadget.state.template_field_dict),
        promise_queue = new RSVP.Queue(),
        data;

      if (modification_dict.hasOwnProperty('data')) {
        data = JSON.parse(modification_dict.data);
        if (is_empty_recursive(data)) {
          return;
        }
        data.forEach(function (table, table_index) {
          table.shift(); // drop the header
          table.forEach(function (row, row_index) {
            var row_id = gadget.state.key + 'T' + table_index + 'R' + row_index,
              row_label_element = gadget.element.querySelector('tr#' + row_id + ' th');
            row_label_element.textContent = row.shift() || ''; // pop-up the row label from data

            // then handle all inputs within the row
            row.forEach(function (column) {
              promise_queue
                .push(function () {
                  // Rendering of embedded field is prescribed by another field
                  // in the form (usually in "hidden" group). Therefor we have a
                  // reference for the template field included in state (field)
                  var template_field = template_field_dict[column.field_id],
                    field_json = copy(template_field),
                    sub_gadget = gadget.props.gadget_dict[column.key];

                  // we copy (unknown) structure of template_field and carefully
                  // add known attributes from `column`
                  field_json.default = column.value;
                  field_json.key = "field_" + column.key;
                  field_json.hidden = gadget.state.hidden || template_field.hidden; // any hidden will hide the element
                  field_json.editable = gadget.state.editable && template_field.editable; // any non-editable will disable editation 
                  field_json.error_text = column.error_text;

                  return sub_gadget.render({
                    label: false,
                    field_type: column.type,
                    field_json: field_json
                  });
                });
            });
          });
        });
      } // end: if modification_dict.data
      return promise_queue;
    })

    .declareMethod("getContent", function (options) {
      var gadget = this,
        data = {},  // result dictionary with values
        field_key_list = [],
        field_key;

      function extendData(field_data) {
        var key;
        for (key in field_data) {
          if (field_data.hasOwnProperty(key) && !key.startsWith("_")) {
            data[key] = field_data[key];
          }
        }
      }

      for (field_key in gadget.props.gadget_dict) {
        if (gadget.props.gadget_dict.hasOwnProperty(field_key) && !field_key.startsWith("_")) {
          field_key_list.push(field_key);
        }
      }

      return new RSVP.Queue()
        .push(function () {
          return RSVP.all(field_key_list.map(function (field_key) {
            return gadget.props.gadget_dict[field_key].getContent(options);
          }));
        })
        .push(function (field_value_list) {
          field_value_list.forEach(extendData);
          return data;
        });
    })

    .allowPublicAcquisition("notifyInvalid", function () {
      return;
    })

    .allowPublicAcquisition("notifyValid", function () {
      return;
    })

    .declareMethod("checkValidity", function () {
      return true;
    });

}(window, document, rJS, RSVP, Handlebars, JSON));
