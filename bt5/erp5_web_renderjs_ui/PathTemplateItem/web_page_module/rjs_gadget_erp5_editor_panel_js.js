/*jslint indent: 2, maxerr: 3, nomen: true */
/*global window, rJS, RSVP, $ */
(function (window, rJS, RSVP, $) {
  "use strict";
  rJS(window)
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {};
    })
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          g.props.container = element.querySelector(".jqm-navmenu-panel");
          g.props.jelement = $(g.props.container);
        });
    })
    .ready(function (g) {
      g.props.jelement.panel({
        display: "overlay",
        position: "right",
        theme: "c"
      });
    })


    .allowPublicAcquisition('trigger', function () {
      return this.props.jelement.panel("toggle");
    })
    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    //local method
    .declareMethod('close', function () {
      var container = this.props.container;
      this.props.jelement.panel("close");
      while (container.firstChild) {
        container.removeChild(container.firstChild);
      }
    })
    .declareMethod('render', function (url, options) {
      var gadget = this,
        declared_gadget;
      if (url && gadget.props.options !== options) {
        gadget.props.options = options;
        return new RSVP.Queue()
          .push(function () {
            return gadget.declareGadget(url, {scope: "declared_gadget"});
          })
          .push(function (result) {
            declared_gadget = result;
            return declared_gadget.render(options);
          })
          .push(function () {
            return RSVP.all([
              gadget.close(),
              declared_gadget.getElement()
            ]);
          })
          .push(function (result) {
            var fragment = result[1];
            gadget.props.container.appendChild(fragment);
            gadget.props.jelement.trigger("create");
            gadget.props.jelement.panel("toggle");
          });
      }
      gadget.props.jelement.panel("toggle");
    });
}(window, rJS, RSVP, $));