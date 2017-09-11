/*global window, rJS, RSVP, navigator */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, navigator) {
  "use strict";

  function checkChange() {
    var gadget = this;
    return gadget.changeState({value: gadget.element.querySelector('textarea').value})
      .push(function () {
        return RSVP.all([
          gadget.checkValidity(),
          gadget.notifyChange()
        ]);
      });
  }

  rJS(window)
    .setState({
      editable: false,
      value: ''
    })

    .declareMethod('render', function (options) {
      return this.changeState(options);
    })

    .onStateChange(function (modification_dict) {
      var textarea = this.element.querySelector('textarea');

      if (modification_dict.hasOwnProperty("value")) {
        textarea.value = modification_dict.value;
      }

      if (modification_dict.hasOwnProperty("name")) {
        textarea.setAttribute('name', modification_dict.name);
        textarea.setAttribute('id', modification_dict.name);
      }

      if (modification_dict.hasOwnProperty("title")) {
        textarea.setAttribute('title', modification_dict.title);
      }

      if (this.state.required) {
        textarea.setAttribute('required', 'required');
      } else {
        textarea.removeAttribute('required');
      }

      if (this.state.editable) {
        textarea.removeAttribute('readonly');
      } else {
        textarea.setAttribute('readonly', 'readonly');
      }

      if (this.state.hidden) {
        textarea.hidden = true;
      } else {
        textarea.hidden = false;
      }

    })

    .declareMethod('getContent', function () {
      var result = {},
        input;
      if (this.state.editable) {
        input = this.element.querySelector('textarea');
        result[input.getAttribute('name')] = input.value;
      }
      return result;
    })

    .declareAcquiredMethod("notifyValid", "notifyValid")
    .declareMethod('checkValidity', function () {
      var result = this.element.querySelector('textarea').checkValidity();
      if (result) {
        return this.notifyValid()
          .push(function () {
            return result;
          });
      }
      return result;
    })

    .declareAcquiredMethod("notifyChange", "notifyChange")
    .onEvent('change', checkChange, false, true)
    .onEvent('input', checkChange, false, true)

    .declareAcquiredMethod("notifyInvalid", "notifyInvalid")
    .onEvent('invalid', function (evt) {
      // invalid event does not bubble
      return this.notifyInvalid(evt.target.validationMessage);
    }, true, true)

    .declareAcquiredMethod("notifySubmit", "notifySubmit")
    .onEvent('keydown', function (evt) {
      if (evt.keyCode === 83 && (navigator.platform.match("Mac") ? evt.metaKey : evt.ctrlKey)) {
        evt.preventDefault();
        return this.notifySubmit();
      }
    }, false, false);

}(window, rJS, RSVP, navigator));