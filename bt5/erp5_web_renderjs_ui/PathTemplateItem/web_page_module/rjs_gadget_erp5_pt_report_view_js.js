/*global window, document, rJS, RSVP, URI */
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 79 */
(function (window, document, rJS, RSVP, URI) {
  "use strict";

  function createSectionGadget(gadget, queue, report_section,
                               section_list_element) {
    var form_definition;
    queue
      .push(function () {
        if (report_section.hasOwnProperty('_embedded')) {
          return report_section._embedded.form_definition;
        }
        var uri = new URI(report_section._links.form_definition.href);
        return gadget.jio_getAttachment(uri.segment(2), "view");
      })
      .push(function (result) {
        form_definition = result;
        var section_element = document.createElement('div');
        section_list_element.appendChild(section_element);
        return gadget.declareGadget('gadget_erp5_pt_form_view.html', {
          element: section_element
        });
      })
      .push(function (form_gadget) {
        var erp5_document = {
          '_embedded': {
            '_view': report_section
          },
          '_links': {
            'type': {
              // form_view display portal_type in header
              name: ''
            }
          }
        };
        return form_gadget.render({erp5_document: erp5_document,
                                   form_definition: form_definition,
                                   editable: 0, title: report_section.title});
      });
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition('updateHeader', function (argument_list, scope) {
      // Fetch menu configuration from main form
      if (scope === 'form_view') {
        // report are not supposed to be editable
        var options = argument_list[0];
        delete options.save_action;
        return this.updateHeader(options);
      }
      return;
    })
    .declareMethod('render', function (options) {
      var form_gadget_url;
      if (options.editable) {
        form_gadget_url = 'gadget_erp5_pt_form_view_editable.html';
      } else {
        form_gadget_url = 'gadget_erp5_pt_form_view.html';
      }
      return this.changeState({
        erp5_document: options.erp5_document,
        form_definition: options.form_definition,
        form_gadget_url: form_gadget_url,
      });
    })
    .onStateChange(function (modification_dict) {
      var gadget = this,
        form_gadget,
        section_container_element = document.createElement('div'),
        report_section_list =
          gadget.state.erp5_document._embedded._view.report_section_list;
      return new RSVP.Queue()

        // Render the erp5 form
        .push(function () {
          if (modification_dict.hasOwnProperty('form_gadget_url')) {
            return gadget.declareGadget(gadget.state.form_gadget_url, {
              scope: 'form_view'
            });
          }
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (result) {
          form_gadget = result;
          return form_gadget.render({
            erp5_document: gadget.state.erp5_document,
            form_definition: gadget.state.form_definition,
            editable: 0
          });
        })

        // Render the report sections
        .push(function () {
          var i,
            queue = new RSVP.Queue();
          for (i = 0; i < report_section_list.length; i += 1) {
            createSectionGadget(gadget, queue, report_section_list[i],
                                section_container_element);
          }
          return queue;
        })

        // Modify the DOM if needed
        .push(function () {
          var form_view_element = gadget.element.querySelector('.form_view'),
            section_element =
              gadget.element.querySelector('.report_section_list');
          if (modification_dict.hasOwnProperty('form_gadget_url')) {
            // Clear first to DOM, append after to reduce flickering/manip
            while (form_view_element.firstChild) {
              form_view_element.removeChild(form_view_element.firstChild);
            }
            form_view_element.appendChild(form_gadget.element);
          }

          // Always replace the report section
          // XXX It could certainly be improved
          // Clear first to DOM, append after to reduce flickering/manip
          while (section_element.firstChild) {
            section_element.removeChild(section_element.firstChild);
          }
          section_element.appendChild(section_container_element);
        });

    })

    .declareMethod('checkValidity', function checkValidity() {
      return true;
    })
    .declareMethod('getContent', function getContent() {
      return {};
    })
    .declareMethod('triggerSubmit', function getContent() {
      return;
    });

}(window, document, rJS, RSVP, URI));