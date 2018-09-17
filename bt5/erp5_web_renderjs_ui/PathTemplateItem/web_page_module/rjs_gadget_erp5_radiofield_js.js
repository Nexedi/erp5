/*global window, rJS, RSVP, document */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  function appendCheckboxField(gadget, item) {
    var input_gadget,
      label_gadget;
    return gadget.declareGadget('gadget_html5_input.html', {scope: item[1]})
      .push(function (result) {
        input_gadget = result;
        var state_dict = {
          type: 'radio',
          name: gadget.state.name,
          value: item[1],
          editable: true,
          hidden: gadget.state.hidden
        };
        if (item[1] === gadget.state.value) {
          state_dict.checked = 1;
        }
        return result.render(state_dict);
      })
      .push(function () {
        return gadget.declareGadget('gadget_html5_element.html');
      })
      .push(function (result) {
        label_gadget = result;
        var state_dict = {
          tag: 'label',
          text_content: item[0]
        };
        return result.render(state_dict);
      })
      .push(function () {
        var div = document.createElement("div");
        div.setAttribute("class", "ui-field-contain");
        div.appendChild(label_gadget.element);
        div.appendChild(input_gadget.element);
        gadget.element.appendChild(div);
      });
  }

  rJS(window)

    .declareMethod('render', function (options) {
      var field_json = options.field_json || {},
        state_dict = {
          value: field_json.value || field_json.default,
          select_first_item: field_json.select_first_item,
          required: field_json.required,
          editable: field_json.editable,
          name: field_json.key,
          title: field_json.title,
          item_list: field_json.items,
          hidden: field_json.hidden,
          // Force calling subfield render
          // as user may have modified the input value
          render_timestamp: new Date().getTime()
        };

      //the first item will always be selected if no initial default value is supplied.
      if (state_dict.value === "" && state_dict.select_first_item) {
        state_dict.value = state_dict.item_list[0][1];
      }

      return this.changeState(state_dict);
    })

    .onStateChange(function () {
      var element = this.element,
        gadget = this,
        value = this.state.value,
        item_list = this.state.item_list,
        i,
        sub_gadget,
        queue;

      // Clear first to DOM, append after to reduce flickering/manip
      while (element.firstChild) {
        element.removeChild(element.firstChild);
      }

      function enQueue() {
        var argument_list = arguments;
        queue
          .push(function () {
            return appendCheckboxField.apply(this, argument_list);
          });
      }

      if (gadget.state.editable) {
        queue = new RSVP.Queue();

        for (i = 0; i < item_list.length; i += 1) {
          enQueue(gadget, item_list[i]);
        }

      } else {
        queue = gadget.declareGadget('gadget_html5_element.html', {scope: 'sub'})
          .push(function (result) {
            sub_gadget = result;
            var text_content = "";

            for (i = 0; i < item_list.length; i += 1) {
              if (item_list[i][1] === value) {
                text_content = item_list[i][0];
              }
            }
            return sub_gadget.render({
              text_content: text_content,
              tag: 'p'
            });
          })
          .push(function () {
            element.appendChild(sub_gadget.element);
          });
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
            // Automatically add default_%s:
            //   https://lab.nexedi.com/nexedi/erp5/blob/8ae0706177/product/Formulator/Widget.py#L1226
            var j;
            for (j = 0; j < result_list.length; j += 1) {
              if (result_list[j].hasOwnProperty(gadget.state.name)) {
                result_list[j]["default_" + gadget.state.name] = "";
                return result_list[j];
              }
            }
            j = {};
            j["default_" + gadget.state.name] = "";
            return j;
          });
      }
      return final_result;
    }, {mutex: 'changestate'})

    .declareMethod('checkValidity', function () {
      var name = this.state.name;
      if (this.state.editable && this.state.required) {
        return this.getContent()
          .push(function (result) {
            return !result[name];
          });
      }
      return true;
    });
}(window, rJS, RSVP));