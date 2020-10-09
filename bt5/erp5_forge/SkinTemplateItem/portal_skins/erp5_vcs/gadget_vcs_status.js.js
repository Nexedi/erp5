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
      type: true,
      class: true,
      id: true,
      for: true
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
      child_list,
      len,
      link_len,
      already_dropped,
      finished = false,
      id = -1;

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
          child_list = []

          // Open/hide element
          if (current_node.firstChild) {
            id += 1;
            child_list.push(
              domsugar('input', {type: 'checkbox', id: 'showhide' + id, class: 'showhide'}),
              domsugar('label', {for: 'showhide' + id, class: 'showhide show', text: '-'}),
              domsugar('label', {for: 'showhide' + id, class: 'showhide hide', text: '+'}),
            );
          } else {
            child_list.push(
              domsugar('label', {class: 'showhide', text: ' '}),
            );
          }

          // Select element
          child_list.push(domsugar('label', [
            domsugar('input', {type: 'checkbox', class: 'vcs_to_commit'}),
            current_node.getAttribute('text')
          ]));

          // Child items
          if (current_node.firstChild) {
            ul_node = domsugar('ul');
            while (current_node.firstChild) {
              ul_node.appendChild(current_node.firstChild);
            }
            child_list.push(ul_node);
          }

          current_node.parentNode.replaceChild(
            domsugar('li', child_list),
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
              domsugar('div', {text: 'Checking for changes.'})
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

    })

    .onEvent("change", function (evt) {
      var gadget = this,
        tag_name = evt.target.tagName,
        i,
        element_list,
        checkbox,
        parent_checkbox,
        parent_ul,
        state_dict,
        is_checked,
        is_indeterminate;

      // Only handle vcs_to_commit checkbox
      if ((tag_name !== 'INPUT') || (evt.target.className !== 'vcs_to_commit')) {
        return;
      }

      // https://css-tricks.com/indeterminate-checkboxes/

      // Check/uncheck all children checkboxes
      element_list = evt.target.parentElement
                               .parentElement.querySelectorAll('input.vcs_to_commit');
      for (i = 0; i < element_list.length; i += 1) {
        element_list[i].checked = evt.target.checked;
        element_list[i].indeterminate = false;
      }

      // Check/uncheck/undefine all parent checkboxes
      checkbox = evt.target;
      while (checkbox !== null) {
        parent_checkbox = checkbox.closest('ul')
                                  .parentNode
                                  .querySelector('input.vcs_to_commit');

        if (parent_checkbox === checkbox) {
          // Top checkbox
          checkbox = null;
        } else {
          // check the state of all child chexbox
          element_list = parent_checkbox.closest('li').querySelector('ul').children;
          is_checked = true;
          is_indeterminate = false;
          for (i = 0; i < element_list.length; i += 1) {
            is_checked = is_checked && element_list[i].querySelector('input.vcs_to_commit').checked;
            is_indeterminate = is_indeterminate || element_list[i].querySelector('input.vcs_to_commit').checked;
          }
          parent_checkbox.checked = is_checked;
          parent_checkbox.indeterminate = (!is_checked) && is_indeterminate;

          checkbox = parent_checkbox;
        }
    }
      
    }, false, false)

    .onEvent("click", function (evt) {
      // Only handle click on BUTTON and IMG element
      var gadget = this,
        tag_name = evt.target.tagName,
        state_dict;

      if (tag_name !== 'BUTTON') {
        return;
      }

      // Disable any button. It must be managed by this gadget
      evt.preventDefault();

      throw new Error('Unhandled button: ' + evt.target.textContent);
      // return;
    }, false, false)

    //////////////////////////////////////////////////
    // Used when submitting the form
    //////////////////////////////////////////////////
    .declareMethod('getContent', function () {
      throw new Error('getContent not implemented');
    }, {mutex: 'changestate'})

    .declareMethod('checkValidity', function () {
      throw new Error('checkValidity not implemented');
    }, {mutex: 'changestate'})

}(rJS, jIO, domsugar, RSVP, window));