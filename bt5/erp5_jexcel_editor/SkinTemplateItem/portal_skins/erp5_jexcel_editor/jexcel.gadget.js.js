/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, jexcel*/
(function (window, rJS, RSVP, jexcel) {
  "use strict";

  var template = {
    minDimensions: [2, 2],
    toolbar: true
  };

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

    .declareMethod("render", function (options) {
      var gadget = this;
      console.log("ready111");
      //return gadget.changeState(options);
    })

    .onStateChange(function (modification_dict) {
      var gadget = this;
      var table;
      gadget.deferNotifyChangeBinded = gadget.deferNotifyChange.bind(gadget);
      if (modification_dict.hasOwnProperty('value')) {
        var tmp = Object.assign({}, template);
        Object.assign(tmp, template);
        Object.assign(tmp, gadget.state.value);
        table = jexcel(gadget.element.querySelector(".spreadsheet"), Object.assign(tmp, {
          onchange: gadget.deferNotifyChangeBinded
        }));
        this.table = table;
      }
    })

    .declareMethod('getContent', function () {
      var form_data = {};
      if (this.state.editable) {
        form_data[this.state.key] = JSON.stringify(this.table.getConfig());
        this.state.value = form_data[this.state.key];
      }
      return form_data;
    });

}(window, rJS, RSVP, jexcel));