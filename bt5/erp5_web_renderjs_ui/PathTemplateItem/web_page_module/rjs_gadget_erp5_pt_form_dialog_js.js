/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, rJS, RSVP, URI, loopEventListener, document */
(function (window, rJS, RSVP, URI, loopEventListener) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window);

  gadget_klass
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {};
    })

    // Assign the element to a variable
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })

    /////////////////////////////////////////////////////////////////
    // acquisition
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareAcquiredMethod("displayFormulatorValidationError",
                           "displayFormulatorValidationError")


    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('triggerSubmit', function () {
      this.props.element.querySelector('button').click();
    })
    .declareMethod('render', function (options) {
      var erp5_document = options.erp5_document,
        form_options = options.erp5_form || {},
        form_gadget = this;

      form_gadget.props.id = options.jio_key;
      form_gadget.props.view = options.view;
      form_gadget.props.editable = options.editable;
      form_gadget.props.action = erp5_document._embedded._view._actions.put;
      form_gadget.props.form_id = erp5_document._embedded._view.form_id;

      return form_gadget.getDeclaredGadget("erp5_form")

        .push(function (erp5_form) {
          var title = options.form_definition.title,
            i,
            icon,
            span = document.createElement("span"),
            section = form_gadget.__element.querySelector("section"),
            selector = form_gadget.__element.querySelector("h3"),
            view_list = erp5_document._links.action_workflow || [];

          for (i = 0; i < view_list.length; i += 1) {
            if (view_list[i].name === options.view) {
              title = view_list[i].title;
            }
          }

          // XXX hardcoded...
          switch (title) {
          case "Create User":
            icon = " ui-icon-user";
            break;
          case "Create Document":
            icon = " ui-icon-file-o";
            break;
          case "Change State":
            icon = " ui-icon-share-alt";
            break;
          case "Submit":
            icon = " ui-icon-check";
            break;
          default:
            icon = " ui-icon-random";
            break;
          }
          span.className = "ui-icon ui-icon-custom" + icon;
          span.textContent = "\u00A0";
          selector.appendChild(span);
          selector.appendChild(document.createTextNode(title));
          selector.setAttribute("data-i18n", "[last]" + title);

          // <span class="ui-icon ui-icon-custom ui-icon-random">&nbsp;</span>
          form_options.erp5_document = options.erp5_document;
          form_options.form_definition = options.form_definition;
          form_options.view = options.view;

          return new RSVP.Queue()
            .push(function () {
              return form_gadget.translateHtml(section.innerHTML);
            })
            .push(function (my_translation_html) {
              section.innerHTML = my_translation_html;
              return RSVP.all([
                erp5_form.render(form_options),
                form_gadget.getUrlFor({command: 'change', options: {page: undefined, view: undefined}}),
                form_gadget.getUrlFor({command: 'change', options: {page: "breadcrumb"}})
              ]);
            })
            .push(function (all_result) {
              return form_gadget.updateHeader({
                cancel_url: all_result[1],
                page_title: options.erp5_document.title,
                breadcrumb_url: all_result[2],
                submit_action: true
              });
            });
        });
    })


    .declareService(function () {
      var form_gadget = this;

      function formSubmit() {
        return form_gadget.notifySubmitting()
          .push(function () {
            return form_gadget.getDeclaredGadget("erp5_form");
          })
          .push(function (erp5_form) {
            return erp5_form.getContent();
          })
          .push(function (content_dict) {
            var data = {},
              key;

            data[form_gadget.props.form_id.key] =
                                    form_gadget.props.form_id['default'];
            // XXX Hardcoded
            data.dialog_id = form_gadget.props.form_id['default'];
            data.dialog_method = form_gadget.props.action.action;
            for (key in content_dict) {
              if (content_dict.hasOwnProperty(key)) {
                data[key] = content_dict[key];
              }
            }

            return form_gadget.jio_putAttachment(
              form_gadget.props.id,
              form_gadget.props.action.href,
              data
            );

          })
          .push(function (evt) {
            var location = evt.target.getResponseHeader("X-Location");
            if (location === undefined || location === null) {
              // No redirection, stay on the same document
              return form_gadget.getUrlFor({command: 'change', options: {view: "view", page: undefined}});
            }
            return RSVP.all([
              form_gadget.notifySubmitted(),
              form_gadget.redirect({command: 'push_history', options: {jio_key: new URI(location).segment(2), editable: form_gadget.props.editable}})
            ]);
          })
          .push(undefined, function (error) {
            if ((error.target !== undefined) && (error.target.status === 400)) {
              return form_gadget.notifySubmitted()
                .push(function () {
                  return form_gadget.notifyChange();
                })
                .push(function () {
                  return form_gadget.displayFormulatorValidationError(JSON.parse(error.target.responseText));
                });
            }
            throw error;
          });
      }

      // Listen to form submit
      return loopEventListener(
        form_gadget.props.element.querySelector('form'),
        'submit',
        false,
        formSubmit
      );
    });

}(window, rJS, RSVP, URI, loopEventListener));