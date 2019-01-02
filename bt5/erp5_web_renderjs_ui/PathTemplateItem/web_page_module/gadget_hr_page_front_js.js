/*globals window, RSVP, rJS*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS) {
  "use strict";
   var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                              .querySelector(".front-template")
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
    .ready(function (g) {
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            g.translate("validated"),
            g.translate("invalidated"),
            g.translate("Not synced!"),
            g.translate("Waiting for approval")
          ]);
        })
        .push(function (result_list) {
          g.props.translation_dict = {
            "validated": result_list[0],
            "invalidated": result_list[1],
            "Not synced!": result_list[2],
            "Waiting for approval": result_list[3]
          };
        });
    })
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod('getSetting', 'getSetting')
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("redirect", "redirect")
    .allowPublicAcquisition("jio_allDocs", function (param_list) {
      var gadget = this;
      return this.jio_allDocs.apply(this, param_list)
        .push(function (result) {
          var i,
            len;
          for (i = 0, len = result.data.total_rows; i < len; i += 1) {
            // XXX jIO does not create UUID with module inside
            if (result.data.rows[i].id.indexOf("module") === -1) {
              result.data.rows[i].value.state =
                gadget.props.translation_dict["Not synced!"];
            } else {
              result.data.rows[i].value.state =
                result.data.rows[i].value.state || gadget.props.translation_dict[
                  "Waiting for approval"];
            }
          }
          return result;
        });
    })
    .declareMethod("render", function (options) {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.translateHtml(template());
        })
        .push(function (html) {
          gadget.props.element.innerHTML = html;
          return gadget.getSetting('last_sync_date');
        })
        .push(function (result) {
          if (!result) {
            return gadget.redirect({
              page: 'sync',
              auto_repair: true
            });
          }
          gadget.props.element.querySelector('.last_sync_date').innerHTML = result;
          gadget.props.portal_type = "Expense Record";
          gadget.props.document_title_plural = "Expense Requests";
          return RSVP.all([
            gadget.declareGadget("gadget_officejs_widget_listbox.html", {element: gadget.props.element.querySelector(".listbox-suspended")}),
            gadget.declareGadget("gadget_officejs_widget_listbox.html", {element: gadget.props.element.querySelector(".listbox-draft")})
            ]);
        })
        .push(function (listbox_gadget_list) {
          return RSVP.all([
            listbox_gadget_list[0].render({
              column_list: [{
                select: 'comment',
                title: 'Description'
              }, {
                select: 'type_title',
                title: 'Type'
              }, {
                select: 'quantity',
                title: 'Total Price'
              }, {
                select: 'resource_title',
                title: 'Currency'
              }, {
                select: 'date',
                title: 'Input Date'
              }, {
                select: 'doc_id',
                title: 'ID'
              }, {
                select: 'state',
                title: 'State'
              }],
              query: {
                query: 'portal_type:("% Record") AND state:"Suspended"',
                select_list: ['doc_id', 'quantity', 'resource_title',
                              'comment', 'date', 'type_title',
                              'state'],
                sort_on: [["modification_date", "descending"]]
              }
            }),
            listbox_gadget_list[1].render({
              column_list: [{
                select: 'comment',
                title: 'Description'
              }, {
                select: 'portal_type',
                title: 'Type'
              }, {
                select: 'state',
                title: 'State'
              }],
              query: {
                query: '(simulation_state:"draft" OR sync_flag:"0") AND (portal_type: "Expense Record" OR portal_type:"Travel Request Record" OR portal_type:"Leave Report Record" OR portal_type:"Leave Request Record") ',
                select_list: ['comment', 'portal_type', 'state'],
                sort_on: [["modification_date", "descending"]]
              }
            })
          ]);
          
        });
    })
      .declareService(function () {
        var gadget = this;
        return new RSVP.Queue()
         .push(function () {
           return loopEventListener(
             gadget.props.element.querySelector('form.synchro-form'),
             'submit',
             false,
             function () {
              gadget.props.element.querySelector("button").disabled = true;
              return gadget.redirect({
                page: 'sync',
                auto_repair: true
              });
             });
         });
    });

}(window, RSVP, rJS));