/*jslint nomen: true*/
/*global jIO, DOMParser */
(function (jIO, DOMParser) {
  "use strict";

  /////////////////////////////////////////////////////////////
  // OPML Parser
  /////////////////////////////////////////////////////////////
  function OPMLParser(txt) {
    this._dom_parser = new DOMParser().parseFromString(txt, 'text/xml');
  }

  OPMLParser.prototype.parseHead = function () {
    // fetch all children instead
    var channel_element = this._dom_parser.querySelector("opml > head"),
      tag_element,
      i,
      result = {};

    for (i = channel_element.childNodes.length - 1; i >= 0; i -= 1) {
      tag_element = channel_element.childNodes[i];
      result[tag_element.tagName] = tag_element.textContent;
    }
    return result;
  };

  OPMLParser.prototype.parseOutline = function (result_list, outline_element,
                                                prefix, include, id) {
    var attribute,
      i,
      child,
      result = {};

    if ((id === prefix) || (id === undefined)) {
      result_list.push({
        id: prefix,
        value: {}
      });
      if (include) {
        for (i = outline_element.attributes.length - 1; i >= 0; i -= 1) {
          attribute = outline_element.attributes[i];
          if (attribute.value) {
            result[attribute.name] = attribute.value;
          }
        }
        result_list[result_list.length - 1].doc = result;
      }
    }

    for (i = outline_element.childNodes.length - 1; i >= 0; i -= 1) {
      child = outline_element.childNodes[i];
      if (child.tagName === 'outline') {
        this.parseOutline(result_list, child, prefix + '/' + i, include, id);
      }
    }
  };

  OPMLParser.prototype.getDocumentList = function (include, id) {
    var result_list,
      item_list = this._dom_parser.querySelectorAll("body > outline"),
      i;

    if ((id === '/0') || (id === undefined)) {
      result_list = [{
        id: '/0',
        value: {}
      }];
      if (include) {
        result_list[0].doc = this.parseHead();
      }
    } else {
      result_list = [];
    }

    for (i = 0; i < item_list.length; i += 1) {
      this.parseOutline(result_list, item_list[i], '/1/' + i, include, id);
    }
    return result_list;
  };

  /////////////////////////////////////////////////////////////
  // RSS Parser
  /////////////////////////////////////////////////////////////
  function RSSParser(txt) {
    this._dom_parser = new DOMParser().parseFromString(txt, 'text/xml');
  }

  RSSParser.prototype.parseElement = function (element) {
    var tag_element,
      i,
      j,
      attribute,
      result = {};

    for (i = element.childNodes.length - 1; i >= 0; i -= 1) {
      tag_element = element.childNodes[i];
      if (tag_element.tagName !== 'item') {
        result[tag_element.tagName] = tag_element.textContent;

        for (j = tag_element.attributes.length - 1; j >= 0; j -= 1) {
          attribute = tag_element.attributes[j];
          if (attribute.value) {
            result[tag_element.tagName + '_' + attribute.name] =
              attribute.value;
          }
        }
      }
    }
    return result;
  };

  RSSParser.prototype.getDocumentList = function (include, id) {
    var result_list,
      item_list = this._dom_parser.querySelectorAll("rss > channel > item"),
      i;

    if ((id === '/0') || (id === undefined)) {
      result_list = [{
        id: '/0',
        value: {}
      }];
      if (include) {
        result_list[0].doc = this.parseElement(
          this._dom_parser.querySelector("rss > channel")
        );
      }
    } else {
      result_list = [];
    }

    for (i = 0; i < item_list.length; i += 1) {
      if ((id === '/0/' + i) || (id === undefined)) {
        result_list.push({
          id: '/0/' + i,
          value: {}
        });
        if (include) {
          result_list[result_list.length - 1].doc =
            this.parseElement(item_list[i]);
        }
      }
    }
    return result_list;
  };

  /////////////////////////////////////////////////////////////
  // Helpers
  /////////////////////////////////////////////////////////////
  var parser_dict = {
    'rss': RSSParser,
    'opml': OPMLParser
  };

  function getParser(storage) {
    return storage._sub_storage.getAttachment(storage._document_id,
                                              storage._attachment_id,
                                              {format: 'text'})
      .push(function (txt) {
        return new parser_dict[storage._parser_name](txt);
      });
  }

  /////////////////////////////////////////////////////////////
  // Storage
  /////////////////////////////////////////////////////////////
  function ParserStorage(spec) {
    this._attachment_id = spec.attachment_id;
    this._document_id = spec.document_id;
    this._parser_name = spec.parser;
    this._sub_storage = jIO.createJIO(spec.sub_storage);
  }

  ParserStorage.prototype.hasCapacity = function (capacity) {
    return (capacity === "list") || (capacity === 'include');
  };

  ParserStorage.prototype.buildQuery = function (options) {
    if (options === undefined) {
      options = {};
    }
    return getParser(this)
      .push(function (parser) {
        return parser.getDocumentList((options.include_docs || false));
      });
  };

  ParserStorage.prototype.get = function (id) {
    return getParser(this)
      .push(function (parser) {
        var result_list = parser.getDocumentList(true, id);
        if (result_list.length) {
          return result_list[0].doc;
        }
        throw new jIO.util.jIOError(
          "Cannot find parsed document: " + id,
          404
        );
      });
  };

  jIO.addStorage('parser', ParserStorage);

}(jIO, DOMParser));