"""
================================================================================
Return common parameter across all templates
================================================================================
"""

if parameter == "fallback_image":
  return "common_images/fallback.png"

if parameter == "default_theme_css_url":
  return "default_themes/themes.css"

if parameter == "wkhtmltopdf_rendering_fix":
  return 
  """
  <script>
  (function () {
    var table_list = document.body.querySelectorAll("table"),
      sheet_width_in_px,
      div;

    if (table_list.length > 0) {
      // measure what is the px equivalent for 210mm (A4 210x297mm)
      div = document.createElement("div")
      div.style.width = "200mm";  // XXX HARDCODED
      document.body.appendChild(div);
      sheet_width_in_px = div.clientWidth;
      document.body.removeChild(div);

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
  }());
  </script>
  """
