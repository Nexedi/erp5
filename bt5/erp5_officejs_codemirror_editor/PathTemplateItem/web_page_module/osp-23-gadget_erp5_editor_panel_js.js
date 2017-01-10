/*jslint indent: 2, maxerr: 3, nomen: true */
/*global window, rJS, RSVP */
(function (window, rJS, RSVP) {
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
        });
    })

    .allowPublicAcquisition('trigger', function () {
      this.props.element.classList.toggle('visible');
      // return this.props.jelement.panel("toggle");
    })
    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    //local method
    .declareMethod('close', function () {
      var container = this.props.container;
      while (container.firstChild) {
        container.removeChild(container.firstChild);
      }
      if (this.props.element.classList.contains('visible')) {
        this.props.element.classList.remove('visible');
      }
    })
    .declareMethod('render', function (url, options) {
      var gadget = this,
        declared_gadget;
      if (url && JSON.stringify(gadget.props.options) !== JSON.stringify(options)) {
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
            gadget.props.element.classList.toggle('visible');
          });
      }
      gadget.props.element.classList.toggle('visible');
    });
}(window, rJS, RSVP));