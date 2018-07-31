/*global window, rJS, RSVP, URI, SimpleQuery, ComplexQuery, Query, navigator */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP, URI, SimpleQuery, ComplexQuery, Query, navigator) {
  "use strict";

  function setjIOERP5Configuration(gadget) {
    var erp5_url = gadget.state.erp5_url;
    return new RSVP.Queue()
      .push(function () {
        return RSVP.all([
          gadget.getSetting("portal_type", "Web Page"),
          gadget.getSetting("erp5_attachment_synchro", ""),
          gadget.getSetting("default_view_reference", 'jio_view')
        ]);
      })
      .push(function (result) {
        var configuration = {},
          jio_query_list = [],
          attachment_synchro = result[1] !== "",
          extended_attachment_url = result[1],
          portal_type = result[0].split(','),
          query = '',
          i,
          // https://bugs.chromium.org/p/chromium/issues/detail?id=375297
          // mobile device memory is limited for blob,
          // we reach this limit with parallel operation.
          is_low_memory = (navigator.userAgent.indexOf("Chrome") > 0) &&
            (navigator.userAgent.indexOf('Mobile') > 0);

        for (i = 0; i < portal_type.length; i += 1) {
          jio_query_list.push(new SimpleQuery({
            key: "portal_type",
            operator: "",
            type: "simple",
            value: portal_type[i]
          }));
        }

        query = Query.objectToSearchText(new ComplexQuery({
          operator: "OR",
          query_list: jio_query_list,
          type: "complex"
        }));

        configuration = {
          type: "replicate",
          // XXX This drop the signature lists...
          query: {
            query: query,
            limit: [0, 50],
            sort_on: [["modification_date", "descending"]]
          },
          use_remote_post: true,
          conflict_handling: 1,
          parallel_operation_attachment_amount: is_low_memory ? 1 : 10,
          parallel_operation_amount: is_low_memory ? 1 : 10,
//          signature_hash_key: "modification_date",
          check_local_attachment_modification: attachment_synchro,
          check_local_attachment_creation: attachment_synchro,
          check_remote_attachment_modification: attachment_synchro,
          check_remote_attachment_creation: attachment_synchro,
          check_remote_attachment_deletion: attachment_synchro,
          check_local_modification: true,
          check_local_creation: true,
          check_local_deletion: false,
          check_remote_modification: true,
          check_remote_creation: true,
          check_remote_deletion: true,
          signature_sub_storage: {
            type: "query",
            sub_storage: {
              type: "uuid",
              sub_storage: {
                type: "indexeddb",
                database: "officejs-erp5-hash"
              }
            }
          },
          local_sub_storage: {
            type: "query",
            schema: {"modification_date": {type: "string", format: "date-time"}},
            sub_storage: {
              type: "uuid",
              sub_storage: {
                type: "indexeddb",
                database: "officejs-erp5"
              }
            }
          },
          remote_sub_storage: {
            type: "saferepair",
            sub_storage: {
              type: "mapping",
              attachment_list: ["data"],
              attachment: {
                "data": {
                  "get": {
                    "uri_template": (new URI("hateoas"))
                                   .absoluteTo(erp5_url)
                                   .toString() + extended_attachment_url
                  },
                  "put": {
                    "erp5_put_template": (new URI("hateoas")).absoluteTo(erp5_url)
                      .toString() + "/{+id}/Base_edit"
                  }
                }
              },
              sub_storage: {
                type: "erp5",
                url: (new URI("hateoas"))
                    .absoluteTo(erp5_url)
                    .toString(),
                default_view_reference: result[2]
              }
            }
          }
        };
        return gadget.setSetting('jio_storage_description', configuration);
      })
      .push(function () {
        return gadget.setSetting('jio_storage_name', "ERP5");
      })
      .push(function () {
        return gadget.setSetting('storage_attachment_issue', true);
      })
      .push(function () {
        return gadget.setGlobalSetting('erp5_url', erp5_url);
      })
      .push(function () {
        return gadget.setSetting('sync_reload', true);
      })
      .push(function () {
        return gadget.redirect({command: "display", options: {page: 'ojs_sync', auto_repair: 'true'}});
      });
  }

  var gadget_klass = rJS(window);

  gadget_klass
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          g.props.deferred = RSVP.defer();
        });
    })
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("reload", "reload")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareMethod("getGlobalSetting", function (key) {
      var gadget = this;
      return gadget.getDeclaredGadget("global_setting_gadget")
        .push(function (global_setting_gadget) {
          return global_setting_gadget.getSetting(key);
        });
    })
    .declareMethod("setGlobalSetting", function (key, value) {
      var gadget = this;
      return gadget.getDeclaredGadget("global_setting_gadget")
        .push(function (global_setting_gadget) {
          return global_setting_gadget.setSetting(key, value);
        });
    })

    /////////////////////////////////////////
    // Form submit
    /////////////////////////////////////////
    .onEvent('submit', function () {
      var gadget = this;
      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (content) {
          gadget.state.erp5_url = content.erp5_url;
          return setjIOERP5Configuration(gadget);
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .declareMethod('render', function () {
      var gadget = this;
      return gadget.getUrlFor({command: 'display', options: {page: 'ojs_configurator'}})
        .push(function (url) {
          return gadget.updateHeader({
            page_title: "Connect To ERP5 Storage",
            back_url: url,
            submit_action: true,
            panel_action: false
          });
        });
    })

    .declareService(function () {
      var gadget = this;

      return gadget.declareGadget("gadget_officejs_setting.html", {
        "scope": "global_setting_gadget",
        "element": gadget.element.querySelector(".global_setting_gadget"),
        "sandbox": "iframe"
      })
        .push(function (global_setting_gadget) {
          return global_setting_gadget.getSetting(
            "erp5_url",
            "https://nexedijs.erp5.net"
          );
        })
        .push(function (erp5_url) {
          gadget.state.erp5_url = erp5_url;
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {
              "_embedded": {"_view": {
                "my_erp5_url": {
                  "description": "",
                  "title": "Connection Url",
                  "default": gadget.state.erp5_url,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "erp5_url",
                  "hidden": 0,
                  "type": "StringField"
                }
              }},
              "_links": {
                "type": {
                  // form_list display portal_type in header
                  name: ""
                }
              }
            },
            form_definition: {
              group_list: [[
                "top",
                [["my_erp5_url"]]
              ]]
            }
          });
        })
        .push(function () {
          return gadget.getDeclaredGadget('access');
        })
        .push(function (sub_gadget) {
          return sub_gadget.render("ERP5");
        });
    });

}(window, rJS, RSVP, URI, SimpleQuery, ComplexQuery, Query, navigator));
