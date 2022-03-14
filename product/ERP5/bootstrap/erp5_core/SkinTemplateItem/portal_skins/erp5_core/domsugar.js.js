// DOM sugar
// ==================================================================
// Modified version of "Sugared DOM" https://gist.github.com/jacobrask/3524145
//
// Usage
// ------------------------------------------------------------------
// var make = domsugar(document);
//
// make( 'p.foo#bar', { hidden: true }, [ make( 'span' ) ] );
// => <p class="foo" id="bar" hidden><span></span></p>
//
// make( '.bar', [ '<b></b>' ] );
// make( '.bar', { text: '<b></b>' } );
// => <div class="bar">&lt;b&gt;&lt/b&gt;</div>
//
// make( 'div', [ make( 'b', [ 'Foo', make( 'i' ) ] ) ] );
// make( 'div', { html: '<b>Foo<i></i></b>' } );
// => <div><b>Foo<i></i></b></div>
//
// var myDiv = document.createElement( 'div' );
// make( myDiv, { id: 'foo' } );
// => <div id="foo"></div>

(function (window, document) {
  'use strict';

  // Some properties need to be direct, other are common ones and setting
  // them directly is faster than setAttribute.
  var direct_property_dict = {
    'class': 'className',
    className: 'className',
    defaultValue: 'defaultValue',
    'for': 'htmlFor',
    html: 'innerHTML',
    id: 'id',
    name: 'name',
    src: 'src',
    text: 'textContent',
    title: 'title',
    value: 'value'
  },
    // Object lookup is faster than indexOf.
    boolean_property_dict = {
      checked: 1,
      defaultChecked: 1,
      disabled: 1,
      hidden: 1,
      multiple: 1,
      selected: 1,
      required: 1,
      readonly: 1,
      autofocus: 1,
      spellcheck: 1
    };
    // splitter = /(#|\.)/;

  function setProperty(el, key, value) {
    var prop = direct_property_dict[key];
    if (prop) {
      el[prop] = (value === null ? '' : String(value));
    } else if (boolean_property_dict[key]) {
      el[key] = !!value;
    } else if (value === null) {
      el.removeAttribute(key);
    } else {
      el.setAttribute(key, String(value));
    }
  }

  function appendChildren(el, children) {
    var i, l, node;
    for (i = 0, l = children.length; i < l; i += 1) {
      node = children[i];
      if (node) {
        if (node instanceof Array) {
          appendChildren(el, node);
        } else {
          if (typeof node === 'string') {
            node = document.createTextNode(node);
          }
          el.appendChild(node);
        }
      }
    }
  }

  window.domsugar = function (tag, props, children) {
    if (props instanceof Array) {
      children = props;
      props = null;
    }
    var el,
      prop;
/*
    if ( !tag ) { tag = 'div'; createDocumentFragment }

        var parts, name, el,
            i, j, l, node, prop;
        if ( typeof tag === 'string' && splitter.test( tag ) ) {
            parts = tag.split( splitter );
            tag = parts[0];
            if ( !props ) { props = {}; }
            for ( i = 1, j = 2, l = parts.length; j < l; i += 2, j += 2 ) {
                name = parts[j];
                if ( parts[i] === '#' ) {
                    props.id = name;
                } else {
                    props.className = props.className ?
                        props.className + ' ' + name : name;
                }
            }
        }
        el = typeof tag === 'string' ? doc.createElement( tag ) : tag;
*/
    if (typeof tag === 'string') {
      el = document.createElement(tag);
    } else if (tag) {
      el = tag;
      // Empty the element
      while (el.firstChild) {
        el.firstChild.remove();
      }
    } else {
      el = document.createDocumentFragment();
    }
    if (props) {
      for (prop in props) {
        if (props.hasOwnProperty(prop) && (props[prop] !== undefined)) {
          setProperty(el, prop, props[prop]);
        }
      }
    }
    if ((el.tagName === 'A') &&
        (props.target === '_blank')) {
      // Fix security hole with `noopener`
      if (!el.relList.contains('noopener')) {
        el.relList.add('noopener');
      }
      if (!el.relList.contains('noreferrer')) {
        el.relList.add('noreferrer');
      }
    }
    if (children) {
      appendChildren(el, children);
    }
    return el;
  };

  /*global document, window*/
}(window, document));
