/*global window, rJS, RSVP */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod('trigger', 'trigger')

    .declareMethod('render', function (options) {
      return this.changeState({
        target: options.target,
        value: options.value
      });
    })

    .onStateChange(function (modification_dict) {
      if (modification_dict.hasOwnProperty('value')) {
        this.element.querySelector('button').textContent = this.state.value;
      }
    })

    .onEvent('click', function () {
      if (this.state.hasOwnProperty('target')) {
        return this.trigger('maximize', {target: this.state.target});
      }
    });

}(window, rJS, RSVP));