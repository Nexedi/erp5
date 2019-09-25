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

      if (this.state.hidden) {
        select.hidden = true;
      } else {
        select.hidden = false;
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
    })

    .declareMethod('getContent', function getContent() {
      var result = {},
        select = this.element.querySelector('select');
      if (this.state.editable) {
        result[select.getAttribute('name')] =
          select.options[select.selectedIndex].value;
        // Change the value state in place
        // This will prevent the gadget to be changed if
        // its parent call render with the same value
        // (as ERP5 does in case of formulator error)
        this.state.value = result[select.getAttribute('name')];
      }
      return result;
    })

    .declareAcquiredMethod("notifyValid", "notifyValid")
    .declareMethod('checkValidity', function checkValidity() {
      var result = this.element.querySelector('select').checkValidity();
      if (result) {
        return this.notifyValid()
          .push(function () {
            return result;
          });
      }
      return result;
    })

    .declareAcquiredMethod("notifyChange", "notifyChange")
    .onEvent('change', function change() {
      return RSVP.all([
        this.checkValidity(),
        this.notifyChange()
      ]);
    }, false, false)
    .onEvent('input', function input() {
      return RSVP.all([
        this.checkValidity(),
        this.notifyChange()
      ]);
    }, false, false)

    .declareAcquiredMethod("notifyInvalid", "notifyInvalid")
    .onEvent('invalid', function invalid(evt) {
      // invalid event does not bubble
      return this.notifyInvalid(evt.target.validationMessage);
    }, true, false);

}(document, window, rJS, RSVP, getFirstNonEmpty, isEmpty));