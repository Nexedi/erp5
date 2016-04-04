/*globals window, rJS, Handlebars*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, rJS, Handlebars) {
  "use strict";

  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                              .querySelector(".view-product-template")
                              .innerHTML,
    template = Handlebars.compile(source);


  gadget_klass
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })

    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("translateHtml", "translateHtml")

    .declareMethod("render", function (options) {
      var gadget = this;
      var temp_doc = {};
      for (var i in options.doc){
        temp_doc[i] = options.doc[i]
      }
      temp_doc['product_path'] = options.jio_key
      return gadget.translateHtml(template(temp_doc))
        .push(function (html) {
          gadget.props.element.innerHTML = html;

          if (options.jio_key.indexOf('product_module/') == 0){
            $('<a data-role="button" href="Base_redirectTo/'+options.jio_key+'" target="_blank">'+translateString('Go To ERP5')+'</a>').appendTo($(gadget.props.element.querySelector('form')))
          }

          return gadget.updateHeader({
            title: "Product"
          });
        });

    });

}(window, rJS, Handlebars));