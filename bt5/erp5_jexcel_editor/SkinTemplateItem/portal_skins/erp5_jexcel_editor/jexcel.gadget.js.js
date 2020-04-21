/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, jexcel*/
(function (window, rJS, RSVP, jexcel) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("notifySubmit", "notifySubmit")
    .declareJob("deferNotifySubmit", function () {
      // Ensure error will be correctly handled
      return this.notifySubmit();
    })
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareJob("deferNotifyChange", function () {
      // Ensure error will be correctly handled
      return this.notifyChange();
    })
    .ready(function () {
      var context = this;
      context.deferNotifyChangeBinded = context.deferNotifyChange.bind(context);
      var editor = jexcel(this.element.querySelector(".spreadsheet"), {
          minDimensions: [10, 10],
          columns: {width: 200}
        });
    })
    .declareMethod("render", function (option_dict) {
      var gadget = this;
    })
  
    ;

}(window, rJS, RSVP, jexcel));