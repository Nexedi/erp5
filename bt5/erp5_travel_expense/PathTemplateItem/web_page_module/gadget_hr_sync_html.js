<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>OfficeJS Sync Page</title>

    <script src="rsvp.js"></script>
    <script src="renderjs.js"></script>
    <script src="handlebars.js"></script>
    <script src="gadget_global.js" ></script>

    <script id="page-template" type="text/x-handlebars-template">
      <article class="ui-content ui-body-c">
        <section class="ui-content-header-plain">
          <h3 class="ui-content-title ui-body-c">
            <span class="ui-icon ui-icon-custom ui-icon-refresh">&nbsp;</span>
            Synchronize your data
          </h3>
        </section>
        <section class="ui-body-c ui-content-section">
          <div class="ui-controlgroup ui-controlgroup-horizontal">
            <div class="ui-grid-b ui-responsive">
              <div class="ui-block-a"></div>
              <div class="ui-block-b">
                <form class="synchro-form view-web-page-form">
                  <button type="submit" data-i18n="Launch Synchronization" data-theme="b">Launch Synchronization</button>
                </form>
              </div>
              <div class="ui-block-c"></div>
            </div>
          </div>
        </section>
      </article>
    </script>

    <script src="gadget_officejs_page_sync.js"></script>

  </head>

  <body>
  </body>
</html>