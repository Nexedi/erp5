/*global window, rJS, RSVP */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  function maximize(gadget, element) {
    element.querySelector('[data-gadget-scope="header"]')
      .className = 'maximize-mode';
    element.querySelector('[data-gadget-scope="panel"]')
      .className = 'maximize-mode';
    gadget.state.target.element.className = 'content-iframe-maximize';
    return gadget.state.main_gadget.getDeclaredGadget('header')
      .push(function (header_gadget) {
        return header_gadget.setTitleButton('maximize');
      });
  }

  function minimize(gadget, element) {
    element.querySelector('[data-gadget-scope="header"]')
      .className = '';
    element.querySelector('[data-gadget-scope="panel"]')
      .className = '';
    gadget.state.target.element.className = '';
    return gadget.state.main_gadget.getDeclaredGadget('header')
      .push(function (header_gadget) {
        return header_gadget.setTitleButton('');
      });
  }

  rJS(window)

    .setState({
      maximize: false,
      target: null
    })
    .declareAcquiredMethod('updateHeader', 'updateHeader')
    .declareAcquiredMethod('getUrlFor', 'getUrlFor')
    .declareMethod('reset', function (options) {
      return this.changeState({maximize: false});
    })

    .declareMethod('trigger', function (gadget, options) {
      var state = {
        main_gadget: gadget,
        maximize: false
      };
      if (options && options.hasOwnProperty('target')) {
        state.target = options.target;
        state.maximize = true;
      }
      return this.changeState(state);
    })

    .onStateChange(function (modification_dict) {
      var gadget = this, element;
      if (modification_dict.hasOwnProperty('maximize')) {
        element = gadget.state.main_gadget.element;
        if (gadget.state.maximize) {
          return maximize(gadget, element);
        } else {
          minimize(gadget, element);
        }
      }
    });

}(window, rJS, RSVP));