/*jslint nomen: true, indent: 2 */
/*global window, rJS, domsugar, document, DOMParser, NodeFilter*/
(function (window, rJS, domsugar, document, DOMParser, NodeFilter) {
  "use strict";

  function startsWithOneOf(str, prefix_list) {
    var i;
    for (i = prefix_list.length - 1; i >= 0; i -= 1) {
      if (str.substr(0, prefix_list[i].length) === prefix_list[i]) {
        return true;
      }
    }
    return false;
  }

  var whitelist = {
    node_list: {
      BODY: true,
      P: true,
      H1: true,
      H2: true,
      H3: true,
      H4: true,
      H5: true,
      H6: true,
      UL: true,
      OL: true,
      LI: true,
      DL: true,
      DT: true,
      DD: true,
      BLOCKQUOTE: true,
      Q: true,
      I: true,
      B: true,
      CITE: true,
      EM: true,
      VAR: true,
      ADDRESS: true,
      DFN: true,
      U: true,
      INS: true,
      S: true,
      STRIKE: true,
      DEL: true,
      SUP: true,
      SUB: true,
      MARK: true,
      TT: true,
      PRE: true,
      CODE: true,
      KBD: true,
      SAMP: true,
      STRONG: true,
      SMALL: true,
      A: true,
      HR: true,
      TABLE: true,
      THEAD: true,
      TFOOT: true,
      TR: true,
      TH: true,
      TD: true,
      BR: true,
      IMG: true,
      FIGURE: true,
      FIGCAPTION: true,
      PICTURE: true,
      SOURCE: true,
      TIME: true,
      ARTICLE: true,
      ASIDE: true,
      NAV: true,
      FOOTER: true
    },
    attribute_list: {
      alt: true,
      rel: true,
      href: true,
      src: true,
      srcset: true,
      media: true,
      datetime: true,
      'class': true
    },
    link_node_list: {
      A: true,
      IMG: true,
      FIGURE: true,
      PICTURE: true
    },
    link_list: {
      href: true,
      src: true,
      srcset: true
    }
  },
    emptylist = {
      BR: true,
      HR: true
    },
    blacklist = {
      SCRIPT: true,
      STYLE: true,
      NOSCRIPT: true,
      FORM: true,
      FIELDSET: true,
      INPUT: true,
      SELECT: true,
      TEXTAREA: true,
      BUTTON: true,
      IFRAME: true,
      SVG: true
    };

  function keepOnlyChildren(current_node) {
    var fragment = document.createDocumentFragment();

    while (current_node.firstChild) {
      fragment.appendChild(current_node.firstChild);
    }
    current_node.parentNode.replaceChild(
      fragment,
      current_node
    );
  }

  function cleanup(html) {
    var html_doc = (new DOMParser()).parseFromString(html,
                                                     'text/html'),
      iterator,
      current_node,
      attribute,
      attribute_list,
      len,
      link_len,
      already_dropped,
      finished = false;

    iterator = document.createNodeIterator(
      html_doc.body,
      NodeFilter.SHOW_ELEMENT,
      function () {
        return NodeFilter.FILTER_ACCEPT;
      }
    );

    while (!finished) {
      current_node = iterator.nextNode();
      finished = (current_node === null);
      if (!finished) {

        if (blacklist[current_node.nodeName]) {
          // Drop element
          current_node.parentNode.removeChild(current_node);

        } else if (!whitelist.node_list[current_node.nodeName]) {
          // Only keep children
          keepOnlyChildren(current_node);

        } else {
          // Cleanup attributes
          attribute_list = current_node.attributes;
          len = attribute_list.length;
          while (len !== 0) {
            len = len - 1;
            attribute = attribute_list[len].name;
            if (!whitelist.attribute_list[attribute]) {
              current_node.removeAttribute(attribute);
            }
          }

          // Cleanup links
          attribute_list = current_node.attributes;
          len = attribute_list.length;
          link_len = 0;
          already_dropped = false;
          while (len !== 0) {
            len = len - 1;
            attribute = attribute_list[len].name;
            if (whitelist.link_list[attribute]) {
              if (startsWithOneOf(current_node.getAttribute(attribute),
                                  ['http://', 'https://', '//', 'data:'])) {
                link_len += 1;
              } else {
                keepOnlyChildren(current_node);
                already_dropped = true;
                break;
              }
            }
          }

          // Lazy img load
          if (current_node.nodeName === 'IMG') {
            current_node.setAttribute('loading', 'lazy');
          }

          // Drop link node without url
          if (whitelist.link_node_list[current_node.nodeName]) {
            if ((link_len === 0) && (!already_dropped)) {
              already_dropped = true;
              keepOnlyChildren(current_node);
            }
          }

          // Drop element if no text or link
          if ((link_len === 0) && (!already_dropped) &&
              (!current_node.textContent) &&
              (!emptylist[current_node.nodeName])) {
            current_node.parentNode.removeChild(current_node);
          }
        }

      }
    }

    return html_doc.querySelector('body') || domsugar(null);
  }

  rJS(window)

    .declareMethod('render', function (options) {
      domsugar(this.element, Array.from(cleanup(options.value || '').childNodes));
    });

}(window, rJS, domsugar, document, DOMParser, NodeFilter));