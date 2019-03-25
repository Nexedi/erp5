/*global window, rJS, document, RSVP*/
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80, unparam: true */
(function (window, rJS, document, RSVP) {
  'use strict';

  function appendListField(gadget, value, item_list) {
    var div = document.createElement('div');
    gadget.element.appendChild(div);
    return new RSVP.Queue()
      .push(function () {
        return gadget.declareGadget('gadget_erp5_field_list.html',
                                    {element: div});
      })
      .push(function (result) {
        var state = {
            value: value,
            items: item_list,
            editable: gadget.state.editable,
            // Single listfield is never mandatory.
            // Check requirement globally instead
            required: 0,
            key: 'sub',
            title: gadget.state.title,
            hidden: gadget.state.hidden
          };
        return result.render({field_json: state});
      });
  }

  rJS(window)
    .declareMethod('render', function (options) {
      var field_json = options.field_json || {},
        item_list = field_json.items,
        state_dict = {
          value_list: JSON.stringify(field_json.value ||
                                     field_json.default || []),
          editable: field_json.editable,
          required: field_json.required,
          name: field_json.key,
          title: field_json.title,
          sub_select_key: field_json.sub_select_key,
          sub_input_key: field_json.sub_input_key,
          hidden: field_json.hidden
        };
      if ((item_list.length === 0) || (item_list[0][0] !== "")) {
        item_list.unshift(["", ""]);
      }
      state_dict.item_list = JSON.stringify(item_list);
      return this.changeState(state_dict);
    })

    .onStateChange(function () {
      var i,
        value_list = JSON.parse(this.state.value_list),
        item_list = JSON.parse(this.state.item_list),
        queue = new RSVP.Queue(),
        element = this.element,
        gadget = this;

      // Always display an empty value at the end
      value_list.push("");

      // Clear first to DOM, append after to reduce flickering/manip
      while (element.firstChild) {
        element.removeChild(element.firstChild);
      }

      function enQueue() {
        var argument_list = arguments;
        queue
          .push(function () {
            return appendListField.apply(this, argument_list);
          });
      }

      for (i = 0; i < value_list.length; i += 1) {
        enQueue(gadget, value_list[i], item_list);
      }
      return queue;
    })

    .declareMethod('getContent', function () {
      var i,
        element = this.element,
        queue = new RSVP.Queue(),
        final_result = {},
        result_list = [],
        gadget = this;

      function calculateSubContent(node) {
        queue
          .push(function () {
            var scope = node.getAttribute('data-gadget-scope');
            if (scope !== null) {
              return gadget.getDeclaredGadget(
                node.getAttribute('data-gadget-scope')
              )
                .push(function (result) {
                  return result.getContent();
                })
                .push(function (result) {
                  result_list.push(result.sub);
                });
            }
          });
      }

      if (this.state.editable) {
        for (i = 0; i < element.childNodes.length; i += 1) {
          calculateSubContent(element.childNodes[i]);
        }
        return queue
          .push(function () {
            final_result[gadget.state.sub_select_key] = result_list;
            final_result[gadget.state.sub_input_key] = 0;
            return final_result;
          });
      }
      return final_result;
    })

    .allowPublicAcquisition('notifyValid', function () {
      return;
    })

    .declareAcquiredMethod("notifyValid", "notifyValid")
    .declareAcquiredMethod("notifyInvalid", "notifyInvalid")
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .allowPublicAcquisition('notifyChange', function (argument_list, scope) {
      // An empty listfield should be created when the last one is modified
      // An empty listfield should be removed

      var gadget = this,
        sub_gadget;
      return gadget.getDeclaredGadget(scope)
        .push(function (result) {
          sub_gadget = result;
          return sub_gadget.getContent();
        })
        .push(function (result) {
          var value = result.sub;
          if (sub_gadget.element === gadget.element.lastChild) {
            if (value) {
              return appendListField(gadget, "",
                                     JSON.parse(gadget.state.item_list));
            }
          } else {
            if (!value) {
              gadget.element.removeChild(sub_gadget.element);
            }
          }
        })
        .push(function () {
          $(gadget.element).enhanceWithin();    
          return gadget.notifyChange();
        });
    })

    .declareMethod('checkValidity', function () {
      var gadget = this,
        empty = true;
      if (this.state.editable && this.state.required) {
        return this.getContent()
          .push(function (result) {
            var value_list = result[gadget.state.sub_select_key],
              i;
            for (i = 0; i < value_list.length; i += 1) {
              if (value_list[i]) {
                empty = false;
              }
            }
            if (empty) {
              return gadget.notifyInvalid("Please fill out this field.");
            }
            return gadget.notifyValid();
          })
          .push(function () {
            return !empty;
          });
      }
      return true;
    });

}(window, rJS, document, RSVP));