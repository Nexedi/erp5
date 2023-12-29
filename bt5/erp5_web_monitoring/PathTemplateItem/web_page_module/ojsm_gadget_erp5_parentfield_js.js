/*global window, rJS, RSVP, Handlebars */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Handlebars) {
  "use strict";

  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
      .querySelector(".render-link-template")
      .innerHTML,
    link_template = Handlebars.compile(source);

  gadget_klass

    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    .declareMethod('render', function (options) {
      var gadget = this, state_dict = {}, i, software_instance;
      return new RSVP.Queue()
        .push(function () {
          return gadget.jio_allDocs({
            select_list: [
              "parent_url",
              "parent_id",
              "title",
              "opml_title",
              "portal_type",
              "_links",
              "_embedded",
              "reference",
              "aggregate_reference",
              "ipv6",
              "ipv4",
              "partition_id",
              "software_release"
            ],
            query: '(portal_type:"Software Instance") AND (parent_id:"' +
              options.parent_id + '")'
          });
        })
        .push(function (result) {
          if (result) {
            for (i = 0; i < result.data.total_rows; i += 1) {
              software_instance = result.data.rows[i].value;
            }
          } else {
            software_instance = {};
          }
          switch (options.field) {
          case "instance_tree":
            var opml_doc;
            return new RSVP.Queue()
              .push(function () {
                return gadget.jio_get(options.parent_id);
              })
              .push(function (outline_doc) {
                return RSVP.all([outline_doc.parent_id,
                                 gadget.jio_get(outline_doc.parent_url)]);
              })
              .push(function (doc_list) {
                opml_doc = doc_list[1];
                return gadget.getUrlFor({command: 'push_history', options: {
                  jio_key: doc_list[0]
                }});
              })
              .push(function (hosting_url) {
                state_dict.content = link_template({
                  url: hosting_url,
                  title: opml_doc.title
                });
                return gadget.changeState(state_dict);
              });
          case "software_instance":
            if (software_instance.reference) {
              return new RSVP.Queue()
                .push(function () {
                  return gadget.getUrlFor({command: 'push_history', options: {
                    jio_key: software_instance.reference
                  }});
                })
                .push(function (hosting_url) {
                  state_dict.content = link_template({
                    url: hosting_url,
                    title: software_instance.title
                  });
                  return gadget.changeState(state_dict);
                });
            } else {
              state_dict.content = link_template({
                url: '*',
                title: options.channel_item
              });
              return gadget.changeState(state_dict);
            }
          case "computer":
            state_dict.content = software_instance.aggregate_reference;
            return gadget.changeState(state_dict);
          case "partition":
            state_dict.content = software_instance.partition_id;
            return gadget.changeState(state_dict);
          case "partition_ipv6":
            state_dict.content = software_instance.ipv6;
            return gadget.changeState(state_dict);
          case "software_release":
            state_dict.content = link_template({
              url: software_instance.software_release,
              title: "Access Software release",
              target: "_blank"
            });
            return gadget.changeState(state_dict);
          default:
            state_dict.content = "";
            return gadget.changeState(state_dict);
          }
        });
    })

    .onStateChange(function (modification_dict) {
      this.element.innerHTML = modification_dict.content;
    });

}(window, rJS, RSVP, Handlebars));