/*global window, rJS, document*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, document) {
  "use strict";

  rJS(window)

    .declareMethod("render", function (options) {
      return this.changeState({
        key: options.field_json.key,
        value: options.field_json.default,
        renderjs_extra: options.field_json.renderjs_extra,
        editable: options.field_json.editable,
        url: options.field_json.url,
        sandbox: options.field_json.sandbox || undefined,
        hidden: options.field_json.hidden,
        css_class: options.field_json.css_class
      });
    })

    .onStateChange(function (modification_dict) {
      var gadget = this;
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
          var render_kw;
          try {
            render_kw = JSON.parse(gadget.state.renderjs_extra);
          } catch (e) {
            render_kw = {};
          }
          render_kw.key = gadget.state.key;
          render_kw.value = gadget.state.value;
          render_kw.editable = gadget.state.editable;
          render_kw.hidden = gadget.state.hidden;
          return result.render(render_kw)
            .push(function () {
              var div;
              if (render_kw.maximize) {
                div = document.createElement('div');
                gadget.element.insertBefore(div, gadget.element.firstChild);
                return gadget.declareGadget(render_kw.maximize, {
                  scope: "maximize_button",
                  sandbox: 'public',
                  element: div
                })
                .push(function (maximize_button) {
                  return maximize_button.render({
                    target: gadget,
                    value: 'Maximize'
                  });
                });
              }
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
