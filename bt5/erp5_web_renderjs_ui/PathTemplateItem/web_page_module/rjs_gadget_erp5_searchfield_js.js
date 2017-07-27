/*global window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function (options) {
      var state_dict = {
        extended_search: options.extended_search || "",
        focus: options.focus
      };

      return this.changeState(state_dict);
    })

    .onStateChange(function () {
      var gadget = this;
      return gadget.getDeclaredGadget('input')
        .push(function (input_gadget) {
          var focus = gadget.state.focus || false;

          if (gadget.state.focus === undefined && !gadget.state.extended_search) {
            focus = true;
          }

          return input_gadget.render({
            type: "search",
            value: gadget.state.extended_search,
            focus: focus,
            name: "search",
            editable: true
          });
        });
    })

    .allowPublicAcquisition("notifyValid", function () {return; })

    .declareMethod('getContent', function () {
      return this.getDeclaredGadget('input')
        .push(function (input_gadget) {
          return input_gadget.getContent();
        })
        .push(function (result) {
          if (result.search) {
            // XXX trim from input gadget?
            result.search = result.search.trim();
          }
          return result;
        });
    });

}(window, rJS));