/*global window, rJS */
(function(window, rJS) {
    "use strict";
    rJS(window).ready(function(gadget) {
        return gadget.getElement().push(function(element) {
            gadget.element = element;
        });
    }).declareMethod("render", function(options) {
        var input = this.element.querySelector("input");
        input.setAttribute("value", options.value);
        input.setAttribute("name", options.key);
        input.setAttribute("title", options.property_definition.description);
    }).declareMethod("getContent", function() {
        var input = this.element.querySelector("input"), result = {};
        if (input.value !== "") {
            result[input.getAttribute("name")] = parseFloat(input.value);
        } else {
            result[input.getAttribute("name")] = null;
        }
        return result;
    });
})(window, rJS);