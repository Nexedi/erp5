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
               1: {value: 'Bar'},
               6: {value: 'Foo'}
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
      }
    }
    return tree;
  }

  function buildTreeHTML(id, tree) {
    var html = '',
      key,
      node_list = [],
      subid,
      state,
      node;

    if (tree.hasOwnProperty('sub')) {
      for (key in tree.sub) {
        if (tree.sub.hasOwnProperty(key)) {
          subid = id + key;
          state = tree.sub[key].value;
          node = {id: subid, title: key};
          if (tree.sub[key].hasOwnProperty('value')) {
            node.state = tree.sub[key].value;
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
      var parameter_dict = JSON.parse(options.value),
        item_path_list = parameter_dict.item_path_list,
        html_tree = buildTreeHTML('tree', convertPathListToTree(item_path_list));
      this.action_url = parameter_dict.action_url;
      this.element.innerHTML = html_tree;
      console.log(html_tree);
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
        if (evt.target.getAttribute('name') === 'child_path') {
          // Get the parent element with with path
          var parent = evt.target.parentElement.parentElement.parentElement,
            state = parent.querySelector('input[type=checkbox][name$="_path"]').nextElementSibling.getAttribute('state');

          // Only update the children and parents together if parent element
          // has no state value
          if (!state) {
            var childrenChecked = parent.querySelectorAll('input[type=checkbox][name="child_path"]:checked'),
              children = parent.querySelectorAll('input[type=checkbox][name="child_path"]'),
              parentCheckBox = parent.querySelector('input[type=checkbox][name$="parent_path"]');
            if (children.length === childrenChecked.length) {
              parentCheckBox.checked = evt.target.checked;
            }
          }

        }
        if (evt.target.getAttribute('name') === 'parent_path') {
          // Check for the state of the target
          // If there is no state, then check if all the children are flattened
          // or not. If there is another tree in the child nodes, do nothing.
          // Else update the checked status of all the child nodes similar to
          // that of the parent
          if (!evt.target.nextSibling.getAttribute('state')) {
            var nodeChildPath = evt.target.nextElementSibling.nextElementSibling.querySelectorAll('input[type=checkbox][name="child_path"]'),
              nodeParentPath = evt.target.nextElementSibling.nextElementSibling.querySelectorAll('input[type=checkbox][name="parent_path"]'),
              i,
              element;
            // If there is no nodeParentPath and some childParentPath, update
            // the checked status of the childParentPath
            if ((!nodeParentPath.length) && (nodeChildPath.length)) {
              for (i = 0; element = nodeChildPath[i]; i++) {
                element.checked = evt.target.checked;
              }
            }
          }
        }
        console.log('Update the checkbox state of children (and parents too)');
      }
    }, false, false)

    .declareMethod('getContent', function (options) {
      var input_list = options.input_list;
      console.log(input_list);
      return jIO.util.ajax({
        type: 'POST',
        url: this.action_url,
        data: {'checkNeeded': 'True',
              'item_path_list': input_list}
      });
    });

}(rJS, jIO, Handlebars, RSVP, window));