/*globals window, RSVP, rJS*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS) {
  "use strict";

  rJS(window)
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
          gadget.props.portal_type = "Travel Request Record";
          gadget.props.document_title_plural = "Mission Requests";
          return gadget.getUrlFor({page: "add_travel_request_record"});
        })
        .push(function (url) {
          var header = {
            title: gadget.props.document_title_plural
          };
          if (!options.came_from_jio_key) {
            header.add_url = url;
          }
          return gadget.updateHeader(header);
        })
        .push(function () {
          return gadget.getDeclaredGadget("listbox");
        })
        .push(function (listbox) {
          var query;
          query =  'portal_type:("' + gadget.props.portal_type + '")';
          if (options.came_from_jio_key) {
            query += ' AND state: "Accepted"';
          }
          return listbox.render({
            came_from_jio_key: options.came_from_jio_key,
            search_page: 'travel_request_record_list',
            search: options.search,
            column_list: [
            {
              select: 'title',
              title: 'Titre'
            }, {
              select: 'resource_title',
              title: 'Mission Type'
            }, {
              select: 'destination_node_title',
              title: 'Destination'
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
              query:  query,
              select_list: ['resource_title', 'title', 'destination_node_title',
                            'start_date', 'stop_date', 'state'],
              sort_on: [["start_date", "descending"]]
            }
          });
        });
    });

}(window, RSVP, rJS));