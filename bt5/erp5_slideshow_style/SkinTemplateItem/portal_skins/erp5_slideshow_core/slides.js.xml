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
            <value> <string>ts22818918.05</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>slides.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

var friendWindows = [];\n
var idx = 1;\n
var slides;\n
\n
/* main() */\n
\n
window.onload = function() {\n
  slides = document.querySelectorAll("body > section");\n
  onhashchange();\n
  setSlide();\n
  document.body.className = "loaded";\n
  onresize();\n
}\n
\n
/* Handle keys */\n
\n
window.onkeydown = function(e) {\n
  // Don\'t intercept keyboard shortcuts\n
  if (e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) {\n
    return;\n
  }\n
  if ( e.keyCode == 37 // left arrow\n
    || e.keyCode == 33 // page up\n
  ) {\n
    e.preventDefault();\n
    back();\n
  }\n
  if ( e.keyCode == 39 // right arrow\n
    || e.keyCode == 34 // page down\n
  ) {\n
    e.preventDefault();\n
    forward();\n
  }\n
\n
  if ( e.keyCode == 32) { // space\n
      e.preventDefault();\n
      toggleContent();\n
  }\n
}\n
\n
/* Adapt the size of the slides to the window */\n
\n
window.onresize = function() {\n
  var sx = document.body.clientWidth / window.innerWidth;\n
  var sy = document.body.clientHeight / window.innerHeight;\n
  var transform = "scale(" + (1/Math.max(sx, sy)) + ")";\n
  document.body.style.MozTransform = transform;\n
  document.body.style.WebkitTransform = transform;\n
  document.body.style.OTransform = transform;\n
  document.body.style.msTransform = transform;\n
  document.body.style.transform = transform;\n
}\n
function getDetails(idx) {\n
  var s = document.querySelector("section:nth-of-type("+ idx +")");\n
  var d = s.querySelector("details");\n
  return d?d.innerHTML:"";\n
}\n
window.onmessage = function(e) {\n
  msg = e.data;\n
  win = e.source;\n
  if (msg === "register") {\n
    friendWindows.push(win);\n
    win.postMessage(JSON.stringify({method: "registered", title: document.title, count: slides.length}), document.location);\n
    win.postMessage(JSON.stringify({method: "newslide", details: getDetails(idx), idx: idx}), document.location);\n
    return;\n
  }\n
  if (msg === "back") back();\n
  if (msg === "forward") forward();\n
  if (msg === "toggleContent") toggleContent();\n
  // setSlide(42)\n
  var r = /setSlide\\((\\d+)\\)/.exec(msg);\n
  if (r) {\n
      idx = r[1];\n
      setSlide();\n
  }\n
}\n
\n
/* If a Video is present in this new slide, play it.\n
    If a Video is present in the previous slide, stop it. */\n
\n
function toggleContent() {\n
  var s = document.querySelector("section[aria-selected]");\n
  if (s) {\n
      var video = s.querySelector("video");\n
      if (video) {\n
          if (video.ended || video.paused) {\n
              video.play();\n
          } else {\n
              video.pause();\n
          }\n
      }\n
  }\n
}\n
\n
/* If the user change the slide number in the URL bar, jump\n
    to this slide. */\n
\n
window.onhashchange = function(e) {\n
  var newidx = ~~window.location.hash.split("#")[1];\n
  if (!newidx) newidx = 1;\n
  if (newidx == idx) return;\n
  idx = newidx;\n
  setSlide();\n
}\n
\n
/* Slide controls */\n
\n
function back() {\n
  if (idx == 1) return;\n
  idx--;\n
  setSlide();\n
}\n
function forward() {\n
  if (idx >= slides.length) return;\n
  idx++;\n
  setSlide();\n
}\n
function setSlide() {\n
  var old = document.querySelector("section[aria-selected]");\n
  var next = document.querySelector("section:nth-of-type("+ idx +")");\n
  if (old) {\n
    old.removeAttribute("aria-selected");\n
    var video = old.querySelector("video");\n
    if (video) { video.pause(); }\n
  }\n
  if (next) {\n
    next.setAttribute("aria-selected", "true");\n
    var video = next.querySelector("video");\n
    if (video) { video.play(); }\n
  } else {\n
    console.warn("No such slide: " + idx);\n
    idx = 0;\n
    for (var i = 0; i < slides.length; i++) {\n
        if (slides[i].hasAttribute("aria-selected")) {\n
            idx = i + 1;\n
        }\n
    }\n
  }\n
  window.location.hash = idx;\n
  for (var i = 0; i < friendWindows.length; i++) {\n
      friendWindows[i].postMessage(JSON.stringify({method: "newslide", details: getDetails(idx), idx: idx}), document.location);\n
  }\n
}\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>3714</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>slides.js</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
