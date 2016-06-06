<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="File" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_Cacheable__manager_id</string> </key>
            <value> <string>http_cache</string> </value>
        </item>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts21897119.52</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>html-hint.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

// CodeMirror, copyright (c) by Marijn Haverbeke and others\n
// Distributed under an MIT license: http://codemirror.net/LICENSE\n
\n
(function(mod) {\n
  if (typeof exports == "object" && typeof module == "object") // CommonJS\n
    mod(require("../../lib/codemirror"), require("./xml-hint"));\n
  else if (typeof define == "function" && define.amd) // AMD\n
    define(["../../lib/codemirror", "./xml-hint"], mod);\n
  else // Plain browser env\n
    mod(CodeMirror);\n
})(function(CodeMirror) {\n
  "use strict";\n
\n
  var langs = "ab aa af ak sq am ar an hy as av ae ay az bm ba eu be bn bh bi bs br bg my ca ch ce ny zh cv kw co cr hr cs da dv nl dz en eo et ee fo fj fi fr ff gl ka de el gn gu ht ha he hz hi ho hu ia id ie ga ig ik io is it iu ja jv kl kn kr ks kk km ki rw ky kv kg ko ku kj la lb lg li ln lo lt lu lv gv mk mg ms ml mt mi mr mh mn na nv nb nd ne ng nn no ii nr oc oj cu om or os pa pi fa pl ps pt qu rm rn ro ru sa sc sd se sm sg sr gd sn si sk sl so st es su sw ss sv ta te tg th ti bo tk tl tn to tr ts tt tw ty ug uk ur uz ve vi vo wa cy wo fy xh yi yo za zu".split(" ");\n
  var targets = ["_blank", "_self", "_top", "_parent"];\n
  var charsets = ["ascii", "utf-8", "utf-16", "latin1", "latin1"];\n
  var methods = ["get", "post", "put", "delete"];\n
  var encs = ["application/x-www-form-urlencoded", "multipart/form-data", "text/plain"];\n
  var media = ["all", "screen", "print", "embossed", "braille", "handheld", "print", "projection", "screen", "tty", "tv", "speech",\n
               "3d-glasses", "resolution [>][<][=] [X]", "device-aspect-ratio: X/Y", "orientation:portrait",\n
               "orientation:landscape", "device-height: [X]", "device-width: [X]"];\n
  var s = { attrs: {} }; // Simple tag, reused for a whole lot of tags\n
\n
  var data = {\n
    a: {\n
      attrs: {\n
        href: null, ping: null, type: null,\n
        media: media,\n
        target: targets,\n
        hreflang: langs\n
      }\n
    },\n
    abbr: s,\n
    acronym: s,\n
    address: s,\n
    applet: s,\n
    area: {\n
      attrs: {\n
        alt: null, coords: null, href: null, target: null, ping: null,\n
        media: media, hreflang: langs, type: null,\n
        shape: ["default", "rect", "circle", "poly"]\n
      }\n
    },\n
    article: s,\n
    aside: s,\n
    audio: {\n
      attrs: {\n
        src: null, mediagroup: null,\n
        crossorigin: ["anonymous", "use-credentials"],\n
        preload: ["none", "metadata", "auto"],\n
        autoplay: ["", "autoplay"],\n
        loop: ["", "loop"],\n
        controls: ["", "controls"]\n
      }\n
    },\n
    b: s,\n
    base: { attrs: { href: null, target: targets } },\n
    basefont: s,\n
    bdi: s,\n
    bdo: s,\n
    big: s,\n
    blockquote: { attrs: { cite: null } },\n
    body: s,\n
    br: s,\n
    button: {\n
      attrs: {\n
        form: null, formaction: null, name: null, value: null,\n
        autofocus: ["", "autofocus"],\n
        disabled: ["", "autofocus"],\n
        formenctype: encs,\n
        formmethod: methods,\n
        formnovalidate: ["", "novalidate"],\n
        formtarget: targets,\n
        type: ["submit", "reset", "button"]\n
      }\n
    },\n
    canvas: { attrs: { width: null, height: null } },\n
    caption: s,\n
    center: s,\n
    cite: s,\n
    code: s,\n
    col: { attrs: { span: null } },\n
    colgroup: { attrs: { span: null } },\n
    command: {\n
      attrs: {\n
        type: ["command", "checkbox", "radio"],\n
        label: null, icon: null, radiogroup: null, command: null, title: null,\n
        disabled: ["", "disabled"],\n
        checked: ["", "checked"]\n
      }\n
    },\n
    data: { attrs: { value: null } },\n
    datagrid: { attrs: { disabled: ["", "disabled"], multiple: ["", "multiple"] } },\n
    datalist: { attrs: { data: null } },\n
    dd: s,\n
    del: { attrs: { cite: null, datetime: null } },\n
    details: { attrs: { open: ["", "open"] } },\n
    dfn: s,\n
    dir: s,\n
    div: s,\n
    dl: s,\n
    dt: s,\n
    em: s,\n
    embed: { attrs: { src: null, type: null, width: null, height: null } },\n
    eventsource: { attrs: { src: null } },\n
    fieldset: { attrs: { disabled: ["", "disabled"], form: null, name: null } },\n
    figcaption: s,\n
    figure: s,\n
    font: s,\n
    footer: s,\n
    form: {\n
      attrs: {\n
        action: null, name: null,\n
        "accept-charset": charsets,\n
        autocomplete: ["on", "off"],\n
        enctype: encs,\n
        method: methods,\n
        novalidate: ["", "novalidate"],\n
        target: targets\n
      }\n
    },\n
    frame: s,\n
    frameset: s,\n
    h1: s, h2: s, h3: s, h4: s, h5: s, h6: s,\n
    head: {\n
      attrs: {},\n
      children: ["title", "base", "link", "style", "meta", "script", "noscript", "command"]\n
    },\n
    header: s,\n
    hgroup: s,\n
    hr: s,\n
    html: {\n
      attrs: { manifest: null },\n
      children: ["head", "body"]\n
    },\n
    i: s,\n
    iframe: {\n
      attrs: {\n
        src: null, srcdoc: null, name: null, width: null, height: null,\n
        sandbox: ["allow-top-navigation", "allow-same-origin", "allow-forms", "allow-scripts"],\n
        seamless: ["", "seamless"]\n
      }\n
    },\n
    img: {\n
      attrs: {\n
        alt: null, src: null, ismap: null, usemap: null, width: null, height: null,\n
        crossorigin: ["anonymous", "use-credentials"]\n
      }\n
    },\n
    input: {\n
      attrs: {\n
        alt: null, dirname: null, form: null, formaction: null,\n
        height: null, list: null, max: null, maxlength: null, min: null,\n
        name: null, pattern: null, placeholder: null, size: null, src: null,\n
        step: null, value: null, width: null,\n
        accept: ["audio/*", "video/*", "image/*"],\n
        autocomplete: ["on", "off"],\n
        autofocus: ["", "autofocus"],\n
        checked: ["", "checked"],\n
        disabled: ["", "disabled"],\n
        formenctype: encs,\n
        formmethod: methods,\n
        formnovalidate: ["", "novalidate"],\n
        formtarget: targets,\n
        multiple: ["", "multiple"],\n
        readonly: ["", "readonly"],\n
        required: ["", "required"],\n
        type: ["hidden", "text", "search", "tel", "url", "email", "password", "datetime", "date", "month",\n
               "week", "time", "datetime-local", "number", "range", "color", "checkbox", "radio",\n
               "file", "submit", "image", "reset", "button"]\n
      }\n
    },\n
    ins: { attrs: { cite: null, datetime: null } },\n
    kbd: s,\n
    keygen: {\n
      attrs: {\n
        challenge: null, form: null, name: null,\n
        autofocus: ["", "autofocus"],\n
        disabled: ["", "disabled"],\n
        keytype: ["RSA"]\n
      }\n
    },\n
    label: { attrs: { "for": null, form: null } },\n
    legend: s,\n
    li: { attrs: { value: null } },\n
    link: {\n
      attrs: {\n
        href: null, type: null,\n
        hreflang: langs,\n
        media: media,\n
        sizes: ["all", "16x16", "16x16 32x32", "16x16 32x32 64x64"]\n
      }\n
    },\n
    map: { attrs: { name: null } },\n
    mark: s,\n
    menu: { attrs: { label: null, type: ["list", "context", "toolbar"] } },\n
    meta: {\n
      attrs: {\n
        content: null,\n
        charset: charsets,\n
        name: ["viewport", "application-name", "author", "description", "generator", "keywords"],\n
        "http-equiv": ["content-language", "content-type", "default-style", "refresh"]\n
      }\n
    },\n
    meter: { attrs: { value: null, min: null, low: null, high: null, max: null, optimum: null } },\n
    nav: s,\n
    noframes: s,\n
    noscript: s,\n
    object: {\n
      attrs: {\n
        data: null, type: null, name: null, usemap: null, form: null, width: null, height: null,\n
        typemustmatch: ["", "typemustmatch"]\n
      }\n
    },\n
    ol: { attrs: { reversed: ["", "reversed"], start: null, type: ["1", "a", "A", "i", "I"] } },\n
    optgroup: { attrs: { disabled: ["", "disabled"], label: null } },\n
    option: { attrs: { disabled: ["", "disabled"], label: null, selected: ["", "selected"], value: null } },\n
    output: { attrs: { "for": null, form: null, name: null } },\n
    p: s,\n
    param: { attrs: { name: null, value: null } },\n
    pre: s,\n
    progress: { attrs: { value: null, max: null } },\n
    q: { attrs: { cite: null } },\n
    rp: s,\n
    rt: s,\n
    ruby: s,\n
    s: s,\n
    samp: s,\n
    script: {\n
      attrs: {\n
        type: ["text/javascript"],\n
        src: null,\n
        async: ["", "async"],\n
        defer: ["", "defer"],\n
        charset: charsets\n
      }\n
    },\n
    section: s,\n
    select: {\n
      attrs: {\n
        form: null, name: null, size: null,\n
        autofocus: ["", "autofocus"],\n
        disabled: ["", "disabled"],\n
        multiple: ["", "multiple"]\n
      }\n
    },\n
    small: s,\n
    source: { attrs: { src: null, type: null, media: null } },\n
    span: s,\n
    strike: s,\n
    strong: s,\n
    style: {\n
      attrs: {\n
        type: ["text/css"],\n
        media: media,\n
        scoped: null\n
      }\n
    },\n
    sub: s,\n
    summary: s,\n
    sup: s,\n
    table: s,\n
    tbody: s,\n
    td: { attrs: { colspan: null, rowspan: null, headers: null } },\n
    textarea: {\n
      attrs: {\n
        dirname: null, form: null, maxlength: null, name: null, placeholder: null,\n
        rows: null, cols: null,\n
        autofocus: ["", "autofocus"],\n
        disabled: ["", "disabled"],\n
        readonly: ["", "readonly"],\n
        required: ["", "required"],\n
        wrap: ["soft", "hard"]\n
      }\n
    },\n
    tfoot: s,\n
    th: { attrs: { colspan: null, rowspan: null, headers: null, scope: ["row", "col", "rowgroup", "colgroup"] } },\n
    thead: s,\n
    time: { attrs: { datetime: null } },\n
    title: s,\n
    tr: s,\n
    track: {\n
      attrs: {\n
        src: null, label: null, "default": null,\n
        kind: ["subtitles", "captions", "descriptions", "chapters", "metadata"],\n
        srclang: langs\n
      }\n
    },\n
    tt: s,\n
    u: s,\n
    ul: s,\n
    "var": s,\n
    video: {\n
      attrs: {\n
        src: null, poster: null, width: null, height: null,\n
        crossorigin: ["anonymous", "use-credentials"],\n
        preload: ["auto", "metadata", "none"],\n
        autoplay: ["", "autoplay"],\n
        mediagroup: ["movie"],\n
        muted: ["", "muted"],\n
        controls: ["", "controls"]\n
      }\n
    },\n
    wbr: s\n
  };\n
\n
  var globalAttrs = {\n
    accesskey: ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],\n
    "class": null,\n
    contenteditable: ["true", "false"],\n
    contextmenu: null,\n
    dir: ["ltr", "rtl", "auto"],\n
    draggable: ["true", "false", "auto"],\n
    dropzone: ["copy", "move", "link", "string:", "file:"],\n
    hidden: ["hidden"],\n
    id: null,\n
    inert: ["inert"],\n
    itemid: null,\n
    itemprop: null,\n
    itemref: null,\n
    itemscope: ["itemscope"],\n
    itemtype: null,\n
    lang: ["en", "es"],\n
    spellcheck: ["true", "false"],\n
    style: null,\n
    tabindex: ["1", "2", "3", "4", "5", "6", "7", "8", "9"],\n
    title: null,\n
    translate: ["yes", "no"],\n
    onclick: null,\n
    rel: ["stylesheet", "alternate", "author", "bookmark", "help", "license", "next", "nofollow", "noreferrer", "prefetch", "prev", "search", "tag"]\n
  };\n
  function populate(obj) {\n
    for (var attr in globalAttrs) if (globalAttrs.hasOwnProperty(attr))\n
      obj.attrs[attr] = globalAttrs[attr];\n
  }\n
\n
  populate(s);\n
  for (var tag in data) if (data.hasOwnProperty(tag) && data[tag] != s)\n
    populate(data[tag]);\n
\n
  CodeMirror.htmlSchema = data;\n
  function htmlHint(cm, options) {\n
    var local = {schemaInfo: data};\n
    if (options) for (var opt in options) local[opt] = options[opt];\n
    return CodeMirror.hint.xml(cm, local);\n
  }\n
  CodeMirror.registerHelper("hint", "html", htmlHint);\n
});\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>11341</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
