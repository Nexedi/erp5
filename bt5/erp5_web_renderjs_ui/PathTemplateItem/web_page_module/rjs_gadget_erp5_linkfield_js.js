/*global window, document, rJS */
/*jslint indent: 2, maxerr: 3 */
(function (window, document, rJS) {
  "use strict";

  rJS(window)
    .setState({
      tag: 'a'
    })

    .declareMethod('render', function (options) {
      var field_json = options.field_json || {},
        state_dict = {
          value: field_json.value || field_json.default || "",
          editable: field_json.editable,
          required: field_json.required,
          id: field_json.key,
          name: field_json.key,
          error_text: field_json.error_text,
          title: field_json.description,
          label: field_json.title,
          hidden: field_json.hidden,
          trim: true,
          // Force calling subfield render
          // as user may have modified the input value
          render_timestamp: new Date().getTime()
        };
      return this.changeState(state_dict);
    })

    .onStateChange(function (modification_dict) {
      var element = this.element,
        gadget = this,
        url,
        result,
        new_div;
      if (modification_dict.hasOwnProperty('editable')) {
        if (gadget.state.editable) {
          url = 'gadget_html5_input.html';
        } else {
          url = 'gadget_html5_element.html';
        }
        while (element.firstChild) {
          element.removeChild(element.firstChild);
        }
        new_div = document.createElement('div');
        element.appendChild(new_div);
        result = this.declareGadget(url, {scope: 'sub', element: new_div});
      } else {
        result = this.getDeclaredGadget('sub');
      }
      return result
        .push(function (input) {
          var state;
          if (gadget.state.editable) {
            state = gadget.state;
          } else {
            state = {
              tag: 'a',
              href: gadget.state.value,
              text_content: gadget.state.label
            };
          }
          return input.render(state);
        });
    })

    /** Return content even for non-editable cells - be backward compatible! */
    .declareMethod('getContent', function () {
      if (this.state.editable) {
        return this.getDeclaredGadget('sub')
          .push(function (gadget) {
            return gadget.getContent();
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

}(window, document, rJS));