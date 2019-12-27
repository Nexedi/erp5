/*global window, rJS, RSVP, document*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, document) {
  'use strict';

  function appendCheckboxField(gadget, item, checked) {
    var input_gadget,
      label_gadget;
    if (!gadget.state.editable) {
      if (checked) {
        return gadget.declareGadget('gadget_html5_element.html')
          .push(function (result) {
            label_gadget = result;
            return result.render({
              tag: 'p',
              text_content: item[0]
            });
          })
          .push(function () {
            gadget.element.appendChild(label_gadget.element);
          });
      }
      return;
    }

    return gadget.declareGadget('gadget_html5_input.html', {
      scope: item[1],
      element: 'span'
    })
      .push(function (result) {
        input_gadget = result;
        var state_dict = {
          type: 'checkbox',
          name: gadget.state.name,
          value: item[1],
          checked: checked,
          editable: true,
          hidden: gadget.state.hidden
        };

        return result.render(state_dict);
      })
      .push(function () {
        var div = document.createElement("div"),
          label = document.createElement("label"),
          text_node = document.createTextNode(item[0]);
        label.appendChild(input_gadget.element);
        label.appendChild(text_node);
        div.appendChild(label);
        gadget.element.appendChild(div);
      });
  }

  rJS(window)

    .declareMethod('render', function (options) {
      var field_json = options.field_json || {},
        state_dict = {
          editable: field_json.editable,
          name: field_json.key,
          item_list: field_json.items,
          value_list: field_json.value || field_json.default,
          hidden: field_json.hidden,
          // Force calling subfield render
          // as user may have modified the input value
          render_timestamp: new Date().getTime()
        };

      return this.changeState(state_dict);
    })

    .onStateChange(function () {
      var element = this.element,
        gadget = this,
        value_list = this.state.value_list,
        value_dict = {},
        item_list = this.state.item_list,
        i,
        queue;

      // Clear first to DOM, append after to reduce flickering/manip
      while (element.firstChild) {
        element.removeChild(element.firstChild);
      }

      if (typeof value_list === 'string') {
        value_list = [value_list];
      }
      for (i = 0; i < value_list.length; i += 1) {
        value_dict[value_list[i]] = null;
      }

      function enQueue() {
        var argument_list = arguments;
        queue
          .push(function () {
            return appendCheckboxField.apply(this, argument_list);
          });
      }

      queue = new RSVP.Queue();

      for (i = 0; i < item_list.length; i += 1) {
        enQueue(gadget, item_list[i], value_dict.hasOwnProperty(item_list[i][1]));
      }

      return queue;
    })

    .declareMethod('getContent', function () {
      var i,
        queue = new RSVP.Queue(),
        final_result = {},
        result_list = [],
        gadget = this;

      function calculateSubContent(scope) {
        queue
          .push(function () {
            return gadget.getDeclaredGadget(scope)
              .push(function (result) {
                return result.getContent();
              })
              .push(function (result) {
                result_list.push(result);
              });
          });
      }

      if (this.state.editable) {
        for (i = 0; i < gadget.state.item_list.length; i += 1) {
          calculateSubContent(gadget.state.item_list[i][1]);
        }

        return queue
          .push(function () {
            var j,
              value_list = [];
            for (j = 0; j < result_list.length; j += 1) {
              if (result_list[j][gadget.state.name]) {
                value_list.push(gadget.state.item_list[j][1]);
              }
            }
            final_result[gadget.state.name] = value_list;
            // Automatically add default_%s:int:0
            //   https://lab.nexedi.com/nexedi/erp5/blob/8ae0706177/product/Formulator/Widget.py#L1273
            final_result["default_" + gadget.state.name + ":int"] = 0;
            return final_result;
          });
      }
      return final_result;
    }, {mutex: 'changestate'})

    .declareMethod('checkValidity', function () {
      var name = this.state.name;
      if (this.state.editable && this.state.required) {
        return this.getContent()
          .push(function (result) {
            return result[name].length !== 0;
          });
      }
      return true;
    });

}(window, rJS, RSVP, document));