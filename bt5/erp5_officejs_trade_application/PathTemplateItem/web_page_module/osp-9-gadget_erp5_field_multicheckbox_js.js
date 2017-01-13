/*global window, rJS, Handlebars, document, RSVP, loopEventListener*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, Handlebars, RSVP) {
  'use strict';
  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    unchecked_source = gadget_klass.__template_element
                      .getElementById("unchecked-template")
                      .innerHTML,
    unchecked_template = Handlebars.compile(unchecked_source),
    checked_source = gadget_klass.__template_element
                       .getElementById("checked-template")
                       .innerHTML,
    checked_template = Handlebars.compile(checked_source);
  gadget_klass
    .ready(function (g) {
      g.props = {};
    })
    // Assign the element to a variable
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareMethod('render', function (options) {
      var gadget = this,
        tmp,
        template,
        container,
        field_json = options.field_json,
        i;
      gadget.props.field_json = field_json;
      container = gadget.props.element.querySelector(".checkbox_container");
      tmp = "";
      for (i = 0; i < field_json.items.length; i += 1) {
        if (field_json.default.indexOf(field_json.items[i][1]) > -1) {
          template = checked_template;
        } else {
          template = unchecked_template;
        }
        tmp += template({
          value: field_json.items[i][1],
          text: field_json.items[i][0]
        });
      }
      container.innerHTML = tmp;
      return new RSVP.Queue()
        .push(function () {
          return gadget.translateHtml(container.innerHTML);
        })
        .push(function (translated_htmls) {
          var checkbox_list;
          container.innerHTML = translated_htmls;
          if (field_json.editable !== 1) {
            checkbox_list = container.querySelectorAll('input[type="checkbox"]');
            for (i = 0; i < checkbox_list.length; i += 1) {
              checkbox_list[i].setAttribute("class", "ui-btn ui-shadow ui-state-readonly");
            }
          }
        });
    })
    .declareMethod('getContent', function () {
      var gadget = this,
        result = {},
        tmp = [],
        checkbox_list = this.props.element.querySelectorAll('input[type="checkbox"]'),
        i;
      for (i = 0; i < checkbox_list.length; i += 1) {
        if (checkbox_list[i].checked) {
          tmp.push(checkbox_list[i].value);
        }
      }
      result[gadget.props.field_json.key] = tmp;
      result["default_" + gadget.props.field_json.key + ":int"] = 0;
      return result;
    });
}(window, rJS, Handlebars, RSVP));