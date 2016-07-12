/*jslint indent: 2, maxerr: 3, nomen: true */
/*global window, rJS */
(function (window, rJS) {
  "use strict";


  rJS(window)

    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (my_gadget) {
      my_gadget.props = {};
      return my_gadget.getElement()
        .push(function (element) {
          my_gadget.props.element = element;
          return my_gadget.getDeclaredGadget("relation_input");
        })
        .push(function (relation_input_gadget) {
          my_gadget.props.relation_input_gadget = relation_input_gadget;
        });
    })
    .allowPublicAcquisition("addRelationInput", function () {
      return;
    })
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function (options) {
      return this.props.relation_input_gadget.render(options, {
        index: 0
      });
    })
    .declareMethod('getContent', function (options) {
      return this.props.relation_input_gadget.getContent(options);
    });

}(window, rJS));