/*global window, rJS, RSVP, domsugar, Reveal, URL*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function (window, rJS, RSVP, domsugar, Reveal, URL) {
  "use strict";

  function fixupERP5UrlCompatibility(jio_key, url) {
    console.log(jio_key);
    if (!jio_key) {
      return url;
    }
    return new URL(
      url,
      new URL(jio_key + '/', window.location.href).href
    ).href;
  }

  function getSlideElementList(presentation_html) {
    // Convert to an Array so that array methods can be used to reorder slides
    return Array.prototype.slice.call(domsugar('div', {
      'class': 'slide_list',
      html: presentation_html
    }).querySelectorAll(':scope > section'));
  }

  function replaceNode(current_node, new_tag) {
    var fragment = domsugar(new_tag);

    while (current_node.firstChild) {
      fragment.appendChild(current_node.firstChild);
    }
    current_node.parentNode.removeChild(
      current_node
    );
    return fragment;
  }

  function cleanupSlide(slide_element, jio_key) {
    var detail_list = Array.prototype.slice.call(
      slide_element.querySelectorAll(':scope > details')
    ),
      len = detail_list.length,
      i,
      section_element;

    if (len > 0) {
      // Create the first vertical section containing every else than details
      section_element = domsugar('section');
      while (slide_element.firstChild) {
        section_element.appendChild(slide_element.firstChild);
      }
      slide_element.appendChild(section_element);

      // Transform every details into a section,
      // and move it outside the first vertical section
      for (i = 0; i < len; i += 1) {
        if (detail_list[i].firstChild) {
          slide_element.appendChild(replaceNode(detail_list[i], 'section'));
        } else {
          // Drop empty details element
          section_element.removeChild(detail_list[i]);
        }
      }
    }

    // Rewrite img url to support sub document ID
    detail_list = Array.prototype.slice.call(
      slide_element.querySelectorAll('img')
    );
    len = detail_list.length;
    for (i = 0; i < len; i += 1) {
      console.log('img', detail_list[i]);
      detail_list[i].src = fixupERP5UrlCompatibility(
        jio_key,
        detail_list[i].src
      )
    }


    return slide_element;
  }

  function cleanupPresentationFormat(presentation_html, jio_key) {
    var slide_list = getSlideElementList(presentation_html),
      i,
      len = slide_list.length;
    for (i = 0; i < len; i += 1) {
      cleanupSlide(slide_list[i], jio_key);
    }
    return domsugar('div', {class: 'reveal'}, [
      domsugar('div', {class: 'slides'}, slide_list)
    ]);
  }

  ///////////////////////////////////////////////////
  // Gadget
  ///////////////////////////////////////////////////
  rJS(window)


    .declareMethod('render', function (options) {
      return this.changeState({
        value: options.value || "",
        jio_key: options.jio_key
      });
    })

    .onStateChange(function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          domsugar(gadget.element, [
            cleanupPresentationFormat(gadget.state.value, gadget.state.jio_key)
          ]);

          return Reveal.initialize(gadget.element, {
            controls: true,
            progress: true,
            history: true,
            center: false,
            transition: 'slide',
            // Exposes the reveal.js API through window.postMessage
            postMessage: true,
            // Dispatches all reveal.js events to the parent window
            // through postMessage
            postMessageEvents: false
          });
        })
        .push(function () {
          Reveal.configure({
            slideNumber: 'c / t',
            // XXX This will not work if iframe is from another domain
            width: window.parent.innerWidth,
            height: window.parent.innerHeight,
            minScale: 0.01,
            maxScale: 10
          });
          Reveal.layout();
        });
    });


}(window, rJS, RSVP, domsugar, Reveal, URL));