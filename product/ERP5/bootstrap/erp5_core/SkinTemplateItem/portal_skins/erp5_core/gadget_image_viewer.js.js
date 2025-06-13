/*global window, rJS, URL*/
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, URL) {
  'use strict';

  function addToRotation(rotation, degree) {
    rotation = (rotation + degree) % 360;
    if (rotation < 0) { rotation += 360; }
    return rotation;
  }

  function addToZoom(zoom, increment) {
    zoom += increment;
    // Limits of +5 and -4 are arbitrary. If we want to change the limits,
    // and the step of the zoom, we should redefine the related CSS class system.
    if (zoom > 5) { return 5; }
    if (zoom < -4) { return -4; }
    return zoom;
  }

  rJS(window)
    .setState({
      rotation: 0,
      zoom: 0
    })

    .declareAcquiredMethod("getTranslationList", "getTranslationList")

    .declareMethod('render', function (options) {
      return this.renderAsynchronously(options);
    })

    .declareJob('renderAsynchronously', function (options) {
      var gadget = this,
        translation_list = [];
      gadget.element.querySelectorAll("[data-i18n]").values().forEach(function (el) {
        translation_list.push([
          el.getAttribute("data-i18n"),
          el
        ]);
      });
      return gadget.getTranslationList(translation_list.map(function (x) {
        return x[0];
      }))
        .then(function (translation_result) {
          var i;
          for (i = 0; i < translation_list.length; i++) {
            translation_list[i][1].innerText = translation_result[i];
          }
          return gadget.changeState({
            src: options.value,
            quality: options.quality,
            format: options.format,
            alt: options.description || options.title
          });
        });
    })

    .onStateChange(function (modification_dict) {
      var gadget = this,
        className = "image-viewer-transformation";

      if (gadget.state.rotation) {
        className += " rotation-" + gadget.state.rotation;
      }

      if (gadget.state.zoom) {
        className += " zoom-" + gadget.state.zoom;
      }

      if (gadget.state.image_element === undefined && gadget.state.src) {
        var img_element = window.document.createElement("img"),
          src_attr = new URL(gadget.state.src);

        if (gadget.state.alt) {
          img_element.setAttribute("alt", gadget.state.alt);
        }

        if (gadget.state.quality) {
          src_attr.searchParams.set("quality", gadget.state.quality);
        }
        if (gadget.state.format) {
          src_attr.searchParams.set("format", gadget.state.format);
        }
        img_element.setAttribute("src", src_attr);

        gadget.element.querySelector(".gadget_image_viewer_content").appendChild(img_element);
        gadget.state.image_element = img_element;
      }

      gadget.state.image_element.className = className;
      return gadget;
    })

    .onEvent('click', function (event) {
      if (event.target.tagName === 'BUTTON') {
        switch (event.target.getAttribute('data-function')) {
        case 'reset':
          return this.changeState({rotation: 0, zoom: 0});
        case 'rotate-left':
          return this.changeState({rotation: addToRotation(this.state.rotation, -90)});
        case 'rotate-right':
          return this.changeState({rotation: addToRotation(this.state.rotation, 90)});
        case 'zoom-in':
          return this.changeState({zoom: addToZoom(this.state.zoom, 1)});
        case 'zoom-out':
          return this.changeState({zoom: addToZoom(this.state.zoom, -1)});
        }
      }
    })

    .declareMethod('getContent', function () {
      // The image viewer field never modifies a document
      return {};
    })

    .declareMethod('checkValidity', function () {
      return true;
    });
})(window, rJS, URL);
