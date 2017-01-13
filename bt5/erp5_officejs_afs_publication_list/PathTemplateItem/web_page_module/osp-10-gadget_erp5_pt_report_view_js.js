/*global window, document, rJS, RSVP, URI */
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 79 */
(function (window, document, rJS, RSVP, URI) {
  "use strict";

  function createSectionGadget(gadget, queue, report_section) {
    var uri = new URI(report_section._links.form_definition.href),
      form_definition;
    queue
      .push(function () {
        return gadget.jio_getAttachment(uri.segment(2), "view");
      })
      .push(function (result) {
        form_definition = result;
        var section_list_element = gadget.props
            .element.querySelector('.report_section_list'),
          section_element = document.createElement('div');
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
                                   form_definition: form_definition});
      });
  }

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
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })

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
        return this.updateHeader.apply(this, argument_list);
      }
      return;
    })
    .declareMethod('render', function (options) {
      var erp5_document = options.erp5_document,
        form_definition = options.form_definition,
        rendered_form = erp5_document._embedded._view,
        gadget = this,
        report_section_list = rendered_form.report_section_list,
        form_gadget_url;

      delete options.erp5_document;
      delete options.form_definition;
      if (options.editable) {
        form_gadget_url = 'gadget_erp5_pt_form_view_editable.html';
      } else {
        form_gadget_url = 'gadget_erp5_pt_form_view.html';
      }

      return gadget.declareGadget(form_gadget_url, {
        element: gadget.props.element.querySelector('.form_view'),
        scope: 'form_view'
      })
        .push(function (view_gadget) {
          return view_gadget.render({erp5_document: erp5_document,
                                     form_definition: form_definition});
        })
        // Render the report sections
        .push(function () {
          var i,
            queue = new RSVP.Queue();
          for (i = 0; i < report_section_list.length; i += 1) {
            createSectionGadget(gadget, queue, report_section_list[i]);
          }
          return queue;
        });
    });

}(window, document, rJS, RSVP, URI));