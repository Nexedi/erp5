/*global document, window, rJS, RSVP, getFirstNonEmpty, isEmpty */
/*jslint indent: 2, maxerr: 3, maxlen: 80, nomen: true */
(function (document, window, rJS, RSVP, getFirstNonEmpty, isEmpty) {
  "use strict";

  // How to change html selected option using JavaScript?
  // http://stackoverflow.com/a/20662180

  rJS(window)
    .setState({
      editable: false,
      value: undefined,
      checked: undefined,
      title: '',
      item_list: [],
      required: false
    })

    .declareMethod('render', function render(options) {
      var state_dict = {
          value: getFirstNonEmpty(options.value, ""),
          item_list: JSON.stringify(options.item_list),
          editable: options.editable,
          required: options.required,
          error_text: options.error_text || "",
          id: options.id,
          name: options.name,
          title: options.title,
          hidden: options.hidden
        };
      return this.changeState(state_dict);
    })

    .onStateChange(function onStateChange(modification_dict) {
      var i,
        found = false,
        select = this.element.querySelector('select'),
        item_list = JSON.parse(this.state.item_list),
        option,
        fragment;

      if (modification_dict.hasOwnProperty('value') ||
          modification_dict.hasOwnProperty('item_list') ||
          modification_dict.hasOwnProperty('editable') ||
          modification_dict.hasOwnProperty('required') ||
          modification_dict.hasOwnProperty('id') ||
          modification_dict.hasOwnProperty('name') ||
          modification_dict.hasOwnProperty('title')
          ) {
        select.id = this.state.id || this.state.name;
        select.setAttribute('name', this.state.name);

        if (this.state.title) {
          select.setAttribute('title', this.state.title);
        }

        if (this.state.required) {
          select.required = true;
        } else {
          select.required = false;
        }

        if (this.state.editable) {
          select.readonly = true;
        } else {
          select.readonly = false;
        }

        if (modification_dict.hasOwnProperty('value') ||
            modification_dict.hasOwnProperty('item_list')) {
          fragment = document.createDocumentFragment();

          for (i = 0; i < item_list.length; i += 1) {
            option = document.createElement('option');
            option.textContent = item_list[i][0];
            if (item_list[i][1] === null) {
              option.setAttribute('disabled', 'disabled');
            } else {
              option.setAttribute('value', item_list[i][1]);
              if (item_list[i][1] === this.state.value) {
                option.setAttribute('selected', 'selected');
                found = true;
              }
            }
            fragment.appendChild(option);
          }

          if (!found && !isEmpty(this.state.value)) {
            option = document.createElement('option');
            option.textContent = '??? (' + this.state.value + ')';
            option.setAttribute('value', this.state.value);
            option.setAttribute('selected', 'selected');
            fragment.appendChild(option);
          }

          while (select.firstChild) {
            select.removeChild(select.firstChild);
          }
          select.appendChild(fragment);
        }
      }

      if (modification_dict.hasOwnProperty('error_text') ||
          modification_dict.hasOwnProperty('hidden')) {
        if (this.state.hidden && !this.state.error_text) {
          select.hidden = true;
        } else {
          select.hidden = false;
        }

        if (this.state.error_text &&
            !select.classList.contains("is-invalid")) {
          select.classList.add("is-invalid");
        } else if (!this.state.error_text &&
                   select.classList.contains("is-invalid")) {
          select.classList.remove("is-invalid");
        }
      }
    })

    .declareMethod('getContent', function getContent() {
      var result = {},
        select = this.element.querySelector('select'),
        selected_option;
      if (this.state.editable) {
        selected_option = select.options[select.selectedIndex];
        if (selected_option !== undefined) {
          result[select.getAttribute('name')] =
            selected_option.value;
          // Change the value state in place
          // This will prevent the gadget to be changed if
          // its parent call render with the same value
          // (as ERP5 does in case of formulator error)
          this.state.value = result[select.getAttribute('name')];
        }
      }
      return result;
    }, {mutex: 'changestate'})

    .declareAcquiredMethod("notifyValid", "notifyValid")
    .declareMethod('checkValidity', function checkValidity() {
      var select = this.element.querySelector('select'),
        result = select.checkValidity();
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
    }, {mutex: 'changestate'})

    .declareJob('deferErrorText', function deferErrorText(error_text) {
      return this.changeState({
        error_text: error_text
      });
    })

    .declareAcquiredMethod("notifyChange", "notifyChange")
    .onEvent('change', function change(e) {
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
    }, true, false);

}(document, window, rJS, RSVP, getFirstNonEmpty, isEmpty));