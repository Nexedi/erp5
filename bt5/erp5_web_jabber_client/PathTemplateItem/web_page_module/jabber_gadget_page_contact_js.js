/*global window, rJS, RSVP, Handlebars*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Handlebars) {
  "use strict";

  function compareContact(a, b) {
    var result;
    if (a.new_message && (!b.new_message)) {
      result = -1;
    } else if (b.new_message && (!a.new_message)) {
      result = 1;
    } else if (a.status && (!b.status)) {
      result = -1;
    } else if (b.status && (!a.status)) {
      result = 1;
    } else if (b.jid < a.jid) {
      result = 1;
    } else if (a.jid < b.jid) {
      result = -1;
    } else {
      result = 0;
    }
    return result;
  }

  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                         .getElementById("contact-list-template")
                         .innerHTML,
    table_template = Handlebars.compile(source);

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
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function () {
      var page_gadget = this,
        contact_list = [],
        gadget = this;

      return page_gadget.updateHeader({
        page_title: 'Contact'
      })
        .push(function () {
          return page_gadget.jio_allDocs({select_list: ['jid', 'read', 'offline']});
        })
        .push(function (result) {
          var i,
            contact,
            promise_list = [];
          for (i = 0; i < result.data.total_rows; i += 1) {
            contact = result.data.rows[i].value;
            contact_list.push({
              jid: contact.jid,
              new_message: !contact.read,
              status: !contact.offline
            });
            promise_list.push(gadget.getUrlFor({command: 'display', options: {page: 'dialog', jid: contact.jid}}));
          }
          return RSVP.all(promise_list);
        })
        .push(function (url_list) {
          var i;
          for (i = 0; i < url_list.length; i += 1) {
            contact_list[i].url = url_list[i];
          }
          contact_list.sort(compareContact);
          gadget.props.element.innerHTML =
            table_template({
              contact: contact_list
            });
        });
    });

}(window, rJS, RSVP, Handlebars));