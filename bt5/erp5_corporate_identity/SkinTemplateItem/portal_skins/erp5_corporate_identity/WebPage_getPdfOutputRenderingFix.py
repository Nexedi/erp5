"""
================================================================================
Scripts correcting wrong behaviors in WkHTMLtoPDF rendering
================================================================================
"""
# parameters:
# ------------------------------------------------------------------------------
# parameter                          Parameter to lookup

# included:
# - prevent resizing of document and font-size based on width of widest element

return """
  <script>
  (function () {
    var table_list = document.body.querySelectorAll("table"),
      blockquote_list = document.body.querySelectorAll("table"),
      gantt_list = document.body.querySelectorAll(".gantt_container"),
      sheet_width_in_px,
      div;

    // always measure what is the px equivalent for 210mm (A4 210x297mm)
    div = document.createElement("div")
    div.style.width = "200mm";  // XXX HARDCODED
    document.body.appendChild(div);
    sheet_width_in_px = div.clientWidth;
    document.body.removeChild(div);
    console.log(table_list)
    if (table_list.length > 0) {

      // Resize a table by reducing th and td font-size,
      // to avoid the table to be larger than the sheet width,
      // to avoid global fonts to be reduced.
      [].forEach.call(table_list, function (table) {
        if (sheet_width_in_px > table.clientWidth) return;
        var ratio_percent = Math.floor((sheet_width_in_px / table.clientWidth) * 100);
        table.style.width = "100%";

        // Select th and td and affect the font-size in percent.
        // The CSS should not set the font-size on the table instead of th and td
        [].forEach.call(table.querySelectorAll("td"), function (e) {
          e.setAttribute("style", "font-size: " + ratio_percent + "%");
        });
        [].forEach.call(table.querySelectorAll("th"), function (e) {
          e.setAttribute("style", "font-size: " + ratio_percent + "%");
        });
      });
    }
    if (gantt_list.length > 0) {
      [].forEach.call(gantt_list, function (gantt) {
        if (sheet_width_in_px > gantt.clientWidth) return;
        var ratio_percent = Math.floor((sheet_width_in_px / gantt.clientWidth) * 100);
        gantt.style.width = "100%";

        [].forEach.call(gantt.children, function (e) {
          e.setAttribute("style", "font-size: " + ratio_percent + "%");
        });
      });
    }

    // same for other elements
    if (blockquote_list.length > 0) {
      [].forEach.call(blockquote_list, function (blockquote) {
        if (sheet_width_in_px > blockquote.clientWidth) return;
        var ratio_percent = Math.floor((sheet_width_in_px / blockquote.clientWidth) * 100);
        blockquote.style.width = "100%";

        [].forEach.call(blockquote.children, function (e) {
          e.setAttribute("style", "font-size: " + ratio_percent + "%");
        });
      });
    }
  }());
  </script>
  """
