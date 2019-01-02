/*globals window, RSVP, rJS, URL*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS, URL) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('triggerSubmit', function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .declareMethod("render", function () {
      var gadget = this;
      return gadget.updateHeader({
        page_title: 'Bookmark Manager Preferences',
        save_action: true
      })
        .push(function () {
          return RSVP.all([
            gadget.getSetting('bookmark_auto_redirect', true),
            gadget.getSetting(
              'bookmark_search_engine',
              "https://duckduckgo.com/?q="
            )
          ]);
        })
        .push(function (setting_list) {
          return gadget.changeState({
            auto_redirect: setting_list[0],
            search_engine: setting_list[1],
            share_url: (new URL(
                "#/?page=ojs_bookmark_dispatcher&search=%s", window.location
              )).href
          });
        });
    })

    .onStateChange(function () {
      var gadget = this;
      return gadget.getDeclaredGadget("form_view")
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {
              "_embedded": {"_view": {
                "my_share_url": {
                  "description": "To use the bookmark manager as a search " +
                    "engine, add this url to the search engine" +
                    "list of your browser",
                  "title": "Share Url",
                  "default": gadget.state.share_url,
                  "css_class": "",
                  "required": 0,
                  "editable": 1,
                  "key": "share_url",
                  "hidden": 0,
                  "type": "StringField"
                },
                "my_auto_redirect": {
                  "description": "Automatic redirection on single result",
                  "title": "Auto Redirection",
                  "default": gadget.state.auto_redirect,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "auto_redirect",
                  "hidden": 0,
                  "type": "CheckBoxField"
                },
                "my_search_engine": {
                  "description": "",
                  "title": "Search Engine",
                  "default": gadget.state.search_engine,
                  "css_class": "",
                  "required": 0,
                  "editable": 1,
                  "key": "search_engine",
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
                [["my_share_url"], ["my_auto_redirect"], ["my_search_engine"]]
              ]]
            }
          });
        });
    })
    .onEvent("submit", function () {
      var gadget = this;
      return gadget.notifySubmitting()
        .push(function () {
          return gadget.getDeclaredGadget("form_view");
        })
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (content) {
          return RSVP.all([
            gadget.setSetting('bookmark_auto_redirect', content.auto_redirect),
            gadget.setSetting('bookmark_search_engine', content.search_engine)
          ]);
        })
        .push(function () {
          return gadget.notifySubmitted({
            message: 'Preferences Saved',
            status: 'success'
          });
        });
    });

}(window, RSVP, rJS, URL));