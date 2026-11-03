(function (window, rJS) {
  rJS(window)
    .onStateChange(function (modification_dict) {
      if (modification_dict.hasOwnProperty('helptext')) {
        var x = this.element.getElementsByTagName("P")[0];
        x.innerText = modification_dict.helptext.trim();
      }
    })
    .onEvent('click', function (evt) {
      var x = this.element.getElementsByTagName("P")[0];
      if (x.style.display === "none") {
        x.style.display = "block";
      } else {
        x.style.display = "none";
      }
    }, false, false);
}(window, rJS));

