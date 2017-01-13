/*jslint indent: 2, maxerr: 3, nomen: true */
/*global window, rJS, RSVP, document */
(function (window, rJS, RSVP, document) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (gadget) {
      gadget.props = {};
      return gadget.getElement()
        .push(function (element) {
          gadget.props.element = element;
        });
    })
    .allowPublicAcquisition("addRelationInput", function () {
      var fieldset = document.createElement("fieldset"),
        gadget = this,
        container = gadget.props.element.querySelector('.container');
      return gadget.declareGadget('gadget_erp5_relation_input.html', {
        element: fieldset
      })
        .push(function (relation_input) {
          var field_json = gadget.props.field_json,
            index;
          if (field_json.default.value) {
            index = field_json.default.relation_item_relative_url.length;
            field_json.default.relation_item_relative_url.push('');
            field_json.default.value.push('');
          } else {
            index = field_json.relation_item_relative_url.length;
            field_json.relation_item_relative_url.push('');
            field_json.default.push('');
          }
          gadget.props.gadget_list.push(relation_input);
          return relation_input.render({field_json: gadget.props.field_json}, {
            index: index,
            addRelationInput: true
          });
        })
        .push(function () {
          container.appendChild(fieldset);
        });
    })

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function (options) {
      var gadget = this,
        i,
        list = [],
        fieldset,
        container = gadget.props.element.querySelector('.container'),
        field_json = options.field_json || {},
        relation_item_relative_url;
      gadget.props.field_json = field_json;
      if (field_json.default.value) {
        if (field_json.default.relation_item_relative_url[field_json.default.relation_item_relative_url.length - 1]) {
          //return form listbox
          field_json.default.value.push("");
          field_json.default.relation_item_relative_url.push("");
        }
        relation_item_relative_url = field_json.default.relation_item_relative_url;
      } else {
        field_json.relation_item_relative_url.push('');
        field_json.default.push('');
        relation_item_relative_url = field_json.relation_item_relative_url;
      }
      for (i = 0; i < relation_item_relative_url.length; i += 1) {
        fieldset = document.createElement("fieldset");
        container.appendChild(fieldset);
        list.push(gadget.declareGadget('gadget_erp5_relation_input.html', {
          element: fieldset
        }));
      }
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all(list);
        })
        .push(function (gadget_list) {
          list = [];
          gadget.props.gadget_list = gadget_list;
          for (i = 0; i < gadget_list.length; i += 1) {
            list.push(gadget_list[i].render(options, {
              index: i,
              addRelationInput: (i === gadget_list.length - 1)
            }));
          }
          return RSVP.all(list);
        });
    })
    .declareMethod('getContent', function (options) {
      var list = [],
        i,
        gadget = this,
        length = gadget.props.gadget_list.length;
      if (options.format === 'erp5') {
        length -= 1;
      }
      for (i = 0; i < length; i += 1) {
        list.push(gadget.props.gadget_list[i].getContent(options, {"type": "MultiRelationField"}));
      }
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all(list);
        })
        .push(function (result) {
          var tmp = {},
            key,
            key1;
          for (i = 0; i < result.length; i += 1) {
            for (key in result[i]) {
              if (result[i].hasOwnProperty(key)) {
                if (options.format === 'erp5') {
                  if (tmp[key] === undefined) {
                    tmp[key] = [];
                  }
                  tmp[key].push(result[i][key]);
                } else {
                  if (tmp[key] === undefined) {
                    tmp[key] = {};
                  }
                  for (key1 in result[i][key]) {
                    if (result[i][key].hasOwnProperty(key1)) {
                      if (tmp[key][key1] === undefined) {
                        tmp[key][key1] = [];
                      }
                      tmp[key][key1].push(result[i][key][key1][0]);
                    }
                  }
                }
              }
            }
          }
          return tmp;
        });
    });
}(window, rJS, RSVP, document));