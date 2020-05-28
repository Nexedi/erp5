/*global window, document, rJS, CKEDITOR, RSVP*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function () {
  "use strict";

  rJS(window)

    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareJob("deferNotifyChange", function () {
      // Ensure error will be correctly handled
      return this.notifyChange();
    })

    .declareMethod('render', function (options) {
      return this.changeState({
        key: options.key,
        value: options.value || ""
        // editable: options.editable === undefined ? true : options.editable
      });
    })

    .declareMethod('getContent', function () {
      var result = {};
      if (this.state.editable) {
        throw new Error('notimplemented');
        /*
        result[this.state.key] = this.ckeditor.getData();
        // Change the value state in place
        // This will prevent the gadget to be changed if
        // its parent call render with the same value
        // (as ERP5 does in case of formulator error)
        this.state.value = result[this.state.key];
        */
      }
      return result;
    })

    .onStateChange(function () {
      this.element.innerHTML = value;
      console.log(this.state);
      return;
    });


}());