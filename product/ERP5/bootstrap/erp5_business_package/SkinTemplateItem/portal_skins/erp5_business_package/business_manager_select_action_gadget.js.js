/*global window, rJS, RSVP, Handlebars, jIO, location, console */
/*jslint nomen: true, maxlen:80, indent:2*/
(function (rJS, jIO, Handlebars, RSVP, window) {
  "use strict";
  var gk = rJS(window),
    data_source = document.getElementById('subtree').innerHTML,
    get_data_template = Handlebars.compile(data_source);

  function convertPathListToTree(item_path_list) {
    /* From
       [
         ['portal_ids/6', 'Foo']
         ['portal_ids/1', 'Bar']
       ]
       To
       {
         sub: {
           portal_ids: {
             sub: {
               1: {value: 'Bar', path: 'portal_ids/1},
               6: {value: 'Foo', path: 'portal_ids/6}
             }
           }
         }
       }
    */
    var tree = {},
      i,
      splitted_key_list,
      j,
      key,
      subtree;

    for (i = item_path_list.length - 1; i >= 0; i -= 1) {
      splitted_key_list = item_path_list[i][0].split('/');
      subtree = tree;
      for (j = 0; j < splitted_key_list.length; j += 1) {
        key = splitted_key_list[j];
        if (!subtree.hasOwnProperty('sub')) {
          subtree.sub = {};
        }
        if (!subtree.sub.hasOwnProperty(key)) {
          subtree.sub[key] = {};
        }
        subtree = subtree.sub[key];
      }
      if (splitted_key_list.length) {
        subtree.value = item_path_list[i][1];
        subtree.path = item_path_list[i][0];
      }
    }
    return tree;
  }

  function buildTreeHTML(id, tree, checked_list) {
    var html = '',
      key,
      node_list = [],
      subid,
      node;

    // checked_list should be an empty array if it is undefined
    if (!checked_list) {
      checked_list = [];
    }

    if (tree.hasOwnProperty('sub')) {
      for (key in tree.sub) {
        if (tree.sub.hasOwnProperty(key)) {
          subid = id + key;
          node = {id: subid, title: key};
          if (tree.sub[key].hasOwnProperty('value')) {
            // class is a reserved keyword
            node['class'] = tree.sub[key].value;
            node['data-path'] = tree.sub[key].path;
            // If the path is in checked_list, put checked to True so that we
            // can update it in HTML directly
            if (key in checked_list) {
              node['data-checked'] = true;
            }
          }
          else {
            node['class'] = 'Unchanged';
          }
          if (tree.sub[key].hasOwnProperty('sub')) {
            node.tree_html = buildTreeHTML(subid, tree.sub[key]);
          }
          node_list.push(node);
        }
      }
      html = get_data_template({node_list: node_list});
    }
    return html;
  }

  rJS(window)

    .declareMethod('render', function (options) {
      var item_path_list = JSON.parse(options.built_path_list),
        checked_list = JSON.parse(options.value).map(
          function(element) {return element[0];}
          ),
        html_tree = buildTreeHTML('tree', convertPathListToTree(item_path_list,
                                  checked_list)),
        state_dict = {
          key: options.key,
          value: options.value,
          built_path_list: options.built_path_list
        };

      this.item_path_list = item_path_list;
      this.element.innerHTML = html_tree;
      return this.changeState(state_dict);
    })

    .onEvent('change', function (evt) {
      if ((evt.target.type === 'checkbox') && (evt.target.name) && (evt.target.id)) {
        // XXX Update the checkbox state of children (and parents too)
        // Rules:
        // 1 . State of parent shouldn't be dependent on the state of children
        //     and vice-versa if both of them some value(i.e, if there has been
        //     any change in the path).
        // 2 . If parent has no value:
        //      - All children checked -> Parent checked
        //      - Parent checked -> All children checked
        if (evt.target.name === 'child_path') {
          // Get the parent element with with path
          var parent = evt.target.parentElement.parentElement.parentElement,
            state = parent.querySelector(
              'input[type=checkbox][name$="_path"]').nextElementSibling.className;

          // Only update the children and parents together if parent element
          // has no state value
          if (state === 'Unchanged') {
            var childrenChecked = parent.querySelectorAll(
              'input[type=checkbox][name="child_path"]:checked'),
              children = parent.querySelectorAll(
                'input[type=checkbox][name="child_path"]'),
              parentCheckBox = parent.querySelector(
                'input[type=checkbox][name$="parent_path"]');
            if (children.length === childrenChecked.length) {
              parentCheckBox.checked = evt.target.checked;
            }
          }
        }

        if (evt.target.name === 'parent_path') {
          // Check for the state of the target
          // If there is no state, then check if all the children are flattened
          // or not. If there is another tree in the child nodes, do nothing.
          // Else update the checked status of all the child nodes similar to
          // that of the parent
          if (evt.target.nextSibling.className === 'Unchanged') {
            var nodeChildPath = evt.target.nextElementSibling.nextElementSibling.querySelectorAll('input[type=checkbox][name="child_path"]'),
              nodeParentPath = evt.target.nextElementSibling.nextElementSibling.querySelectorAll('input[type=checkbox][name="parent_path"]'),
              i;
            // If there is no nodeParentPath and some childParentPath, update
            // the checked status of the childParentPath
            if ((!nodeParentPath.length) && (nodeChildPath.length)) {
              for (i = 0; i < nodeChildPath.length; i++) {
                nodeChildPath[i].checked = evt.target.checked;
              }
            }
          }
        }
        console.log('Update the checkbox state of children (and parents too)');
      }
    }, false, false)

    .declareMethod('getContent', function () {
      var i,
        path_list = [],
        result = {};

      // Get all the checked checkbox from both child_path and parent_path
      var checkedInputList = this.element.querySelectorAll(
        'input[type=checkbox][name$="_path"]:checked'
        ),
        nextLabelElement;

      // Filter all paths except for those 'Unchanged'
      for (i = 0; i < checkedInputList.length; ++i) {
        nextLabelElement = checkedInputList[i].nextElementSibling;
        var path_state = [];
        if (nextLabelElement.className !== "Unchanged") {
          path_state.push(nextLabelElement.dataset.path);
          path_state.push(nextLabelElement.className);
          path_list.push(path_state);
        }
      }
      this.state.value = JSON.stringify(path_list);
      result[this.state.key] = this.state.value;

      return result
    });

}(rJS, jIO, Handlebars, RSVP, window));