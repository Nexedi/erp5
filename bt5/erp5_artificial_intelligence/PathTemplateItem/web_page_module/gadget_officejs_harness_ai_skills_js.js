/*global window */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window) {
  "use strict";

  var CREATE_HTML_REPORT_INSTRUCTIONS = "# Guide: Writing HTML Report Content\n\n" +
    "Follow these conventions when writing HTML content for a report that will be rendered as a " +
    "formatted, paginated document (table of contents, numbered figures/tables, page breaks).\n\n" +
    "Do not add CSS: no `<style>` blocks, no `style=\"...\"` attributes, and no classes added purely " +
    "for visual styling. Write plain, semantic HTML only.\n\n" +
    "Do not write `<html>`, `<head>` or `<body>` tags - only the content that would go inside " +
    "`<body>` is needed (headings, paragraphs, images, tables, etc.).\n\n" +
    "## 1. Headings and Table of Contents\n\n" +
    "Use plain `<h1>` through `<h6>` - no `id`/`class` needed. The heading's text must be a plain " +
    "text node (no nested `<span>` etc. inside it), since a table-of-contents builder typically reads " +
    "it literally between `>` and `<`. Nesting (h1 > h2 > h3...) is inferred purely from tag depth.\n\n" +
    "A top-level `<h1>` heading commonly starts a new page and is the primary chapter-break " +
    "mechanism - do not insert a table of contents yourself; it is generated automatically from your " +
    "headings.\n\n" +
    "## 2. Images\n\n" +
    "Reference images by a relative path, not an absolute `http(s)://` URL or a `data:` URI. Always " +
    "add an explicit `alt=\"...\"` attribute: besides accessibility, it is commonly used as the " +
    "figure's caption text, and an image with no `alt` can be silently dropped from a generated " +
    "figures list.\n\n" +
    "```html\n" +
    "<img src=\"images/example.png\" alt=\"Caption for this figure\" />\n" +
    "```\n\n" +
    "## 3. Tables\n\n" +
    "Add a `<caption>...</caption>` inside the `<table>` (as the last child, after `<tbody>`) to have " +
    "the table numbered and listed in a generated tables overview. A table with no `<caption>` still " +
    "renders normally, it just isn't tracked/numbered.\n\n" +
    "```html\n" +
    "<table>\n" +
    "  <thead><tr><th>Column A</th><th>Column B</th></tr></thead>\n" +
    "  <tbody><tr><td>value 1</td><td>value 2</td></tr></tbody>\n" +
    "  <caption>Example table description</caption>\n" +
    "</table>\n" +
    "```\n\n" +
    "## 4. Page breaks\n\n" +
    "- A top-level heading forces a new page (see above).\n" +
    "- Do not use the `<section>` tag.\n" +
    "- Tables, images and `<pre><code>` blocks are kept on a single page (never split across a page " +
    "boundary).";

  var SKILL_LIST = [
    {
      name: "create_html_report",
      instructions: CREATE_HTML_REPORT_INSTRUCTIONS
    }
  ];

  window.ChatSkills = {
    SKILL_LIST: SKILL_LIST
  };
}(window));
