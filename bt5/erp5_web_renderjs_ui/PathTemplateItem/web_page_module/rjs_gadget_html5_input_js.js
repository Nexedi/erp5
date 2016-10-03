/*global window, rJS, RSVP */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    .setState({
      editable: false,
      value: '',
      title: '',
      type: 'text',
      required: false
    })

    .declareMethod('render', function (options) {
      var state_dict = {
          value: options.value || "",
          editable: options.editable,
          required: options.required,
          name: options.name,
          type: options.type || 'text',
          title: options.title,
          focus: options.focus
        };
      return this.changeState(state_dict);
    })

    .declareMethod('updateDOM', function () {
      var textarea = this.element.querySelector('input');
      textarea.value = this.state.value;
      textarea.setAttribute('name', this.state.name);
      textarea.setAttribute('type', this.state.type);
      if (this.state.title) {
        textarea.setAttribute('title', this.state.title);
      }

      if (this.state.required) {
        textarea.required = true;
      } else {
        textarea.required = false;
      }

      if (this.state.editable) {
        textarea.readonly = true;
      } else {
        textarea.readonly = false;
      }

      if (this.state.focus === true) {
        textarea.autofocus = true;
        textarea.focus();
      }
    })

    .declareService(function () {
      if (this.state.focus === true) {
        this.element.querySelector('input').focus();
      }
    })

    .declareMethod('getContent', function () {
      var result = {},
        input;
      if (this.state.editable) {
        input = this.element.querySelector('input');
        result[input.getAttribute('name')] = input.value;
      }
      return result;
    })

    .declareAcquiredMethod("notifyValid", "notifyValid")
    .declareMethod('checkValidity', function () {
      var result = this.element.querySelector('input').checkValidity();
      if (result) {
        return this.notifyValid()
          .push(function () {
            return result;
          });
      }
      return result;
    })

    .declareAcquiredMethod("notifyChange", "notifyChange")
    .onEvent('change', function () {
      return RSVP.all([
        this.checkValidity(),
        this.notifyChange()
      ]);
    }, false, false)
    .onEvent('input', function () {
      return RSVP.all([
        this.checkValidity(),
        this.notifyChange()
      ]);
    }, false, false)

    .declareAcquiredMethod("notifyInvalid", "notifyInvalid")
    .onEvent('invalid', function (evt) {
      // invalid event does not bubble
      return this.notifyInvalid(evt.target.validationMessage);
    }, true, true);

}(window, rJS, RSVP));