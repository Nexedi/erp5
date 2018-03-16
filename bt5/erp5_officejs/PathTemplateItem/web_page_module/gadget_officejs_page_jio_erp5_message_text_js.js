/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (document, window, rJS, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("getSetting", 'getSetting')
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')


    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
  
    .allowPublicAcquisition('notifySubmit', function () {
      return this.triggerSubmit();
    })

    .declareMethod("render", function (options) {
      return this.changeState({
        doc: {}
      });
    })

    .onEvent('submit', function () {
      var gadget = this;
      var content;
    
      return gadget.notifySubmitting()
        .push(function () {
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (result) {

          content = result;
          return RSVP.all([
              gadget.getSetting('portal_type'),
              gadget.getSetting('parent_relative_url')
            ]);
        })
        .push(function (result) {
          var portal_type = result[0].split(',')[0];
          var parent_relative_url = result[1].split(',')[0];
        
          if (content.text_content !== "") {
        
            var text_html = document.createElement("html");
            text_html.innerHTML = content.text_content;
            var title = text_html.children[1].firstElementChild.innerText.split(' ').slice(0, 4).join('_');

            return gadget.jio_post({
                "title": title,
                portal_type: portal_type,
                parent_relative_url: parent_relative_url
              });
          }
        })
    
       .push(function (id) {
          if (id)
            return gadget.jio_putAttachment(id, 'data', content.text_content);
        })
       .push(function (result) {
        return gadget.redirect({command: 'display', options: {page: 'ojs_message_front', jio_key: result}});
      });

    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .onStateChange(function () {
      var gadget = this;
      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {
              "_embedded": {"_view": {
                /*"my_title": {
                  "description": "",
                  "title": "Title",
                  "default": gadget.state.doc.title,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "title",
                  "hidden": 0,
                  "type": "StringField"
                },
                "my_reference": {
                  "description": "",
                  "title": "Reference",
                  "default": gadget.state.doc.reference,
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
                  "default": gadget.state.doc.version,
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
                  "default": gadget.state.doc.language,
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
                  "default": gadget.state.doc.description,
                  "css_class": "",
                  "required": 0,
                  "editable": 1,
                  "key": "description",
                  "hidden": 0,
                  "type": "TextAreaField"
                },*/
                "my_content": {
                  "default": gadget.state.doc.text_content,
                  "css_class": "",
                  "required": 0,
                  "editable": 1,
                  "key": "text_content",
                  "hidden": 0,
                  "renderjs_extra": '{"editor": "fck_editor",' +
                    '"maximize": "auto"}',
                  "type": "GadgetField",
                  "url": "gadget_editor.html",
                  "sandbox": "public"
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
                [["my_title"], ["my_reference"]]
              ], [
                "right",
                [["my_version"], ["my_language"]]
              ], [
                "center",
                [["my_description"]]
              ], [
                "bottom",
                [["my_content"]]
              ]]
            }
          });
        })
        .push(function (result) {
          return RSVP.all([
            gadget.getUrlFor({command: 'display', options: {page: 'ojs_message_front'}}),
            gadget.getUrlFor({command: 'selection_previous'}),
            gadget.getUrlFor({command: 'selection_next'})
          ]);
        })
        .push(function (url_list) {
          return gadget.updateHeader({
            page_title: gadget.state.doc.title,
            save_action: true,
            selection_url: url_list[0]
            //previous_url: url_list[1],
           // next_url: url_list[2]
          });
        });
    })
  .declareService(function () {
    //return this.triggerMaximize(true);
  });
}(document, window, rJS, RSVP));
