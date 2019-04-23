/*global window, rJS, isEmpty, getFirstNonEmpty, ensureArray */
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */
(function (window, rJS, getFirstNonEmpty, ensureArray) {
  "use strict";

  function generateTextContent(value, item_list) {
    var i, text_content;
    for (i = 0; i < item_list.length; i += 1) {
      if (item_list[i][1] === value) {
        text_content = item_list[i][0];
      }
    }
    if (text_content === undefined) {
      text_content = '??? (' + value + ')';
    }
    return text_content;
  }

  rJS(window)
    .setState({
      tag: 'p'
    })

    .declareMethod('render', function (options) {
      var field_json = options.field_json || {},
        item_list = ensureArray(field_json.items).map(function (item) {
          if (Array.isArray(item)) {return item; }
          return [item, item];
        }),
        state_dict = {
          value: getFirstNonEmpty(field_json.value, field_json['default'], ""),
          editable: field_json.editable,
          item_list: JSON.stringify(item_list),
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
      if (isEmpty(state_dict.value) &&
          state_dict.first_item &&
          !isEmpty(field_json.items)) {
        state_dict.value = field_json.items[0][1];
      }
      return this.changeState(state_dict);
    })

    .onStateChange(function (modification_dict) {
      var element = this.element,
        url,
        result,
        i,
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
          state.text_content =
            generateTextContent(this.state.value, state.item_list);
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
        if (!this.state.editable) {
          state.text_content =
            generateTextContent(this.state.value, state.item_list);
        }
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

}(window, rJS, getFirstNonEmpty, ensureArray));