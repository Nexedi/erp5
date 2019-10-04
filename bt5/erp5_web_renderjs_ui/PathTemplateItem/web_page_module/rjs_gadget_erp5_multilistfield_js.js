/*global window, rJS, document, RSVP, isEmpty, ensureArray */
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80, unparam: true */
(function (window, rJS, document, RSVP, isEmpty, ensureArray, getFirstNonEmpty) {
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
            key: gadget.state.key,
            title: gadget.state.title,
            hidden: gadget.state.hidden
          };
        return result.render({field_json: state});
      });
  }

  rJS(window)
    .declareAcquiredMethod("translate", "translate")
    .declareMethod('render', function (options) {
      var field_json = options.field_json || {},
        item_list = ensureArray(field_json.items).map(function (item) {
          if (Array.isArray(item)) {return item; }
          else {return [item, item]; }
        }),
        state_dict = {
          value_list: JSON.stringify(
            ensureArray(
              getFirstNonEmpty(field_json.value, field_json['default'], []))
          ),
          editable: field_json.editable,
          required: field_json.required,
          name: field_json.key,
          title: field_json.title,
          key: field_json.key,
          sub_select_key: field_json.sub_select_key,
          sub_input_key: field_json.sub_input_key,
          hidden: field_json.hidden,
          // Force calling subfield render
          // as user may have modified the input value
          render_timestamp: new Date().getTime()
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

      value_list.forEach(function (value) {
        queue
          .push(function () {
            return appendListField(gadget, value, item_list);
          });
      });

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
                  result_list.push(result[gadget.state.key]);
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
            if (result_list[result_list.length - 1] === "") {
              result_list.pop();
            }
            final_result[gadget.state.key] = result_list;
            // Automatically add default_%s:int:0
            //   https://lab.nexedi.com/nexedi/erp5/blob/8ae0706177/product/Formulator/Widget.py#L1185
            final_result["default_" + gadget.state.key + ":int"] = 0;
            final_result[gadget.state.sub_select_key] = result_list;
            final_result[gadget.state.sub_input_key] = 0;
            return final_result;
          });
      }
      return final_result;
    }, {mutex: 'changestate'})

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
          var value = result[gadget.state.key];
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
          return gadget.notifyChange();
        });
    })

    .declareMethod('checkValidity', function () {
      var gadget = this,
        empty = true;
      if (this.state.editable && this.state.required) {
        return new RSVP.Queue()
          .push(function () {
            return RSVP.all([
              gadget.getContent(),
              gadget.translate("Input is required but no input given.")
            ]);
          })
          .push(function (all_result) {
            var value_list = all_result[0][gadget.state.sub_select_key],
              error_message = all_result[1],
              i;
            for (i = 0; i < value_list.length; i += 1) {
              if (value_list[i]) {
                empty = false;
              }
            }
            if (empty) {
              return gadget.notifyInvalid(error_message);
            }
            return gadget.notifyValid();
          })
          .push(function () {
            return !empty;
          });
      }
      return true;
    });

}(window, rJS, document, RSVP, isEmpty, ensureArray, getFirstNonEmpty));