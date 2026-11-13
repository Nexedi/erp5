/*globals window, rJS, RSVP, document, promiseEventListener*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, document, RSVP, rJS, promiseEventListener) {
  "use strict";

  var gadget_klass = rJS(window);
  gadget_klass
    .ready(function (gadget) {
      gadget.props = {};
      return gadget.getElement()
        .push(function (element) {
          gadget.props.element = element;
          var buttonSalePriceRecord, buttonPurchasePriceRecord,
            buttonDailyStatementRecord;

          buttonSalePriceRecord = document.createElement("input");
          buttonSalePriceRecord
            .setAttribute('name', 'create_sale_price_record');
          buttonSalePriceRecord
            .setAttribute('type', 'submit');
          buttonSalePriceRecord
            .setAttribute('value', 'Create Sale Price Record');

          buttonPurchasePriceRecord = document.createElement("input");
          buttonPurchasePriceRecord
            .setAttribute('name', 'create_purchase_price_record');
          buttonPurchasePriceRecord
            .setAttribute('type', 'submit');
          buttonPurchasePriceRecord
            .setAttribute('value', 'Create Purchase Price Record');

          buttonDailyStatementRecord = document.createElement("input");
          buttonDailyStatementRecord
            .setAttribute('name', 'create_daily_statement_record');
          buttonDailyStatementRecord
            .setAttribute('type', 'submit');
          buttonDailyStatementRecord
            .setAttribute('value', 'Create Daily Statement Record');

          gadget.props.element.querySelector('.form')
            .appendChild(buttonSalePriceRecord);
          gadget.props.element.querySelector('.form')
            .appendChild(buttonPurchasePriceRecord);
          gadget.props.element.querySelector('.form')
            .appendChild(buttonDailyStatementRecord);
        });
    })

     .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("updateHeader", "updateHeader")

    .declareMethod("render", function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.updateHeader({
            page_title: "ERP5"
          });
        });
    })

     //create new purchase price record
     .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return promiseEventListener(
            gadget.props.element
              .querySelector('[name=create_purchase_price_record]'),
            'click',
            false
          );
        })
        .push(function () {
          return gadget.redirect({command: 'display',
            options: {jio_key: "purchase_price_record_module",
              page: "add_purchase_price_record"}
            });
        });

    })

     //create new sale price record
     .declareService(function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return promiseEventListener(
            gadget.props.element
              .querySelector('[name=create_sale_price_record]'),
            'click',
            false
          );
        })
        .push(function () {
          return gadget.redirect({command: 'display',
            options: {jio_key: "sale_price_record_module",
              page: "add_sale_price_record"}
            });
        });

    })

    //create new daily statement record
    .declareService(function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return promiseEventListener(
            gadget.props.element
              .querySelector('[name=create_daily_statement_record]'),
            'click',
            false
          );
        })
        .push(function () {
          return gadget.redirect({command: 'display',
            options: {jio_key: "daily_statement_record_module",
              page: "add_daily_statement_record"}
            });
        });
    });



}(window, document, RSVP, rJS, promiseEventListener));
