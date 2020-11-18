/*global window, document, rJS, console, RSVP, domsugar*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function () {
  "use strict";

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

  function cleanupSlide(slide_element) {
    var detail_list = Array.prototype.slice.call(slide_element.querySelectorAll(':scope > details')),
      len = detail_list.length,
      i,
      section_element;
    console.log('cleanup', slide_element, detail_list);

    if (len > 0) {
      // Create the first vertical section containing every else than details
      section_element = domsugar('section');
      while (slide_element.firstChild) {
        section_element.appendChild(slide_element.firstChild);
      }
      slide_element.appendChild(section_element);

      // Transform every details into a section, and move it outside the first vertical section
      for (i = 0; i < len; i += 1) {
        slide_element.appendChild(replaceNode(detail_list[i], 'section'));
      }
    }
    return slide_element;
  }

  function cleanupPresentationFormat(presentation_html) {
    var slide_list = getSlideElementList(presentation_html),
      i,
      len = slide_list.length;
    for (i = 0; i < len; i += 1) {
      cleanupSlide(slide_list[i]);
    }
    return domsugar('div', {class: 'reveal'}, [
      domsugar('div', {class: 'slides'}, slide_list)
    ])
  }

  ///////////////////////////////////////////////////
  // Gadget
  ///////////////////////////////////////////////////
  rJS(window)


    .declareMethod('render', function (options) {
      return this.changeState({
        value: options.value || ""
      });
    })

    .onStateChange(function (modification_dict) {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          domsugar(gadget.element, [
            cleanupPresentationFormat(gadget.state.value)
          ]);

          // console.log(gadget.element.innerHTML);

          return Reveal.initialize(gadget.element, {
            controls: true,
            progress: true,
            history: true,
            center: false,
            transition: 'slide',
            // Exposes the reveal.js API through window.postMessage
            postMessage: true,
            // Dispatches all reveal.js events to the parent window through postMessage
            postMessageEvents: false
          });
        })
        .push(function () {
          return Reveal.configure({slideNumber: 'c / t'});
        });
    });


}());