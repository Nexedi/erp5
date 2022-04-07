/*jslint indent: 2, maxerr: 3, nomen: true */
/*global window, rJS, RSVP, domsugar, JSON*/
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
(function (window, rJS, RSVP, domsugar, JSON) {
  "use strict";
/*
  // Recursively introspect an object if it is empty
  function isEmptyRecursive(data) {
    var item;

    if (typeof data === 'object') {
      for (item in data) {
        if (data.hasOwnProperty(item) && !item.startsWith("_")) {
          if (isEmptyRecursive(data[item]) === false) {return false; } // one non-empty element is enough
        }
      }
      return true;
    }
    return !data && true; // convert basic types to boolean
  }
*/
  function copy(obj) {
    return JSON.parse(JSON.stringify(obj));
  }

  rJS(window)

    .setState({
      data: '',
      template_field_dict: '',
      editable: undefined,
      hidden: undefined,
      key: ''
    })

    .declareMethod('render', function (options) {
      return this.changeState({
        'table_list': JSON.stringify(options.field_json.data),
        'template_field_dict': JSON.stringify(options.field_json.template_field_dict),
        'editable': options.field_json.editable,
        'hidden': options.field_json.hidden,
        'key': options.field_json.key
      });
    }, {mutex: 'render'})

    .onStateChange(function () {
      var gadget = this,
        template_field_dict = JSON.parse(gadget.state.template_field_dict),
        table_list = JSON.parse(gadget.state.table_list);

      return new RSVP.Queue(RSVP.all(table_list.map(function (table,
                                                              table_index) {
        // first item of table is the header
        var header_list = table.shift(),
          // first item of header is the table (tab) title
          table_title = header_list.shift();

        return new RSVP.Queue(RSVP.all(table.map(function (row, row_index) {
          // drop the row label definition because it is not usable now
          var row_label = row.shift();

          return new RSVP.Queue(RSVP.all(row.map(function (column) {
            // transform all cell-definitions into actual gadgets
            return gadget.declareGadget('gadget_erp5_label_field.html', {
              scope: column.key,
              element: 'td',
              sandbox: "public"
            })
              .push(function (sub_gadget) {
                // Rendering of embedded field is prescribed by another field
                // in the form (usually in "hidden" group). Therefor we have a
                // reference for the template field included in state (field)
                var template_field = template_field_dict[column.field_id],
                  field_json = copy(template_field);

                // we copy (unknown) structure of template_field and carefully
                // add known attributes from `column`
                field_json['default'] = column.value;
                field_json.key = "field_" + column.key;
                field_json.hidden = gadget.state.hidden || template_field.hidden; // any hidden will hide the element
                field_json.editable = gadget.state.editable && template_field.editable; // any non-editable will disable editation 
                field_json.error_text = column.error_text;

                return RSVP.hash({
                  _: sub_gadget.render({
                    label: false,
                    development_link: false,
                    field_type: column.type,
                    field_json: field_json
                  }),
                  sub_gadget: sub_gadget
                });
              })
              .push(function (hash) {
                return hash.sub_gadget.element;
              });
          })))
            .push(function (column_element_list) {
              // return row_element
              return domsugar('tr', {
                id: gadget.state.key + "T" + table_index + "R" + row_index
              }, [
                domsugar('th', {text: row_label}),
                domsugar(null, column_element_list)
              ]);

            });
        })))
          .push(function (row_element_list) {
            var th_dom_list = [
              domsugar('th', {text: table_title})
            ],
              i;
            for (i = 0; i < header_list.length; i += 1) {
              // XXX used to be html instead of text
              // But as unsecure, try to restrict
              th_dom_list.push(domsugar('th', {text: header_list[i]}));
            }
            return domsugar('table', [
              domsugar('thead', [
                domsugar('tr', th_dom_list)
              ]),
              domsugar('tbody', row_element_list)
            ]);
          });
      })))
        .push(function (table_element_list) {
          domsugar(gadget.element.querySelector('div.document_table'),
                   table_element_list);
        });
    })

    .declareMethod("getContent", function (options) {
      var gadget = this,
        table_list = JSON.parse(gadget.state.table_list),
        promise_list = [],
        // result dictionary with values
        result_dict = {};

      table_list.map(function (table) {
        // first item of table is the header
        table.shift();

        table.map(function (row) {
          // drop the row label definition because it is not usable now
          row.shift();

          row.map(function (column) {
            var field_key = column.key;
            if (field_key.startsWith("_")) {
              return;
            }
            promise_list.push(
              gadget.getDeclaredGadget(field_key)
                .push(function (sub_gadget) {
                  return sub_gadget.getContent(options);
                })
                .push(function (field_data) {
                  var key;
                  for (key in field_data) {
                    if (field_data.hasOwnProperty(key) && !key.startsWith("_")) {
                      result_dict[key] = field_data[key];
                    }
                  }
                })
            );
          });
        });
      });

      return new RSVP.Queue(RSVP.all(promise_list))
        .push(function () {
          return result_dict;
        });
    }, {mutex: 'render'})

    .allowPublicAcquisition("notifyInvalid", function () {
      return;
    })

    .allowPublicAcquisition("notifyValid", function () {
      return;
    })

    .declareMethod("checkValidity", function () {
      return true;
    }, {mutex: 'render'});

}(window, rJS, RSVP, domsugar, JSON));
