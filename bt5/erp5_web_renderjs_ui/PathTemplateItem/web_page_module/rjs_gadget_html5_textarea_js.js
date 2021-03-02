/*global window, rJS, RSVP, navigator */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, navigator) {
  "use strict";

  rJS(window)
    .setState({
      editable: false,
      value: ''
    })

    .declareMethod('render', function render(options) {
      return this.changeState({
        value: options.value,
        editable: options.editable,
        required: options.required,
        id: options.id,
        name: options.name,
        title: options.title,
        error_text: options.error_text || "",
        hidden: options.hidden
      });
    })

    .onStateChange(function onStateChange(modification_dict) {
      var textarea = this.element.querySelector('textarea');

      if (modification_dict.hasOwnProperty('value') ||
          modification_dict.hasOwnProperty('editable') ||
          modification_dict.hasOwnProperty('required') ||
          modification_dict.hasOwnProperty('id') ||
          modification_dict.hasOwnProperty('name') ||
          modification_dict.hasOwnProperty('title') ||
          modification_dict.hasOwnProperty('hidden')
          ) {

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
          textarea.required = true;
        } else {
          textarea.required = false;
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

      }

      if (modification_dict.hasOwnProperty('error_text')) {
        if (this.state.error_text &&
            !textarea.classList.contains("is-invalid")) {
          textarea.classList.add("is-invalid");
        } else if (!this.state.error_text &&
                   textarea.classList.contains("is-invalid")) {
          textarea.classList.remove("is-invalid");
        }
      }

    })

    .declareMethod('getContent', function getContent() {
      var result = {},
        input;
      if (this.state.editable) {
        input = this.element.querySelector('textarea');
        result[input.getAttribute('name')] = input.value;
        // Change the value state in place
        // This will prevent the gadget to be changed if
        // its parent call render with the same value
        // (as ERP5 does in case of formulator error)
        this.state.value = input.value;
      }
      return result;
    })

    .declareAcquiredMethod("notifyValid", "notifyValid")
    .declareMethod('checkValidity', function checkValidity() {
      var textarea = this.element.querySelector('textarea'),
        result = textarea.checkValidity();
      if (result) {
        return this.notifyValid()
          .push(function () {
            return result;
          });
      }
      if (this.state.error_text) {
        return this.notifyInvalid(this.state.error_text)
          .push(function () {
            return result;
          });
      }
      return result;
    })

    .declareJob('deferErrorText', function deferErrorText(error_text) {
      return this.changeState({
        error_text: error_text
      });
    }, {mutex: 'changestate'})

    .declareAcquiredMethod("notifyChange", "notifyChange")
    .onEvent('change', function change() {
      return RSVP.all([
        this.checkValidity(),
        this.notifyChange("change")
      ]);
    }, false, false)

    .onEvent('input', function input() {
      return RSVP.all([
        this.checkValidity(),
        this.notifyChange("input")
      ]);
    }, false, false)

    .declareAcquiredMethod("notifyFocus", "notifyFocus")
    .onEvent('focus', function focus() {
      return this.notifyFocus();
    }, true, false)

    .declareAcquiredMethod("notifyBlur", "notifyBlur")
    .onEvent('blur', function blur() {
      return this.notifyBlur();
    }, true, false)

    .declareAcquiredMethod("notifyInvalid", "notifyInvalid")
    .onEvent('invalid', function invalid(evt) {
      // invalid event does not bubble
      return RSVP.all([
        this.deferErrorText(evt.target.validationMessage),
        this.notifyInvalid(evt.target.validationMessage)
      ]);
    }, true, false)


    .declareAcquiredMethod("notifySubmit", "notifySubmit")
    .onEvent('keydown', function keydown(evt) {
      var textarea = this.element.querySelector('textarea');
      if (evt.keyCode === 83 && (navigator.platform.match("Mac") ? evt.metaKey : evt.ctrlKey)) {
        //Textarea's change event is generally launched by browser when press a predefined key
        //Call preventDefault prevent change event
        evt.preventDefault();
        //When lose focus, change event is launched
        //Without this, after saving, then click other fields or go to other view
        //Change event will be trigged and there will have a unsaved warning for textarea
        textarea.blur();
        //Refocus for consistency
        textarea.focus();
        return this.notifySubmit();
      }
    }, false, false);

}(window, rJS, RSVP, navigator));