/*globals window, rJS, Handlebars, RSVP, loopEventListener, console, document, jIO, Blob*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, document, RSVP, rJS, Handlebars, loopEventListener, jIO,
            Blob) {
  "use strict";

  function this_func_link(name) {
    return function (opt) {
      return this[name].apply(this, opt);
    };
  }

  function renderOnlyOfficeGadget(gadget) {
    var text_gadget;
    return gadget.declareGadget(
      "../ooffice_presentation_gadget/development/",
      {
        scope: "my_text_content",
        sandbox: "iframe",
        element: gadget.props.element.querySelector(".document-content")
      }
    )
      .push(function (text_content_gadget) {
        text_gadget = text_content_gadget;
        gadget.setFillStyle();
        // switchMaximizeMode(gadget);
        return text_content_gadget;
      })
      .push(function (text_content_gadget) {
        return text_content_gadget.render({
          "key": 'text_content',
          "value": gadget.options.data
        });
      })
      .push(function () {
        return text_gadget.getElement();
      });
  }
  function saveContent(gadget, submit_event) {
    var i,
      doc = gadget.options.doc;
    doc.modification_date = (new Date()).toISOString();
    for (i = 0; i < submit_event.target.length; i += 1) {
      // XXX Should check input type instead
      if (submit_event.target[i].name) {
        doc[submit_event.target[i].name] = submit_event.target[i].value;
      }
    }
    return new RSVP.Queue()
      .push(function () {
        if (gadget.options.doc.content_type === undefined ||
            gadget.options.doc.content_type.indexOf("application/x-asc") === 0
            ) {
          gadget.options.doc.content_type = "application/x-asc-presentation";
          return gadget.getDeclaredGadget("my_text_content");
        }
        return undefined;
      })
      .push(function (text_content_gadget) {
        if (text_content_gadget !== undefined) {
          return text_content_gadget.getContent();
        }
        return undefined;
      })
      .push(function (datauri) {
        if (datauri !== undefined) {
          return gadget.jio_putAttachment(gadget.options.jio_key, 'data',
            jIO.util.dataURItoBlob(datauri.text_content));
        }
        return;
      })
      .push(function () {
        return gadget.jio_put(gadget.options.jio_key, doc);
      });
  }

  function getMaxHeight(wrap_obj) {
    var height;
    if (wrap_obj) {
      height = window.innerHeight - wrap_obj.offsetTop;
    } else {
      height = window.innerHeight;
    }
    if (height < 400) {
      height = 400;
    }
    return height + "px";
  }

  function setFillStyle(gadget) {
    var iframe = gadget.props.element.querySelector('iframe'),
      height = getMaxHeight(iframe),
      width = "100%";
    iframe.setAttribute(
      'style',
      'width: ' + width + '; border: 0 none; height: ' + height
    );
    return {height: height, width: width};
  }

  function switchMaximizeMode(gadget) {
    var iframe = gadget.props.element.querySelector('iframe'),
      iframe_class_string = iframe.getAttribute('class') || "",
      class_name = "ui-content-maximize",
      class_index = iframe_class_string.indexOf(class_name);
    if (class_index === -1) {
      iframe_class_string += ' ' + class_name;
      iframe.setAttribute('style', 'background: white;');
      iframe.setAttribute('class', iframe_class_string);
      return true;
    }
    iframe_class_string = iframe_class_string.substring(0, class_index) +
      iframe_class_string.substring(class_index + class_name.length);
    iframe.setAttribute('style', 'width:100%; border: 0 none; height: 600px');
    iframe.setAttribute('class', iframe_class_string);
    return false;
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
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod('getSetting', 'getSetting')
    .allowPublicAcquisition("getSetting", this_func_link("getSetting"))
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")

    .allowPublicAcquisition('setFillStyle', function () {
      return setFillStyle(this);
    })

    .declareMethod('setFillStyle', function () {
      return setFillStyle(this);
    })

    .allowPublicAcquisition('triggerSubmit', function (option) {
      if (option[0] === "maximize" || option === "maximize") {
        var gadget = this;
        return RSVP.Queue()
          .push(function () {
            return switchMaximizeMode(gadget);
          });
      }
      return this.props.element.querySelector('button').click();
    })

    .declareMethod('triggerSubmit', function (option) {
      if (option[0] === "maximize" || option === "maximize") {
        var gadget = this;
        return RSVP.Queue()
          .push(function () {
            return switchMaximizeMode(gadget);
          });
      }
      return this.props.element.querySelector('button').click();
    })

    .declareMethod("render", function (options) {
      var gadget = this;
      gadget.options = options;

      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.jio_get(options.jio_key),
            gadget.jio_getAttachment(options.jio_key, "data")
              .push(undefined, function (error) {
                if (error.status_code === 404) {
                  return new Blob();
                }
                throw error;
              })
          ]);
        })
        .push(function (result) {
          return new RSVP.Queue()
            .push(function () {
              if (result[0].content_type === undefined ||
                  result[0].content_type.indexOf("application/x-asc") === 0) {
                return jIO.util.readBlobAsDataURL(result[1]);
              }
              return jIO.util.readBlobAsText(result[1]);
            })
            .push(function (evt) {
              result[1] = evt.target.result;
              return result;
            });
        })
        .push(function (list) {
          var doc = list[0],
            data = list[1];
          gadget.options.doc = doc;
          gadget.options.data = data;
          gadget.options.doc.title = gadget.options.doc.title || "";
          return new RSVP.Queue()
            .push(function () {
              return gadget.translateHtml(template(options.doc));
            })
            .push(function (html) {
              gadget.props.element.innerHTML = html;
              return gadget.updateHeader({
                title: options.doc.title + " | " + options.doc.portal_type,
                maximize_action: true,
                maximized: (gadget.options.doc.title !== ""),
                save_action: true
              });
            })
            .push(function () {
              return gadget.props.deferred.resolve();
            });
        });
    })

    /////////////////////////////////////////
    // Render text content gadget
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return gadget.props.deferred.promise;
        })
        .push(function () {
          var iframe;
          if (gadget.options.doc.content_type === undefined ||
              gadget.options.doc.content_type.indexOf("application/x-asc") === 0
              ) {
            return renderOnlyOfficeGadget(gadget);
          }
          iframe = document.createElement("iframe");
          iframe.setAttribute(
            "src",
            "data:text/html," + gadget.options.data
          );
          gadget.props.element.querySelector(".document-content")
            .appendChild(iframe);
          return setFillStyle(gadget);
        })
        .push(function () {
          if (gadget.options.doc.title !== "") {
            return switchMaximizeMode(gadget);
          }
          return;
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

}(window, document, RSVP, rJS, Handlebars, loopEventListener, jIO, Blob));