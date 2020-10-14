/*global window, rJS, RSVP, domsugar, jIO, console, document, NodeFilter,
         FormData */
/*jslint nomen: true, maxlen:80, indent:2*/
(function (window, rJS, RSVP, domsugar, jIO, console, document, NodeFilter) {
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
      for: true,
      name: true,
      value: true
    }
  },
    DISPLAY_TREE = 'display_tree',
    DISPLAY_DIFF = 'display_diff',
    DISPLAY_CHANGELOG = 'display_changelog';

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

  function renderTreeXml(gadget, tree_xml_element) {
    var iterator,
      current_node,
      next_node,
      parent_node,
      value,
      ul_node,
      attribute,
      attribute_list,
      child_list,
      len,
      finished = false,
      id = -1,
      name,
      state_value = JSON.parse(gadget.state.value);

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
          child_list = [];

          // Open/hide element
          if (current_node.firstChild) {
            id += 1;
            child_list.push(
              domsugar('input', {type: 'checkbox', id: 'showhide' + id,
                                 class: 'showhide'}),
              domsugar('label', {for: 'showhide' + id, class: 'showhide show',
                                 text: '-'}),
              domsugar('label', {for: 'showhide' + id, class: 'showhide hide',
                                 text: '+'})
            );
          } else {
            child_list.push(
              domsugar('label', {class: 'showhide', text: ' '})
            );
          }

          // Select element
          parent_node = current_node.closest('ul');
          if (parent_node !== null) {
            parent_node = parent_node.parentNode;
          }
          if (parent_node !== null) {
            parent_node = parent_node.querySelector('input.vcs_to_commit');
          }

          value = current_node.getAttribute('text');

          if ((parent_node !== null) && (parent_node !== current_node)) {
            if (parent_node.value) {
              value = parent_node.value + '/' + value;
            }
          } else {
            value = '';
          }

          name = {
            'green': 'added',
            'orange': 'modified',
            'red': 'deleted'
          }[current_node.getAttribute('aCol')];
          child_list.push(domsugar('label', [
            domsugar('input', {
              type: 'checkbox',
              class: 'vcs_to_commit',
              value: value,
              name: name,
              checked: ((state_value[name] === undefined) ||
                        (state_value[name].indexOf(value) === -1)) ? '' :
                                                                     'checked'
            }),
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

  function renderGadgetHeader(gadget, loading) {
    var element_list = [
      domsugar('p', [
        'Repository: ',
        domsugar('a', {
          text: gadget.state.remote_url,
          href: gadget.state.remote_url
        }),
        ' (' + gadget.state.remote_comment + ')'
      ])
    ],
      tree_icon = 'ui-icon-check-square',
      diff_icon = 'ui-icon-search-plus',
      changelog_icon = 'ui-icon-git';

    if (loading) {
      if (gadget.state.display_step === DISPLAY_TREE) {
        tree_icon = 'ui-icon-spinner';
      } else if (gadget.state.display_step === DISPLAY_DIFF) {
        diff_icon = 'ui-icon-spinner';
      } else if (gadget.state.display_step === DISPLAY_CHANGELOG) {
        changelog_icon = 'ui-icon-spinner';
      } else {
        throw new Error("Can't render header state " +
                        gadget.state.display_step);
      }
    }

    element_list.push(
      domsugar('button', {
        type: 'button',
        text: 'Tree',
        disabled: (gadget.state.display_step === DISPLAY_TREE),
        class: 'display-tree-btn ui-btn-icon-left ' + tree_icon
      }),
      domsugar('button', {
        type: 'button',
        text: 'Diff',
        disabled: (gadget.state.display_step === DISPLAY_DIFF),
        class: 'diff-tree-btn ui-btn-icon-left ' + diff_icon
      }),
      domsugar('button', {
        type: 'button',
        text: 'Changelog',
        disabled: (gadget.state.display_step === DISPLAY_CHANGELOG),
        class: 'changelog-btn ui-btn-icon-left ' + changelog_icon
      })
    );

    if ((!loading) && (gadget.state.display_step === DISPLAY_TREE)) {
      element_list.push(
        domsugar('button', {
          type: 'button',
          text: 'Expand',
          class: 'expand-tree-btn ui-btn-icon-left ui-icon-arrows-v'
        })
      );
    }

    domsugar(gadget.element.querySelector('div.vcsheader'), element_list);
  }

  function updateFullTreeCheckbox(checkbox) {
    var i,
      element_list,
      parent_checkbox,
      is_checked,
      is_indeterminate;
    // https://css-tricks.com/indeterminate-checkboxes/

    // Check/uncheck all children checkboxes
    element_list = checkbox.parentElement
                           .parentElement
                           .querySelectorAll('input.vcs_to_commit');
    for (i = 0; i < element_list.length; i += 1) {
      element_list[i].checked = checkbox.checked;
      element_list[i].indeterminate = false;
    }

    // Check/uncheck/undefine all parent checkboxes
    while (checkbox !== null) {
      parent_checkbox = checkbox.closest('ul')
                                .parentNode
                                .querySelector('input.vcs_to_commit');

      if (parent_checkbox === checkbox) {
        // Top checkbox
        checkbox = null;
      } else {
        // check the state of all child chexbox
        element_list = parent_checkbox.closest('li')
                                      .querySelector('ul')
                                      .children;
        is_checked = true;
        is_indeterminate = false;
        for (i = 0; i < element_list.length; i += 1) {
          is_checked = is_checked &&
                       element_list[i].querySelector('input.vcs_to_commit')
                                      .checked;
          is_indeterminate =
            is_indeterminate ||
            element_list[i].querySelector('input.vcs_to_commit')
                           .checked ||
            element_list[i].querySelector('input.vcs_to_commit')
                           .indeterminate;
        }
        parent_checkbox.checked = is_checked;
        parent_checkbox.indeterminate = (!is_checked) && is_indeterminate;

        checkbox = parent_checkbox;
      }
    }
  }


  function renderTreeView(gadget, extract) {
    return new RSVP.Queue()
      .push(function () {
        renderGadgetHeader(gadget, true);

        var form_data = new FormData();
        form_data.append('show_unmodified:int', 0);
        // form_data.append('bt_id', 'erp5');
        form_data.append('do_extract:int', extract ? 1 : 0);

        return jIO.util.ajax({
          "type": "POST",
          "url": gadget.state.get_tree_url,
          "xhrFields": {
            withCredentials: true
          },
          "dataType": "document",
          "data": form_data
        });
      })
      .push(function (evt) {
        renderGadgetHeader(gadget, false);

        domsugar(gadget.element.querySelector('div.vcsbody'), [
          renderTreeXml(gadget, evt.target.response.querySelector('tree'))
        ]);

        // Update the tree parent
        var element_list = gadget.element
                                 .querySelectorAll('input.vcs_to_commit'),
          i;
        for (i = 0; i < element_list.length; i += 1) {
          if (element_list[i].checked) {
            updateFullTreeCheckbox(element_list[i]);
          }
        }

      });
  }

  function getContentFromTreeView(gadget) {
    var result = JSON.parse(gadget.state.value),
      checkbox_list = gadget.element.querySelectorAll('input.vcs_to_commit'),
      i,
      name;
    result.added = [];
    result.modified = [];
    result.deleted = [];
    for (i = 0; i < checkbox_list.length; i += 1) {
      name = checkbox_list[i].name;
      if (name && checkbox_list[i].checked) {
        result[name].push(checkbox_list[i].value);
      }
    }
    gadget.state.value = JSON.stringify(result);
  }

  function expandTreeView(gadget) {
    var element_list = gadget.element.querySelectorAll('input.showhide'),
      // Do not crash if no checkbox is displayed
      is_checked = (element_list.length !== 0) && (!element_list[0].checked),
      i;
    for (i = 0; i < element_list.length; i += 1) {
      element_list[0].checked = is_checked;
    }
  }

  function declareAndRenderDiff(gadget, path, diff) {
    return gadget.declareGadget('gadget_erp5_side_by_side_diff.html')
      .push(function (diff_gadget) {
        return RSVP.all([
          diff_gadget.element,
          path,
          diff_gadget.render({value: diff})
        ]);
      });
  }

  function renderDiffView(gadget) {
    var result = JSON.parse(gadget.state.value),
      ajax_result,
      diff_count = result.modified.length;
    return new RSVP.Queue()
      .push(function () {
        renderGadgetHeader(gadget, true);

        var form_data = new FormData(),
          key_list = ['modified', 'added', 'deleted'],
          key,
          i,
          j;
        for (i = 0; i < key_list.length; i += 1) {
          key = key_list[i];
          for (j = 0; j < result[key].length; j += 1) {
            form_data.append(key + ':list', result[key][j]);
          }
        }
        return jIO.util.ajax({
          "type": "POST",
          "url": gadget.state.diff_url,
          "xhrFields": {
            withCredentials: true
          },
          "dataType": "json",
          "data": form_data
        });
      })
      .push(function (evt) {
        ajax_result = evt.target.response;
        var promise_list = [],
          i;
        for (i = 0; i < diff_count; i += 1) {
          promise_list.push(
            declareAndRenderDiff(
              gadget,
              ajax_result.modified_list[i].path,
              ajax_result.modified_list[i].diff
            )
          );
        }
        return RSVP.all(promise_list);
      })
      .push(function (result_list) {
        var i,
          element_list = [];
        for (i = 0; i < result_list.length; i += 1) {
          element_list.push(
            domsugar('label', [
              domsugar('input', {
                type: 'checkbox',
                class: 'vcs_to_commit',
                value: result_list[i][1],
                name: 'modified',
                checked: 'checked'
              }),
              result_list[i][1]
            ]),
            result_list[i][0]
          );
        }

        for (i = 0; i < ajax_result.added_list.length; i += 1) {
          element_list.push(
            domsugar('label', [
              domsugar('input', {
                type: 'checkbox',
                class: 'vcs_to_commit',
                value: ajax_result.added_list[i].path,
                name: 'added',
                checked: 'checked'
              }),
              ajax_result.added_list[i].path
            ])
          );
        }

        for (i = 0; i < ajax_result.deleted_list.length; i += 1) {
          element_list.push(
            domsugar('label', [
              domsugar('input', {
                type: 'checkbox',
                class: 'vcs_to_commit',
                value: ajax_result.deleted_list[i].path,
                name: 'deleted',
                checked: 'checked'
              }),
              ajax_result.deleted_list[i].path
            ])
          );
        }

        renderGadgetHeader(gadget, false);
        domsugar(gadget.element.querySelector('div.vcsbody'), element_list);
      });
  }

  function renderChangelogView(gadget) {
    var result = JSON.parse(gadget.state.value);
    renderGadgetHeader(gadget, false);
    domsugar(gadget.element.querySelector('div.vcsbody'), [
      domsugar('textarea', {value: result.changelog}),
      domsugar('h3', {text: 'Added Files'}),
      domsugar('pre', {text: result.added.join('\n')}),
      domsugar('h3', {text: 'Modified Files'}),
      domsugar('pre', {text: result.modified.join('\n')}),
      domsugar('h3', {text: 'Deleted Files'}),
      domsugar('pre', {text: result.deleted.join('\n')})
    ]);
  }

  function getContentFromChangelogView(gadget) {
    var result = JSON.parse(gadget.state.value);
    result.changelog = gadget.element.querySelector('textarea').value;
    gadget.state.value = JSON.stringify(result);
  }

  rJS(window)

    .declareMethod('render', function (options) {
      return this.changeState({
        display_step: DISPLAY_TREE,
        // Only build the bt5 during the first query
        extract: 1,
        diff_url: options.diff_url,
        get_tree_url: options.get_tree_url,
        remote_comment: options.remote_comment,
        remote_url: options.remote_url,
        // key: options.key,
        // value: options.value || "",
        value: JSON.stringify({added: [], modified: [], deleted: [],
                               changelog: ''}),
        editable: (options.editable === undefined) ? true : options.editable
      });
    })

    .onStateChange(function (modification_dict) {
      var gadget = this;

      if (gadget.state.display_step === DISPLAY_TREE) {
        console.log(modification_dict);
        if (modification_dict.hasOwnProperty('display_step')) {
          return renderTreeView(gadget,
                                modification_dict.hasOwnProperty('extract'));
        }
        if (modification_dict.hasOwnProperty('expand_tree')) {
          return expandTreeView(gadget);
        }
      }

      if (modification_dict.display_step === DISPLAY_DIFF) {
        return renderDiffView(gadget);
      }

      if (modification_dict.display_step === DISPLAY_CHANGELOG) {
        return renderChangelogView(gadget);
      }

      throw new Error('Unhandled display step: ' + gadget.state.display_step);

    })

    .onEvent("change", function (evt) {
      var gadget = this,
        tag_name = evt.target.tagName;

      // Only handle vcs_to_commit checkbox
      if ((tag_name !== 'INPUT') ||
          (evt.target.className !== 'vcs_to_commit')) {
        return;
      }

      if (gadget.state.display_step !== DISPLAY_TREE) {
        return;
      }

      updateFullTreeCheckbox(evt.target);
    }, false, false)

    .onEvent("click", function (evt) {
      // Only handle click on BUTTON and IMG element
      var gadget = this,
        tag_name = evt.target.tagName,
        queue;

      if (tag_name !== 'BUTTON') {
        return;
      }

      // Disable any button. It must be managed by this gadget
      evt.preventDefault();

      // Always get content to ensure the possible displayed form
      // is checked and content propagated to the gadget state value
      queue = gadget.getContent();

      if (evt.target.className.indexOf("expand-tree-btn") !== -1) {
        return queue
          .push(function () {
            return gadget.changeState({
              display_step: DISPLAY_TREE,
              expand_tree: new Date()
            });
          });
      }

      if (evt.target.className.indexOf("display-tree-btn") !== -1) {
        return queue
          .push(function () {
            return gadget.changeState({
              display_step: DISPLAY_TREE
            });
          });
      }

      if (evt.target.className.indexOf("diff-tree-btn") !== -1) {
        return queue
          .push(function () {
            return gadget.changeState({
              display_step: DISPLAY_DIFF
            });
          });
      }

      if (evt.target.className.indexOf("changelog-btn") !== -1) {
        return queue
          .push(function () {
            return gadget.changeState({
              display_step: DISPLAY_CHANGELOG
            });
          });
      }

      throw new Error('Unhandled button: ' + evt.target.textContent);
    }, false, false)

    //////////////////////////////////////////////////
    // Used when submitting the form
    //////////////////////////////////////////////////
    .declareMethod('getContent', function () {
      var gadget = this,
        display_step = gadget.state.display_step,
        queue;

      if (gadget.state.display_step === DISPLAY_TREE) {
        queue = new RSVP.Queue(getContentFromTreeView(gadget));
      } else if (gadget.state.display_step === DISPLAY_DIFF) {
        queue = new RSVP.Queue(getContentFromTreeView(gadget));
      } else if (gadget.state.display_step === DISPLAY_CHANGELOG) {
        queue = new RSVP.Queue(getContentFromChangelogView(gadget));
      } else {
        throw new Error('getContent form not handled: ' + display_step);
      }

      return queue
        .push(function () {
          var result = {};
          if (gadget.state.editable) {
            result[gadget.state.key] = gadget.state.value;
          }
          return result;
        });
    }, {mutex: 'changestate'})

    .declareMethod('checkValidity', function () {
      throw new Error('checkValidity not implemented');
    }, {mutex: 'changestate'});

}(window, rJS, RSVP, domsugar, jIO, console, document, NodeFilter));