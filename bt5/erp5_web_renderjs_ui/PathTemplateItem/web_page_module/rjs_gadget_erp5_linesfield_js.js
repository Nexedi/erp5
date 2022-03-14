/*global window, rJS */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  function listToNewlines(lines) {
    if (Array.isArray(lines)) {return lines.join("\n"); }
    return lines;
  }

  rJS(window)
    .setState({
      gadget_rendered: false
    })

    .declareMethod('render', function (options) {
      var gadget = this,
        new_state = {
          "default": listToNewlines(options.field_json.default),
          "editable": options.field_json.editable,
          "required": options.field_json.required,
          "hidden": options.field_json.hidden,
          "title": options.field_json.description,
          "key": options.field_json.key,
          // Force calling subfield render
          // as user may have modified the input value
          render_timestamp: new Date().getTime()
        };

      if (this.state.gadget_rendered === false) {
        return gadget.declareGadget("gadget_erp5_field_textarea.html", {scope: 'sub'})
          .push(function (subgadget) {
            gadget.element.appendChild(subgadget.element);
            new_state.gadget_rendered = true;
            return gadget.changeState(new_state);
          });
      }
      return this.changeState(new_state);
    })

    .onStateChange(function () {
      var gadget = this;
      return this.getDeclaredGadget('sub')
        .push(function (subgadget) {
          return subgadget.render({field_json: gadget.state});
        });
    })

    .declareMethod('getContent', function () {
      return this.getDeclaredGadget('sub')
        .push(function (sub_gadget) {
          return sub_gadget.getContent();
        });
    })

    .declareMethod('checkValidity', function () {
      if (!this.state.editable) {
        return true;
      }
      return this.getDeclaredGadget('sub')
        .push(function (subgadget) {
          return subgadget.checkValidity();
        });
    });

}(window, rJS));