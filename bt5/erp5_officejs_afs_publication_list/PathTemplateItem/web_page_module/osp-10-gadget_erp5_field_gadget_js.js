/*global window, rJS, RSVP*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  function enqueueRender(gadget, options) {
    var loop_deferred = gadget.props.loop_defer,
      new_loop_deferred = RSVP.defer();

    gadget.props.loop_defer = new_loop_deferred;

    gadget.props.render_queue
      .push(function () {
        return gadget.props.service_deferred.promise;
      })
      .push(function (field_gadget) {
        return field_gadget.render(options);
      })
      .push(function () {
        return new_loop_deferred.promise;
      });
    loop_deferred.resolve();
  }

  rJS(window)
    .ready(function (g) {
      var loop_defer = RSVP.defer();
      g.props = {
        service_deferred: RSVP.defer(),
        first_render_deferred: RSVP.defer(),
        render_queue: new RSVP.Queue(),
        loop_defer: loop_defer
      };
      g.props.render_queue
        .push(function () {
          return loop_defer.promise;
        });
    })
    // Assign the element to a variable
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var gadget = this;

      enqueueRender(gadget, {
        key: options.field_json.key,
        value: options.field_json.default,
        editable: options.field_json.editable
      });
      gadget.props.first_render_deferred.resolve(options.field_json);
    })

    .declareMethod("getContent", function () {
      return this.props.field_gadget.getContent();
    })

    .declareService(function () {
      // Add the field in the DOM after the first render method has been called
      var gadget = this,
        gadget_element = gadget.props.element.querySelector('div'),
        field_json;
      return new RSVP.Queue()
        .push(function () {
          return gadget.props.first_render_deferred.promise;
        })
        .push(function (result) {
          field_json = result;
          return gadget.declareGadget(field_json.url, {
            scope: field_json.key,
            sandbox: field_json.sandbox || undefined,
            element: gadget_element
          });
        })
        .push(function (field_gadget) {
          var iframe;
          if (field_json.css_class) {
            gadget_element.setAttribute("class", field_json.css_class);
          }
          if (field_json.sandbox === "iframe") {
            iframe = gadget_element.querySelector("iframe");
            iframe.style.width = "100%";
            iframe.style.height = "100%";
          }
          // Trigger render methods
          gadget.props.field_gadget = field_gadget;
          gadget.props.service_deferred.resolve(field_gadget);
        });
    })


    .declareService(function () {
      // Defer render execution and check errors
      return this.props.render_queue;
    });
}(window, rJS, RSVP));
