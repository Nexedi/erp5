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
      node;

    if (tree.hasOwnProperty('sub')) {
      for (key in tree.sub) {
        if (tree.sub.hasOwnProperty(key)) {
          subid = id + key;
          node = {id: subid, title: key};
          if (tree.sub[key].hasOwnProperty('value')) {
            node.title += ' (' + tree.sub[key].value + ')'
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
        item_path_list = parameter_dict.item_path_list;
      this.action_url = parameter_dict.action_url;
      var node_list = buildTreeHTML('tree', convertPathListToTree(item_path_list));
      this.element.innerHTML = buildTreeHTML('tree', convertPathListToTree(item_path_list));
      console.log(node_list);
    })

    .onEvent('change', function (evt) {
      if ((evt.target.type === 'checkbox') && (!evt.target.id)) {
        // XXX Update the checkbox state of children (and parents too)
        // querySelectorAll and parent ancestors
        // var parentSelected = this.element.querySelectorAll('input[type=checkbox][name=""]:checked')
        var val = this.element.querySelectorAll('input[type=checkbox][name="item_path_list:list"]:checked');
        // Spread the result value so that we can use map on it
        var labelValues = [...val].map(function(x){
          return x.nextSibling.data;
        });
        console.log('Update the checkbox state of children (and parents too)');
        console.log(labelValues);
      }
    }, false, false)

    .declareMethod('getContent', function (options) {
      var input_list = this.element.querySelectorAll('input[type=checkbox][name="item_path_list:list"]:checked');
      console.log(input_list);
      return jIO.util.ajax({
        type: 'POST',
        url: this.action_url,
        data: {'checkNeeded': 'True',
              'item_path_list': input_list}
      });
    })

}(rJS, jIO, Handlebars, RSVP, window));