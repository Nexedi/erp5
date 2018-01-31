/*global window, rJS, isEmpty, getFirstNonEmpty */
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */
(function (window, rJS, getFirstNonEmpty) {
  "use strict";

  rJS(window)
    .setState({
      tag: 'p'
    })

    .declareMethod('render', function (options) {
      var field_json = options.field_json || {},
        state_dict = {
          value: getFirstNonEmpty(field_json.value, field_json['default'], ""),
          item_list: JSON.stringify(field_json.items),
          editable: field_json.editable,
          required: field_json.required,
          name: field_json.key,
          title: field_json.title,
          first_item: field_json.first_item,
          hidden: field_json.hidden,
          // Force calling subfield render
          // as user may have modified the input value
          render_timestamp: new Date().getTime()
        };
      // first_item means to select the first item by default on empty value
      if (isEmpty(state_dict.value) && (state_dict.first_item)) {
        state_dict.value = field_json.items[0][1];
      }
      return this.changeState(state_dict);
    })

    .onStateChange(function (modification_dict) {
      var element = this.element,
        url,
        result,
        i,
        text_content,
        item_list,
        state = {};

      for (i in this.state) {
        if (this.state.hasOwnProperty(i)) {
          state[i] = this.state[i];
        }
      }
      state.item_list = JSON.parse(this.state.item_list);

      if (modification_dict.hasOwnProperty('editable')) {
        if (this.state.editable) {
          url = 'gadget_html5_select.html';
        } else {
          url = 'gadget_html5_element.html';

          item_list = state.item_list;
          for (i = 0; i < item_list.length; i += 1) {
            if (item_list[i][1] === this.state.value) {
              text_content = item_list[i][0];
            }
          }
          if (text_content === undefined) {
            text_content = '??? (' + this.state.value + ')';
          }
          state.text_content = text_content;

        }
        result = this.declareGadget(url, {scope: 'sub'})
          .push(function (input) {
            // Clear first to DOM, append after to reduce flickering/manip
            while (element.firstChild) {
              element.removeChild(element.firstChild);
            }
            element.appendChild(input.element);
            return input;
          });
      } else {
        result = this.getDeclaredGadget('sub');
      }
      return result
        .push(function (input) {
          return input.render(state);
        });
    })

    .declareMethod('getContent', function () {
      if (this.state.editable) {
        return this.getDeclaredGadget('sub')
          .push(function (gadget) {
            return gadget.getContent();
          })
          .push(function (result) {
            // Automatically add default_%s:int:0
            //   https://lab.nexedi.com/nexedi/erp5/blob/8ae0706177/product/Formulator/Widget.py#L1147
            var key_list = Object.keys(result), i;
            for (i = 0; i < key_list.length; i += 1) {
              result["default_" + key_list[i] + ":int"] = 0;
            }
            return result;
          });
      }
      return {};
    }, {mutex: 'changestate'})

    .declareMethod('checkValidity', function () {
      if (this.state.editable) {
        return this.getDeclaredGadget('sub')
          .push(function (gadget) {
            return gadget.checkValidity();
          });
      }
      return true;
    }, {mutex: 'changestate'});

}(window, rJS, getFirstNonEmpty));