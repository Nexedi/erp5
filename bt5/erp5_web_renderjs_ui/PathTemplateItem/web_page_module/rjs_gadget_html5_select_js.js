/*global window, rJS, RSVP, Handlebars, getFirstNonEmpty */
/*jslint indent: 2, maxerr: 3, maxlen: 80, nomen: true */
(function (window, rJS, RSVP, Handlebars, getFirstNonEmpty) {
  "use strict";

  // How to change html selected option using JavaScript?
  // http://stackoverflow.com/a/20662180

  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    option_source = gadget_klass.__template_element
                      .getElementById("option-template")
                      .innerHTML,
    option_template = Handlebars.compile(option_source),
    selected_option_source = gadget_klass.__template_element
                               .getElementById("selected-option-template")
                               .innerHTML,
    selected_option_template = Handlebars.compile(selected_option_source),
    disabled_option_source = gadget_klass.__template_element
                               .getElementById("disabled-option-template")
                               .innerHTML,
    disabled_option_template = Handlebars.compile(disabled_option_source);

  gadget_klass
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
        template,
        select = this.element.querySelector('select'),
        item_list = JSON.parse(this.state.item_list),
        tmp = "";

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
        for (i = 0; i < item_list.length; i += 1) {
          if (item_list[i][1] === null) {
            template = disabled_option_template;
          } else if (item_list[i][1] === this.state.value) {
            template = selected_option_template;
            found = true;
          } else {
            template = option_template;
          }
          tmp += template({
            value: item_list[i][1],
            text: item_list[i][0]
          });
        }

        if (!found) {
          tmp += selected_option_template({
            value: this.state.value,
            text: '??? (' + this.state.value + ')'
          });
        }
        select.innerHTML = tmp;
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
    .onEvent('change', function change(e) {
      return RSVP.all([
        this.checkValidity(),
        this.notifyChange(e)
      ]);
    }, false, false)
    .onEvent('input', function input(e) {
      return RSVP.all([
        this.checkValidity(),
        this.notifyChange(e)
      ]);
    }, false, false)

    .declareAcquiredMethod("notifyInvalid", "notifyInvalid")
    .onEvent('invalid', function invalid(evt) {
      // invalid event does not bubble
      return this.notifyInvalid(evt.target.validationMessage);
    }, true, false);

}(window, rJS, RSVP, Handlebars, getFirstNonEmpty));