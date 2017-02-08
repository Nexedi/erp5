/*globals window, RSVP, rJS, document*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS, document) {
  "use strict";
   var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                              .querySelector(".page-template")
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
          gadget.props.portal_type = "Leave Request Record";
          gadget.props.document_title_plural = "Leave Requests";
          return gadget.getUrlFor({page: "add_leave_request_record"});
        })
        .push(function (url) {
          return gadget.updateHeader({
            title: gadget.props.document_title_plural,
            add_url: url
          });
        })
        .push(function () {
          return gadget.jio_allDocs({
            query: 'portal_type: "Leave Report Record"',
            select_list: ["confirmed_leaves_days_left"],
          });
        })
        .push(function (result) {
          var options = {};
          if (result.data.total_rows > 0) {
            options.day_left = result.data.rows[0].value.confirmed_leaves_days_left;
          }
          return gadget.translateHtml(template(options));
        })
        .push(function (html) {
          gadget.props.element.innerHTML = html;
          return gadget.declareGadget("gadget_officejs_widget_listbox.html", {element: gadget.props.element.querySelector('.leave_request_listbox')});
        })
        .push(function (listbox) {
          return listbox.render({
            search_page: 'leave_request_record_list',
            search: options.search,
            column_list: [{
              select: 'resource_title',
              title: 'Leave Type'
            }, {
              select: 'start_date',
              title: 'Start Date'
            }, {
              select: 'stop_date',
              title: 'End Date'
            }, {
              select: 'state',
              title: 'State'
            }],
            query: {
              query: 'portal_type:("' + gadget.props.portal_type + '")',
              select_list: ['resource_title',
                            'start_date', 'stop_date','state'],
              sort_on: [["start_date", "descending"]]
            }
          });
        });
    });

}(window, RSVP, rJS, document));