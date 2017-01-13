/*global window, rJS, RSVP, jIO*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, jIO) {
  "use strict";

  rJS(window)
    .ready(function (gadget) {
      return gadget.getElement()
        .push(function (element) {
          gadget.element = element;
        });
    })

    .declareAcquiredMethod("notifyValid", "notifyValid")
    .declareAcquiredMethod("notifyInvalid", "notifyInvalid")
    .declareAcquiredMethod("notifyChange", "notifyChange")

    .declareMethod('render', function (options) {
      var input = this.element.querySelector('input'),
        field_json = options.field_json || {};

      input.setAttribute('name', field_json.key);
      input.setAttribute('title', field_json.title);
      if (field_json.required === 1) {
        input.setAttribute('required', 'required');
      }
      if (field_json.editable !== 1) {
        input.setAttribute('readonly', 'readonly');
        input.setAttribute('data-wrapper-class', 'ui-state-readonly');
        // input.setAttribute('disabled', 'disabled');

      }
    })

    .declareMethod('getContent', function () {
      var gadget = this,
        input = gadget.element.querySelector('input'),
        file = input.files[0];
      if (file === undefined) {
        return {};
      }
      return new RSVP.Queue()
        .push(function () {
          return jIO.util.readBlobAsDataURL(file);
        })
        .push(function (evt) {
          var result = {};
          result[input.getAttribute('name')] = {
            url: evt.target.result,
            file_name: file.name
          };
          return result;
        });
    });

}(window, rJS, RSVP, jIO));
