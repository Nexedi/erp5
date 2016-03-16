var friendWindows = [];
var idx = 1;
var slides;

/* main() */

window.onload = function() {
  slides = document.querySelectorAll("body > section");
  onhashchange();
  setSlide();
  document.body.className = "loaded";
  onresize();
}

/* Handle keys */

window.onkeydown = function(e) {
  // Don't intercept keyboard shortcuts
  if (e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) {
    return;
  }
  if ( e.keyCode == 37 // left arrow
    || e.keyCode == 33 // page up
  ) {
    e.preventDefault();
    back();
  }
  if ( e.keyCode == 39 // right arrow
    || e.keyCode == 34 // page down
  ) {
    e.preventDefault();
    forward();
  }

  if ( e.keyCode == 32) { // space
      e.preventDefault();
      toggleContent();
  }
}

/* Adapt the size of the slides to the window */

window.onresize = function() {
  var sx = document.body.clientWidth / window.innerWidth;
  var sy = document.body.clientHeight / window.innerHeight;
  var transform = "scale(" + (1/Math.max(sx, sy)) + ")";
  document.body.style.MozTransform = transform;
  document.body.style.WebkitTransform = transform;
  document.body.style.OTransform = transform;
  document.body.style.msTransform = transform;
  document.body.style.transform = transform;
}
function getDetails(idx) {
  var s = document.querySelector("section:nth-of-type("+ idx +")");
  var d = s.querySelector("details");
  return d?d.innerHTML:"";
}
window.onmessage = function(e) {
  msg = e.data;
  win = e.source;
  if (msg === "register") {
    friendWindows.push(win);
    win.postMessage(JSON.stringify({method: "registered", title: document.title, count: slides.length}), document.location);
    win.postMessage(JSON.stringify({method: "newslide", details: getDetails(idx), idx: idx}), document.location);
    return;
  }
  if (msg === "back") back();
  if (msg === "forward") forward();
  if (msg === "toggleContent") toggleContent();
  // setSlide(42)
  var r = /setSlide\((\d+)\)/.exec(msg);
  if (r) {
      idx = r[1];
      setSlide();
  }
}

/* If a Video is present in this new slide, play it.
    If a Video is present in the previous slide, stop it. */

function toggleContent() {
  var s = document.querySelector("section[aria-selected]");
  if (s) {
      var video = s.querySelector("video");
      if (video) {
          if (video.ended || video.paused) {
              video.play();
          } else {
              video.pause();
          }
      }
  }
}

/* If the user change the slide number in the URL bar, jump
    to this slide. */

window.onhashchange = function(e) {
  var newidx = ~~window.location.hash.split("#")[1];
  if (!newidx) newidx = 1;
  if (newidx == idx) return;
  idx = newidx;
  setSlide();
}

/* Slide controls */

function back() {
  if (idx == 1) return;
  idx--;
  setSlide();
}
function forward() {
  if (idx >= slides.length) return;
  idx++;
  setSlide();
}
function setSlide() {
  var old = document.querySelector("section[aria-selected]");
  var next = document.querySelector("section:nth-of-type("+ idx +")");
  if (old) {
    old.removeAttribute("aria-selected");
    var video = old.querySelector("video");
    if (video) { video.pause(); }
  }
  if (next) {
    next.setAttribute("aria-selected", "true");
    var video = next.querySelector("video");
    if (video) { video.play(); }
  } else {
    console.warn("No such slide: " + idx);
    idx = 0;
    for (var i = 0; i < slides.length; i++) {
        if (slides[i].hasAttribute("aria-selected")) {
            idx = i + 1;
        }
    }
  }
  window.location.hash = idx;
  for (var i = 0; i < friendWindows.length; i++) {
      friendWindows[i].postMessage(JSON.stringify({method: "newslide", details: getDetails(idx), idx: idx}), document.location);
  }
}
