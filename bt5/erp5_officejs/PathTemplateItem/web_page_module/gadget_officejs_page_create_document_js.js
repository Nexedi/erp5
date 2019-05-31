/*global window, document, rJS, RSVP, Handlebars */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, document, rJS, RSVP, Handlebars) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    table_template = Handlebars.compile(gadget_klass.__template_element
                         .getElementById("table-template")
                         .innerHTML);

  function renderLinkList(gadget, title, icon, erp5_link_list) {
    // prepare links for template (replace @href for RJS link)
    return gadget.translateHtml(
      table_template({
        "definition_i18n": title,
        "definition_title": title,
        "definition_icon": icon,
        "document_list": erp5_link_list.map(function (erp5_link, index) {
          return {
            "title": erp5_link.title,
            "i18n": erp5_link.title,
            "link": erp5_link_list[index].href
          };
        })
      })
    );
  }

  gadget_klass
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getSetting", "getSetting")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("getHTMLElementList", function (portal_type_list, jio_key, parent_portal_type) {
      var gadget = this,
        i = 0,
        portal_type_info_list = [],
        portal_type,
        url_for_parameter_list = [],
        x;
      for (x = 0; x < portal_type_list.length; x += 1) {
        portal_type = portal_type_list[x];
        url_for_parameter_list.push({ command: 'change', options: {page: "add_element", jio_key: jio_key, portal_type: portal_type, parent_portal_type: parent_portal_type} });
        portal_type_info_list[i] = { reference: portal_type, title: portal_type};
        i += 1;
      }
      return gadget.getUrlForList(url_for_parameter_list)
        .push(function (url_list) {
          var html_element_list = [], j, element;
          for (j = 0; j < url_list.length; j += 1) {
            element = { href: url_list[j],
              icon: null,
              name: portal_type_info_list[j].reference,
              title: portal_type_info_list[j].title };
            html_element_list.push(element);
          }
          return html_element_list;
        });
    })

    .declareMethod("render", function (options) {
      var gadget = this,
        allowed_sub_types_list = options.allowed_sub_types_list.split(","),
        portal_type,
        document_title;
      return gadget.jio_get(options.jio_key)
        .push(function (document) {
          document_title = document.title;
          return document.portal_type;
        }, function () {
          document_title = options.portal_type;
          return options.portal_type;
        })
        .push(function (portal_type_result) {
          portal_type = portal_type_result;
          // TODO: somehow (a generic action?) get the path string:${object_url}/Base_viewNewContentDialog
          // for now hardcoded
          // get corresponding form definition (only contains a select field)
          return gadget.jio_get("portal_skins/erp5_hal_json_style/Base_viewNewContentDialog");
        })
        .push(function (form_result) {
          form_result.form_definition.title = "Create Document";
          return gadget.changeState({
            doc: { title: document_title, portal_type: allowed_sub_types_list },
            action_options: options,
            child_gadget_url: 'gadget_erp5_pt_form_dialog.html',
            form_type: 'dialog',
            form_definition: form_result.form_definition,
            view: "view"
          });
        });
    })

    .onStateChange(function () {
      var fragment = document.createElement('div'),
        gadget = this;
      while (this.element.firstChild) {
        this.element.removeChild(this.element.firstChild);
      }
      this.element.appendChild(fragment);
      return gadget.declareGadget("gadget_officejs_form_view.html", {element: fragment,
                                                                     scope: 'fg'})
        .push(function (form_view_gadget) {
          return form_view_gadget.render(gadget.state);
        });
    })

    .declareMethod('triggerSubmit', function () {
      return this.getDeclaredGadget('fg')
        .push(function (gadget) {
          return gadget.triggerSubmit();
        });
    });

}(window, document, rJS, RSVP, Handlebars));