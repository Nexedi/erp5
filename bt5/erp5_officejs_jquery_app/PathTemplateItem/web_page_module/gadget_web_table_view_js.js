/*globals window, rJS, Handlebars, RSVP, loopEventListener, console*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS, Handlebars, loopEventListener) {
  "use strict";

  function saveContent(gadget, submit_event) {
    var i,
      doc = gadget.options.doc,
      now = new Date();
    doc.parent_relative_url = "web_page_module";
    doc.portal_type = "Web Table";
    doc.modification_date = now.toISOString();
    for (i = 0; i < submit_event.target.length; i += 1) {
      // XXX Should check input type instead
      if (submit_event.target[i].name) {
        doc[submit_event.target[i].name] = submit_event.target[i].value;
      }
    }
    return new RSVP.Queue()
      .push(function () {
        return gadget.getDeclaredGadget("my_text_content");
      })
      .push(function (text_content_gadget) {
        return text_content_gadget.getContent();
      })
      .push(function (data) {
        doc.text_content = data.text_content;
        return gadget.put(gadget.options.jio_key, doc);
      });
  }

  function maximize(gadget) {
    var iframe = gadget.props.element.querySelector('iframe'),
      iframe_class_string = iframe.getAttribute('class') || "",
      class_name = "ui-content-maximize",
      class_index = iframe_class_string.indexOf(class_name);
    if (class_index === -1) {
      iframe_class_string += ' ' + class_name;
      iframe.setAttribute('style', '');
      iframe.setAttribute('class', iframe_class_string);
      return;
    }
    iframe_class_string = iframe_class_string.substring(0, class_index) +
      iframe_class_string.substring(class_index + class_name.length);
    iframe.setAttribute('style', 'width:100%; border: 0 none; height: 600px');
    iframe.setAttribute('class', iframe_class_string);
    return;
  }

  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
      .querySelector(".view-web-page-template")
      .innerHTML,
    template = Handlebars.compile(source);


  gadget_klass
    .ready(function (g) {
      g.props = {};
      g.options = null;
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          g.props.deferred = RSVP.defer();
        });
    })

    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("get", "jio_get")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("put", "jio_put")
    .declareAcquiredMethod('allDocs', 'jio_allDocs')
    .declareAcquiredMethod("redirect", "redirect")

    .allowPublicAcquisition('triggerMaximize', function () {
      var gadget = this;
      return RSVP.Queue()
        .push(function () {
          return maximize(gadget);
        })
        .fail(function (e) {
          console.log(e);
        });
    })

    .allowPublicAcquisition('triggerSubmit', function (option) {
      if (option[0] === "maximize" || option === "maximize") {
        var gadget = this;
        return RSVP.Queue()
          .push(function () {
            return maximize(gadget);
          });
      }
      return this.props.element.querySelector('button').click();
    })

    .declareMethod('triggerSubmit', function (option) {
      if (option[0] === "maximize" || option === "maximize") {
        var gadget = this;
        return RSVP.Queue()
          .push(function () {
            return maximize(gadget);
          });
      }
      return this.props.element.querySelector('button').click();
    })

    .declareMethod("render", function (options) {
      var gadget = this;
      gadget.options = options;
      gadget.options.doc.title = gadget.options.doc.title || "";
      return new RSVP.Queue()
        .push(function () {
          return gadget.translateHtml(template(options.doc));
        })
        .push(function (html) {
          gadget.props.element.innerHTML = html;
          return gadget.updateHeader({
            title: options.doc.title + " | Web Table",
            save_action: true,
            maximize_action: true,
            maximized: gadget.options.doc.title !== ""
          });
        })
        .push(function () {
          return gadget.props.deferred.resolve();
        });
    })

    /////////////////////////////////////////
    // Render text content gadget
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this,
        text_gadget = null;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return gadget.declareGadget(
            "../officejs_web_table_editor_gadget/development/",
            {
              scope: "my_text_content",
              sandbox: "iframe",
              element: gadget.props.element.querySelector(".document-content")
            }
          );
        })
        .push(function (text_content_gadget) {
          var iframe = gadget.props.element.querySelector('iframe');
          iframe.setAttribute(
            'style',
            'width:100%; border: 0 none; height: 600px'
          );
          text_gadget = text_content_gadget;
          return text_content_gadget.render({
            "key": 'text_content',
            "value": gadget.options.doc.text_content
          });
        })
        .push(function () {
          return text_gadget.getElement();
        }, function (error) {
          var display_error_element;
          if (error.message.indexOf("Timeout while loading:") === 0 ||
              error.indexOf("Timed out after ") === 0) {

            display_error_element =
              gadget.props.element.querySelector(
                "form div.center"
              );
            display_error_element.innerHTML =
                  '<br/><p style="color: red"></p><br/><br/>' +
                  display_error_element.innerHTML;
            display_error_element.querySelector('p').textContent =
              "TIMEOUT: The editor gadget is taking too long to load but is" +
              " currently being cached, please wait for the page to load" +
              " (check your browser loading icon) and then refresh.";
          } else {
            throw error;
          }
        })
        .push(function () {
          if (gadget.options.doc.title !== "") {
            return gadget.triggerSubmit("maximize");
          }
        });
    })

    /////////////////////////////////////////
    // Form submit
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          return loopEventListener(
            gadget.props.element.querySelector('form'),
            'submit',
            true,
            function (event) {
              return saveContent(gadget, event);
            }
          );
        });
    });

}(window, RSVP, rJS, Handlebars, loopEventListener));