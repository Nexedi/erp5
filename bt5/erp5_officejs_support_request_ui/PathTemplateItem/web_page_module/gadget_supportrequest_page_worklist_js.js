/*global window, rJS, RSVP, Query, domsugar */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Query, domsugar) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function () {
      var gadget = this;

      return gadget.updateHeader({
        page_title: 'Worklist',
        page_icon: 'clipboard'
      })
        .push(function () {
          return gadget.getSetting("hateoas_url");
        })
        .push(function (hateoas_url) {
          return gadget.jio_getAttachment(
            'support_request_module',
            hateoas_url + 'support_request_module' +
               '/SupportRequestModule_getWorklistAsJson'
          );
        })
        .push(function (result) {
          /*jslint continue:true*/
          var promise_list = [],
            display_options,
            i;

          for (i = 0; i < result.length; i += 1) {
            if (result[i].action_count === 0) {
              continue;
            }
            display_options = {
              jio_key: "support_request_module",
              extended_search: Query.objectToSearchText(result[i].query),
              page: 'form',
              view: 'view'
            };

            promise_list.push(RSVP.all([
              gadget.getUrlFor({command: 'display', options: display_options}),
              // Remove the counter from the title
              result[i].action_name,
              result[i].action_count
            ]));
          }
          return RSVP.all(promise_list);
        })
        .push(function (result_list) {
          if (result_list.length) {
            return domsugar(
              "ul",
              {
                "data-role": "listview",
                "data-theme": "c",
                "class": "document-listview ui-listview-inset ui-corner-all"
              },
              result_list.map(function (r) {
                var link = r[0], title = r[1], count = r[2];
                return domsugar(
                  "li",
                  {
                    "class": "ui-li-has-count",
                    "data-icon": "false"
                  },
                  [
                    domsugar(
                      "a",
                      {
                        "class": "ui-body-inherit",
                        "href": link
                      },
                      [
                        title,
                        " ",
                        domsugar(
                          "span",
                          { "class": "ui-li-count" },
                          [count.toString()]
                        )
                      ]
                    )
                  ]
                );
              })
            );
          }
          return gadget.translate("All work caught up!")
            .push(function (messageNoWorklist) {
              return domsugar("p", [messageNoWorklist]);
            });
        })
        .push(function (dom_list) {
          domsugar(
            gadget.element.querySelector('.document_list'),
            [dom_list]
          );
        });
    });
}(window, rJS, RSVP, Query, domsugar));