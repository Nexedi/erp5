/*global window, rJS, document*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, document) {
  "use strict";

  rJS(window)

    .declareMethod("render", function (options) {
      return this.changeState({
        key: options.field_json.key,
        value: options.field_json.default,
        editable: options.field_json.editable,
        url: options.field_json.url,
        sandbox: options.field_json.sandbox || undefined,
        hidden: options.field_json.hidden,
        css_class: options.field_json.css_class
      });
    })

    .onStateChange(function (modification_dict) {
      // Check if a sub gadget has to be regenerated
      if ((modification_dict.hasOwnProperty('url')) ||
          (modification_dict.hasOwnProperty('sandbox')) ||
          (modification_dict.hasOwnProperty('key'))) {
        return this.deferDeclareGadget();
      }
      return this.deferRenderGadget();
    })

    .declareJob('deferDeclareGadget', function () {
      var div = document.createElement('div'),
        element = this.element,
        gadget = this;
      if (gadget.state.css_class) {
        element.setAttribute("class", gadget.state.css_class);
      }

      // Clear first to DOM, append after to reduce flickering/manip
      while (element.firstChild) {
        element.removeChild(element.firstChild);
      }
      element.appendChild(div);

      return gadget.declareGadget(gadget.state.url, {
        scope: gadget.state.key,
        sandbox: gadget.state.sandbox,
        element: div
      })
        .push(function () {
          return gadget.deferRenderGadget();
        });
    })

    .declareJob('deferRenderGadget', function () {
      var gadget = this;
      return gadget.getDeclaredGadget(gadget.state.key)
        .push(function (result) {
          return result.render({
            key: gadget.state.key,
            value: gadget.state.value,
            editable: gadget.state.editable,
            hidden: gadget.state.hidden
          });
        });
    })

    .declareMethod("getContent", function () {
      var gadget = this;
      if (!gadget.state.editable) {
        return {};
      }
      return gadget.getDeclaredGadget(gadget.state.key)
        .push(function (result) {
          return result.getContent();
        });
    });

}(window, rJS, document));
