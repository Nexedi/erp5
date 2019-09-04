/*global window, rJS */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod('triggerEditable', 'triggerEditable')

    .onEvent('click', function (event) {
      var identif = event.toElement.value;
      if (identif === 'Edit') {
        return this.triggerEditable({editable: true});
      } else if (identif === 'Execute') {
        return this.triggerEditable({editable: false});
      }
    });

}(window, rJS, RSVP));