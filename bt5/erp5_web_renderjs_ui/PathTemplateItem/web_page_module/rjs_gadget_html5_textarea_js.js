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
      focused: false,
      value: ''
    })

    .declareMethod('render', function (options) {
      var state_dict = {
          value: options.value,
          editable: options.editable,
          name: options.name,
          title: options.title
        };
      return this.changeState(state_dict);
    })

    .declareMethod('updateDOM', function () {
      var textarea = this.element.querySelector('textarea');
      textarea.value = this.state.value;
      textarea.setAttribute('name', this.state.name);
      textarea.setAttribute('title', this.state.title);
      textarea.setAttribute('wrap', 'off');

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

      if (this.state.focused) {
        textarea.setAttribute('rows', this.state.value.split('\n').length);
      } else {
        textarea.setAttribute('rows', 2);
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

    .onEvent('focus', function () {
      return this.changeState({focused: true, value: this.element.querySelector('textarea').value});
    }, true, false)
    .onEvent('blur', function () {
      return this.changeState({focused: false, value: this.element.querySelector('textarea').value});
    }, true, false)

    .declareAcquiredMethod("notifySubmit", "notifySubmit")
    .onEvent('keydown', function (evt) {
      if (evt.keyCode === 83 && (navigator.platform.match("Mac") ? evt.metaKey : evt.ctrlKey)) {
        evt.preventDefault();
        return this.notifySubmit();
      }
    }, false, false);

}(window, rJS, RSVP, navigator));