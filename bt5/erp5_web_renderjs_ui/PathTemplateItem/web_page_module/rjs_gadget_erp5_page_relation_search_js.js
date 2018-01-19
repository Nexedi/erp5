/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, rJS, RSVP, Handlebars*/
(function (window, rJS, RSVP, Handlebars) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    search_source = gadget_klass.__template_element
                         .getElementById("search-template")
                         .innerHTML,
    search_template = Handlebars.compile(search_source);

  Handlebars.registerHelper('equal', function (left_value,
    right_value, options) {
    if (arguments.length < 3) {
      throw new Error("Handlebars Helper equal needs 2 parameters");
    }
    if (left_value !== right_value) {
      return options.inverse(this);
    }
    return options.fn(this);
  });


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
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("translateHtml", "translateHtml")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition('updateHeader', function (param_list) {
      return this.updateHeader({
        page_title: param_list[0].page_title,
        back_url: this.props.back_url,
        filter_action: true
      });
    })
    .declareMethod("render", function (options) {
      var gadget = this,
        select_template = options.select_template || "";
      return gadget.getUrlFor({command: 'history_previous'})
        .push(function (back_url) {
          gadget.props.back_url = back_url;
          return RSVP.all([
            gadget.jio_getAttachment(options.url, options.view),
            gadget.getDeclaredGadget('form_list')
          ]);
        })
        .push(function (results) {
          var form_gadget = results[1],
            listbox_render,
            field = results[0]._embedded._view[options.back_field.slice("field_".length)],
            html;

          gadget.props.listbox = field.listbox;
          gadget.props.listbox_key = Object.keys(field.listbox);
          gadget.props.field_title = field.title;

          if (field.proxy_listbox_ids_len) {
            if (select_template === "") {
              select_template = gadget.props.listbox_key[0];
            }
            listbox_render = gadget.props.listbox[select_template];
            html = search_template({
              options: gadget.props.listbox_key,
              select_template: select_template
            });
            gadget.props.element.querySelector(".left").innerHTML = html;
          } else {
            listbox_render = gadget.props.listbox[gadget.props.listbox_key[0]];
          }
          listbox_render.command = "history_previous";
          listbox_render.line_icon = true;
          return form_gadget.render({
            erp5_document: {"_embedded": {"_view": {
              "listbox": listbox_render
            }},
              "title": results[0].title,
              "_links": results[0]._links
              },
            form_definition: {
              group_list: [[
                "bottom",
                [["listbox"]]
              ]]
            }
          });
        })
        .push(function () {
          return gadget.translateHtml(gadget.props.element.querySelector(".left").innerHTML);
        })
        .push(function (html) {
          gadget.props.element.querySelector(".left").innerHTML = html;
        });
    })
    .declareMethod("triggerSubmit", function () {
      var argument_list = arguments;
      return this.getDeclaredGadget('form_list')
        .push(function (gadget) {
          return gadget.triggerSubmit.apply(gadget, argument_list);
        });
    })
    .onEvent('change', function (evt) {
      var target = evt.target,
        value;
      if (target.nodeName === 'SELECT') {
        value = target.options[target.selectedIndex].value;
        return this.redirect({
          command: 'change',
          options: {
            select_template: value
          }
        });
      }
    });

}(window, rJS, RSVP, Handlebars));