/*jslint nomen: true, indent: 2 */
/*global window, rJS, domsugar, document, DOMParser, NodeFilter*/
(function (window, rJS, domsugar, document, DOMParser, NodeFilter) {
  "use strict";

/*
  function startsWithOneOf(str, prefix_list) {
    var i;
    for (i = prefix_list.length - 1; i >= 0; i -= 1) {
      if (str.substr(0, prefix_list[i].length) === prefix_list[i]) {
        return true;
      }
    }
    return false;
  }
*/

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
      CAPTION: true,
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
      FOOTER: true,
      DIV: true,
      SPAN: true,
      DETAILS: true,
      SUMMARY: true
    },
    attribute_list: {
      alt: true,
      rel: true,
      href: true,
      src: true,
      srcset: true,
      media: true,
      datetime: true,
      'class': true,
      cellspacing: true,
      cellpadding: true,
      border: true,
      colspan: true,
      rowspan: true,
      align: true,
      scope: true,
      summary: true,
      download: true
    },
    style_list: {
      background: true,
      'background-color': true,
      border: true,
      color: true,
      content: true,
      cursor: true,
      'float': true,
      'font-style': true,
      'font-weight': true,
      height: true,
      margin: true,
      'margin-left': true,
      'margin-right': true,
      'margin-top': true,
      'margin-bottom': true,
      'max-width': true,
      padding: true,
      'padding-left': true,
      'padding-right': true,
      'padding-top': true,
      'padding-bottom': true,
      'text-align': true,
      width: true,
      'display': true,
      'list-style': true,
      'text-align': true,
      'vertical-align': true,
      'border-radius': true
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
    blacklist = {
      SCRIPT: true,
      STYLE: true,
      NOSCRIPT: true,
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
      style,
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
          // Keep the style attribute, which is forbidden by CSP
          // which is a good thing, as it prevents injecting <style> element
          style = undefined;
          attribute = 'style';
          if (current_node.hasAttribute(attribute)) {
            style = current_node.getAttribute(attribute);
            // Prevent anybody to put style in the allowed attribute_list
            current_node.removeAttribute(attribute);
          }

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

          // Restore the style
          if (style !== undefined) {
            current_node.style = style;
            // And drop not allowed style attributes
            attribute_list = current_node.style;
            len = attribute_list.length;
            while (len !== 0) {
              len = len - 1;
              attribute = attribute_list[len];
              if (!whitelist.style_list[attribute]) {
                current_node.style[attribute] = null;
              }
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
              link_len += 1;
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