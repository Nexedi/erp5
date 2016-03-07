/*global window, rJS, Handlebars */
/*jslint nomen: true */
(function(window, rJS, Handlebars) {
    "use strict";
    /////////////////////////////////////////////////////////////////
    // Handlebars
    /////////////////////////////////////////////////////////////////
    // Precompile the templates while loading the first gadget instance
    var gadget_klass = rJS(window), option_source = gadget_klass.__template_element.getElementById("option-template").innerHTML, option_template = Handlebars.compile(option_source), selected_option_source = gadget_klass.__template_element.getElementById("selected-option-template").innerHTML, selected_option_template = Handlebars.compile(selected_option_source);
    gadget_klass.ready(function(g) {
        return g.getElement().push(function(element) {
            g.element = element;
        });
    }).declareMethod("render", function(options) {
        var select = this.element.getElementsByTagName("select")[0], i, template, tmp = "";
        select.setAttribute("name", options.key);
        for (i = 0; i < options.property_definition.enum.length; i += 1) {
            if (options.property_definition.enum[i] === options.value) {
                template = selected_option_template;
            } else {
                template = option_template;
            }
            // XXX value and text are always same in json schema
            tmp += template({
                value: options.property_definition.enum[i],
                text: options.property_definition.enum[i]
            });
        }
        select.innerHTML += tmp;
    }).declareMethod("getContent", function() {
        var select = this.element.getElementsByTagName("select")[0], result = {};
        result[select.getAttribute("name")] = select.options[select.selectedIndex].value;
        return result;
    });
})(window, rJS, Handlebars);