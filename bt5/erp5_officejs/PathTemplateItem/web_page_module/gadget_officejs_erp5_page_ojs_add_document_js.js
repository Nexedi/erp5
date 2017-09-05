/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  var content_type = {
    Spreadsheet: 'application/x-asc-spreadsheet',
    Presentation: 'application/x-asc-presentation',
    Text: 'application/x-asc-text'
  };

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_post", "jio_post")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .onEvent('submit', function () {
      var gadget = this;
      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (doc) {
          doc.modification_date = (new Date()).toISOString();
          if (content_type.hasOwnProperty(doc.portal_type)) {
            doc.content_type = content_type[doc.portal_type];
          }
          return gadget.jio_post(doc);
        })
        .push(function () {
          // Workaround, find a way to open document without break gadget.
          return gadget.redirect({"command": "change", "options": {"page": "ojs_document_list"}});
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .declareMethod("render", function () {
      var gadget = this;
      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getDeclaredGadget('form_view'),
            gadget.getSetting('portal_type'),
            gadget.getSetting('parent_relative_url')
          ]);
        })
        .push(function (result) {
          return result[0].render({
            erp5_document: {
              "_embedded": {"_view": {
                "my_title": {
                  "description": "The name of a document in ERP5",
                  "title": "Title",
                  "default": "",
                  "css_class": "",
                  "required": 0,
                  "editable": 1,
                  "key": "title",
                  "hidden": 0,
                  "type": "StringField"
                },
                "my_reference": {
                  "description": "The name of a document in ERP5",
                  "title": "Reference",
                  "default": "",
                  "css_class": "",
                  "required": 0,
                  "editable": 1,
                  "key": "reference",
                  "hidden": 0,
                  "type": "StringField"
                },
                "my_version": {
                  "description": "",
                  "title": "Version",
                  "default": "",
                  "css_class": "",
                  "required": 0,
                  "editable": 1,
                  "key": "version",
                  "hidden": 0,
                  "type": "StringField"
                },
                "my_language": {
                  "description": "",
                  "title": "Language",
                  "default": "",
                  "css_class": "",
                  "required": 0,
                  "editable": 1,
                  "key": "language",
                  "hidden": 0,
                  "type": "StringField"
                },
                "my_description": {
                  "description": "",
                  "title": "Description",
                  "default": "",
                  "css_class": "",
                  "required": 0,
                  "editable": 1,
                  "key": "description",
                  "hidden": 0,
                  "type": "TextAreaField"
                },
                "my_portal_type": {
                  "description": "The name of a document in ERP5",
                  "title": "Portal Type",
                  "default": result[1],
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "portal_type",
                  "hidden": 1,
                  "type": "StringField"
                },
                "my_parent_relative_url": {
                  "description": "",
                  "title": "Parent Relative Url",
                  "default": result[2],
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "parent_relative_url",
                  "hidden": 1,
                  "type": "StringField"
                },
                "my_text_content": {
                  "description": "",
                  "title": "Text Content",
                  "default": "",
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "text_content",
                  "hidden": 1,
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
                "left",
                [["my_title"], ["my_reference"], ["my_version"], ["my_language"], ["my_description"],
                  ["my_portal_type"], ["my_parent_relative_url"]]
              ]]
            }
          });
        })
        .push(function () {
          return gadget.getSetting('document_title');
        })
        .push(function (document_title) {
          return gadget.updateHeader({
            page_title: "New " + document_title,
            save_action: true
          });
        });
    });
}(window, rJS, RSVP));