/*global window, rJS, RSVP, domsugar, jIO, console */
/*jslint nomen: true, maxlen:80, indent:2*/
(function (rJS, jIO, domsugar, RSVP, window) {
  "use strict";

  var whitelist = {
    node_list: {
      P: true,
      UL: true,
      LI: true,
      INPUT: true,
      LABEL: true
    },
    attribute_list: {
      type: true
    }
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

  function renderTreeXml(tree_xml_element) {
    var iterator,
      current_node,
      next_node,
      ul_node,
      attribute,
      attribute_list,
      len,
      link_len,
      already_dropped,
      finished = false;

    // Replace the tree element by a fragment
    next_node = domsugar('ul');
    while (tree_xml_element.firstChild) {
      next_node.appendChild(tree_xml_element.firstChild);
    }
    tree_xml_element = next_node;

    iterator = document.createNodeIterator(
      tree_xml_element,
      NodeFilter.SHOW_ELEMENT,
      function () {
        return NodeFilter.FILTER_ACCEPT;
      }
    );

    while (!finished) {
      current_node = iterator.nextNode();
      finished = (current_node === null);
      if (!finished) {

        if (current_node.nodeName === 'item') {
          next_node = domsugar('li', [
            domsugar('label', [
              domsugar('input', {type: 'checkbox'}),
              '+/-'
            ]),
            domsugar('label', [
              domsugar('input', {type: 'checkbox'}),
              current_node.getAttribute('text')
            ])
          ]);
          if (current_node.firstChild) {
            ul_node = domsugar('ul');
            next_node.appendChild(ul_node);
          }
          while (current_node.firstChild) {
            ul_node.appendChild(current_node.firstChild);
          }
          current_node.parentNode.replaceChild(
            next_node,
            current_node
          );
        } else if (!whitelist.node_list[current_node.nodeName]) {
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

        }

      }
    }

    return tree_xml_element;
  }



  rJS(window)
    .setState({
      display_step: 'display_tree'
    })

    .declareMethod('render', function (options) {
      return this.changeState({
        get_tree_url: options.get_tree_url,
        remote_comment: options.remote_comment,
        remote_url: options.remote_url
      });
    })

    .onStateChange(function () {
      var gadget = this;

      if (gadget.state.display_step === 'display_tree') {
        return new RSVP.Queue()
          .push(function () {
            domsugar(gadget.element, [
              domsugar('p', [
                'Repository: ',
                domsugar('a', {
                  text: gadget.state.remote_url,
                  href: gadget.state.remote_url
                }),
                ' (' + gadget.state.remote_comment + ')'
              ]),
              domsugar('button', {type: 'button', text: 'Show unmodified files'}),
              domsugar('button', {type: 'button', text: 'Expand'}),
              domsugar('button', {type: 'button', text: 'View Diff'}),
              domsugar('button', {type: 'button', text: 'Commit Changes'}),
              domsugar('div')
            ]);

            return jIO.util.ajax(
              {
                "type": "GET",
                "url": gadget.state.get_tree_url,
                "xhrFields": {
                  withCredentials: true
                },
                "dataType": "document"
              }
            );
          })
          .push(function (evt) {
            domsugar(gadget.element.querySelector('div'), [
              renderTreeXml(evt.target.response.querySelector('tree')),
            ]);
          });

      }

      throw new Error('Unhandled display step: ' + gadget.state.display_step);

    });

}(rJS, jIO, domsugar, RSVP, window));