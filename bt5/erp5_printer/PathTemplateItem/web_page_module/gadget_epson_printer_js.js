/*global window, rJS, document*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, document, Handlebars, RSVP) {
  "use strict";
  var gadget_klass = rJS(window),
    epson_print_source = gadget_klass.__template_element
                         .getElementById("epson-print-template")
                         .innerHTML,
    epson_print_template = Handlebars.compile(epson_print_source);

  gadget_klass
    .declareAcquiredMethod("submitContent", "submitContent")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getTranslationList", "getTranslationList")
    .declareMethod("render", function (options) {
      var gadget = this,
        data_dict = options.data_dict,
        translation_list = [
          'Receipt',
          'Order Number',
          'Document Date',
          'Currency',
          'Products details',
          'PROD',
          'QTY',
          'PRICE',
          'Total Including Tax',
          'Discount',
          'Total With Discount',
          'Print by Epson',
          'Confirm Order and Return',
          'Cancel Order and Return',
          'Products details',
          'Order Information',
          'Payment',
          'Delivery Mode'
        ];
      gadget.state.jio_key = options.jio_key;
      gadget.state.printer_url = options.printer_url;
      return new RSVP.Queue()
       .push(function (hateoas_url) {
          return RSVP.all([
            gadget.getSetting('hateoas_url'),
            gadget.getTranslationList(translation_list)
          ]);
        })
       .push(function (result_list) {
          var index;
          gadget.state.hateoas_url = result_list[0];
          for (index = 0; index < translation_list.length; index += 1) {
            data_dict[translation_list[index].replace(/ /g, '_')] = result_list[1][index];
          }
          // example: sale_order_module/359/1, total price is 2427.3, but Order_getODTDataDict return 2427.2999999999997
          for (index = 0; index < data_dict.line_not_tax.length; index += 1) {
            data_dict.line_not_tax[index].total_price = Math.round(data_dict.line_not_tax[index].total_price * 100) / 100;
          }
          //example: sale_order_module/356, total price is 30464.8, but return 30464.79999999999
          data_dict.total_price_with_discount = Math.round(data_dict.total_price_with_discount * 100) / 100;
          data_dict.total_price = Math.round(data_dict.total_price * 100) / 100;


          gadget.element.querySelector('.container').innerHTML = epson_print_template(data_dict);
          // enable monitoring
          window.monitoring_enabled = 0;
          gadget.listenToPrintButton();
        });
    })
    .declareJob("listenToPrintButton", function () {
      var gadget = this,
        print_button = this.element.querySelector('#print_button');
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            promiseEventListener(gadget.element.querySelector('#company_logo'), 'load', false),
            promiseEventListener(gadget.element.querySelector('#order_barcode'), 'load', false)
          ]);
        })
        .push(function () {
          printInvoiceOnEpson(gadget.state.printer_url);
          return loopEventListener(
              print_button,
              'click',
              false,
              function () {
                printInvoiceOnEpson(gadget.state.printer_url);
              });
      });
    })
    .onEvent('submit', function submit(options) {
      var method = document.activeElement.value,
       gadget = this;
      return gadget.submitContent(
        gadget.state.jio_key,
        gadget.state.hateoas_url + gadget.state.jio_key + "/" + method,
        {})
        .push(function (result) {
          return gadget.redirect({
              command: 'display',
              options: {
                "jio_key": result.jio_key,
                "view": result.view
              }
            });
        })
        .push(undefined, function(error) {
          if (! error instanceof RSVP.CancellationError) {
            throw error;
          }
        });
    });
}(window, rJS, document, Handlebars, RSVP));
